print("Initialising comic game API server...");

from flask import *
from flask_socketio import SocketIO, join_room, leave_room, emit, send
from database import *
from imagestore import *
import jwt
import settings
from PIL import Image
import base64
import cStringIO
import io

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

GAME_USER = "COMICGAME";

app = Flask(__name__)

db = get_database(settings.DATABASE_TYPE);
imagestore = get_image_store(settings.IMAGE_STORE_TYPE);

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
    if db.image_exists(image_id):
        data = imagestore.get_image(image_id)
        res = make_response(data);
        if data is None:
            res.status = 500;
        res.headers.set("content-type", "image/png");
    else:
        res = make_response(jsonify({"error": "Image not found"}));
        res.status_code = 404;

    return res;


# Get the panels assigned to this user
@app.route('/api/game/<game_id>/assignments', methods = ["GET"])
def get_assignments(game_id):
    request_data = parse_request_data();

    assignments = db.get_assignments_for(game_id, request_data["user_id"]);

    if assignments is None:
        res =  make_response(jsonify({"error": "No assignments found"}));
        res.status = 404;
        return res;

    return make_response(jsonify({"assignments": assignments}));

def make_comic(comic):
    combined = Image.open('template.png');

    for i in range(0, 3):
        data = imagestore.get_image(comic[i]);

        if data is None:
            continue;

        im = Image.open(io.BytesIO(data));
        combined.paste(im, ((i*1150) + 60,60));

    buffer = cStringIO.StringIO()
    combined.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue());

# Get the panels assigned to this user
@app.route('/api/game/<game_id>/comics', methods = ["POST"])
def post_comic(game_id):
    if request.json is None or "comic" not in request.json:
        res = make_response({"error": "Invalid parameters: Parameter must be a valid JSON object"});
        res.status = 400;
        return res;

    request_data = parse_request_data();

    # Find all three images for this comic and combine them server-side
    comic = request.json["comic"];
    data = make_comic(comic);

    iid = db.add_comic_to_game(game_id, request_data["user_id"], comic);
    imagestore.store_image(iid, data);

    return jsonify({"success": True, "image_id": iid});



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
        # Distribute images to the players
        record = db.query_game_for_user(game_id, "");
        panels = db.get_panels_in_game(game_id);

        players = record["players"];
        num_players = len(players);
        player_idx = 0;

        assignments = {};
        for i in range(0, num_players):
            assignments[players[i]["id"]] = [];

        for i in range(0, len(panels)):
            # Don't assign a panel to the player which created it
            if(panels[i]["created_by"] == players[player_idx]["id"]):
                player_idx = player_idx + 1;
                if player_idx >= num_players:
                    player_idx = 0;

            assignments[players[player_idx]["id"]].append(panels[i]["id"]);

        amount_per_player = 6;
        amount_needed = (num_players * amount_per_player) - len(panels);

        if amount_needed > 0:
            # we are aiming for 6 panels per player, if there is not enough go grab some pre-made ones
            backup_panels = db.get_panels_by_user(GAME_USER, amount_needed);

            if len(backup_panels) > 0:
                player_idx = 0;

                for i in range(0, len(amount_needed)):
                    while len(assignments[players[player_idx]["id"]]) >= amount_per_player:
                        player_idx = player_idx + 1;

                    j = i % len(backup_panels);
                    assignments[players[player_idx]["id"]].append(backup_panels[j]);


        db.store_assignments(game_id, assignments);

        end_time = int(time.time() + CREATE_TIME);

        db.set_game_state(game_id, GameState.CREATING, end_time);
        emit('update', {'state': GameState.CREATING, "round_end": end_time}, room=game_id, namespace='/');

        t = Timer(CREATE_TIME, create_time_compete, [game_id]);
        t.start();

def create_time_compete(game_id):
    with app.app_context():
        db.set_game_state(game_id, GameState.GATHERING, 0);
        emit('update', {'state': GameState.GATHERING}, room=game_id, namespace='/');

        t = Timer(GRACE_PERIOD, gather_time_compete, [game_id]);
        t.start();

def gather_time_compete(game_id):
    with app.app_context():
        # TODO: Find all unused assigned panels, and randomly build comics if requried

        db.set_game_state(game_id, GameState.RATING, 0);
        emit('update', {'state': GameState.RATING}, room=game_id, namespace='/');

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
    print("Starting server on port " + str(settings.PORT));
    socketio.run(app, host="0.0.0.0", port=settings.PORT)
