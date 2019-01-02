from flask import *
from flask_socketio import SocketIO, join_room, leave_room, emit, send
from database import Database
from imagestore import ImageStore
import jwt
import settings

import time
from threading import Timer

#enum of states
class GameState:
    STARTING = 0 # Waiting for players to join the game
    DRAWING = 1 # Creating panels
    DISTRIBUTING = 2 # Internal state: finishing up image upload from clients, randomising the panels and distributing them to players
    CREATING = 3 # players are making strips
    GATHERING = 4 # Internal state: finishing upload of any created strips
    RATING = 5 # Quick fire rating strips off against eachother
    SCOREBOARD = 6 # Game is over, display scoreboard. The game remains in this state forevermore

DRAW_TIME = 60 * 3.5
GRACE_PERIOD = 10
CREATE_TIME = 60 * 3.5

app = Flask(__name__)

db = Database();
imagestore = ImageStore();

@app.route('/', methods = ['GET'])
def index():
    res = make_response(render_template('index.html'));

    request_data = parse_request_data();

    res.set_cookie("cg_data", jwt.encode(request_data, settings.JWT_KEY, algorithm='HS256'), 60 * 60 * 24 * 365);
    return res;

@app.route('/game', methods = ['GET'])
def game():
    res = make_response(render_template('game.html'));

    request_data = parse_request_data();

    res.set_cookie("cg_data", jwt.encode(request_data, settings.JWT_KEY, algorithm='HS256'), 60 * 60 * 24 * 365);
    return res;

@app.route('/image/<image_id>', methods = ['GET'])
def get_image(image_id):
    if imagestore.has_image(image_id):
        res = make_response(imagestore.get_image(image_id));
        res.headers.set("content-type", "image/png");
    else:
        res = make_response(jsonify({"error": "Image not found"}));
        res.status_code = 404;

    return res;

@app.route('/api/game', methods = ["POST"])
def create_game():
    # TODO:
    # If this user is already hosting a game, cancel it and notify players
    request_data = parse_request_data();

    # Add a new game record setting this user as the host
    res = make_response(jsonify({"game_id": db.create_game(request_data["user_id"])}));

    res.set_cookie("cg_data", jwt.encode(request_data, settings.JWT_KEY, algorithm='HS256'), 60 * 60 * 24 * 365);

    return res

# Get game info, initial large data dump when loading a page. This is updated incrementally using web scokets
@app.route("/api/game/<game_id>", methods = ["GET"])
def get_game_info(game_id):
    game_id = game_id.lower();
    request_data = parse_request_data();

    record = db.query_game_for_user(game_id, request_data["user_id"]);

    if record != None:
        res = make_response(jsonify(record));
    else:
        res = make_response(jsonify({"error":"Game not found"}));
        res.status_code = 404;

    res.set_cookie("cg_data", jwt.encode(request_data, settings.JWT_KEY, algorithm='HS256'), 60 * 60 * 24 * 365);

    return res

@app.route('/api/game/<game_id>/start', methods = ["POST"])
def start_game(game_id):
    # TODO:
    # If the user is not hoting a game
    # If the game is in the STARTING state move onto DRAWNING and broadcast notify
    request_data = parse_request_data();

    record = db.query_game_for_user(game_id, request_data["user_id"]);

    if record is None or not record["is_host"]:
        res = make_response(jsonify({"success": False}));
        res.status = 400;
    else:
        end_time = int(time.time() + DRAW_TIME);

        if record["state"] == GameState.STARTING:
            record["state"] = GameState.DRAWING;
            db.set_game_state(game_id, record["state"], end_time);
            t = Timer(DRAW_TIME, draw_time_compete, [game_id]);
            t.start();

        res = make_response(jsonify({"success": True, "game_id": game_id, "state": record["state"], "end_time": end_time}));
        emit('update', {'state': record["state"], 'round_end': end_time}, room=game_id, namespace='/');

    res.set_cookie("cg_data", jwt.encode(request_data, settings.JWT_KEY, algorithm='HS256'), 60 * 60 * 24 * 365);

    return res

def draw_time_compete(game_id):
    with app.app_context():
        db.set_game_state(game_id, GameState.DISTRIBUTING, 0);
        emit('update', {'state': GameState.DISTRIBUTING}, room=game_id, namespace='/');

        t = Timer(GRACE_PERIOD, start_create_state, [game_id]);
        t.start();

def start_create_state(game_id):
    with app.app_context():
        end_time = int(time.time() + CREATE_TIME);

        db.set_game_state(game_id, GameState.CREATING, end_time);
        emit('update', {'state': GameState.CREATING, "round_end": end_time}, room=game_id, namespace='/');

        t = Timer(CREATE_TIME, create_time_compete, [game_id]);
        t.start();

def create_time_compete(game_id):
    with app.app_context():
        db.set_game_state(game_id, GameState.GATHERING, 0);
        emit('update', {'state': GameState.GATHERING}, room=game_id, namespace='/');

@app.route('/api/game/<game_id>/join', methods = ["POST"])
def join_game(game_id):
    game_id = game_id.lower();
    request_data = parse_request_data();

    if "name" not in request.form:
        res = make_response(jsonify({"error": "Player name is required"}));
        res.status = 400;
        return res;

    if db.add_user_to_game(game_id, request_data["user_id"], request.form["name"]):
        res = make_response(jsonify({"success":True, "game_id": game_id}));

        emit('new_player', {'id': request_data["user_id"], 'name': request.form["name"], 'score': 0}, room=game_id, namespace='/');
    else:
        res = make_response(jsonify({"error":"Game not found"}));
        res.status_code = 404;

    res.set_cookie("cg_data", jwt.encode(request_data, settings.JWT_KEY, algorithm='HS256'), 60 * 60 * 24 * 365);

    return res

@app.route('/api/game/<game_id>/panels', methods = ["POST"])
def add_panel(game_id):
    game_id = game_id.lower();
    request_data = parse_request_data();

    image_id = db.add_panel_to_game(game_id, request_data["user_id"]);

    if image_id is not None:
        parts = request.data.split(',', 1);
        b64String = parts[len(parts)-1];

        imagestore.store_image(image_id, b64String);
        res = make_response(jsonify({"success":True, "game_id": game_id}));
    else:
        res = make_response(jsonify({"error":"Game not found"}));
        res.status_code = 404;

    return res

def parse_request_data():
    data = {};

    if "cg_data" in request.cookies:
        try:
            data = jwt.decode(request.cookies["cg_data"], settings.JWT_KEY, algorithms='HS256');
        except:
            data = {};

    if not "user_id" in data:
        # user ID
        data["user_id"] = db.create_user(request.remote_addr);

    return data;

socketio = SocketIO(app)

@socketio.on('connect', namespace='/')
def test_connect():
    print('Client connected')
    emit('my response', {'data': 'Connected'})

@socketio.on('disconnect', namespace='/')
def test_disconnect():
    print('Client disconnected')

@socketio.on('subscribe')
def on_join(data):
    room = data['game_id']
    join_room(room)
    print("New subscriber for game " + room);

@socketio.on('unsubscribe')
def on_leave(data):
    room = data['game_id']
    leave_room(room)
    print("Subscriber gone for game " + room);

if __name__ == "__main__":
    print("Starting server...");
    socketio.run(app, host="0.0.0.0")
