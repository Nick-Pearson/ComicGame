from flask import *
from database import Database
import jwt
import settings
import time

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

app = Flask(__name__)

db = Database();

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

@app.route('/api/game/start/<game_id>', methods = ["POST"])
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

        res = make_response(jsonify({"success": True, "game_id": game_id, "state": record["state"], "end_time": end_time}));

    res.set_cookie("cg_data", jwt.encode(request_data, settings.JWT_KEY, algorithm='HS256'), 60 * 60 * 24 * 365);

    return res

@app.route('/api/game/join/<game_id>', methods = ["POST"])
def join_game(game_id):
    game_id = game_id.lower();
    request_data = parse_request_data();

    if "name" not in request.form:
        res = make_response(jsonify({"error": "Player name is required"}));
        res.status = 400;
        return res;

    if db.add_user_to_game(game_id, request_data["user_id"], request.form["name"]):
        res = make_response(jsonify({"success":True, "game_id": game_id}));
    else:
        res = make_response(jsonify({"error":"Game not found"}));
        res.status_code = 404;

    res.set_cookie("cg_data", jwt.encode(request_data, settings.JWT_KEY, algorithm='HS256'), 60 * 60 * 24 * 365);

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

if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler

    server = pywsgi.WSGIServer(('0.0.0.0', 5000), app, handler_class=WebSocketHandler);
    server.serve_forever();
