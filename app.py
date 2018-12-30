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

@app.route('/', methods = ['GET'])
def index():
    res = make_response(render_template('index.html'));

    request_data = parse_request_data();

    res.set_cookie("cg_data", jwt.encode(request_data, settings.JWT_KEY, algorithm='HS256'), 60 * 60 * 24 * 365);
    return res;

@app.route('/game', methods = ['GET'])
def game():
    # TODO: Check the user belongs to a game
    return render_template('game.html');

@app.route('/api/game', methods = ["POST"])
def create_game():
    # TODO:
    # If this user is already hosting a game, cancel it and notify players
    # Add a new game record setting this user as the host
    # Update the user record with the new game id
    request_data = parse_request_data();

    res = make_response(jsonify({"game_id": "effg"}));
    res.set_cookie("cg_data", jwt.encode(request_data, settings.JWT_KEY, algorithm='HS256'), 60 * 60 * 24 * 365);

    return res

# Get game info, initial large data dump when loading a page. This is updated incrementally using web scokets
@app.route("/api/game/<game_id>", methods = ["GET"])
def get_game_info(game_id):
    return jsonify({"game_id": game_id,
                    "state": GameState.STARTING,
                    "is_host": True,
                    "is_spectator": False,
                    "players": [{"id":"h8dh0", "name": "Simon", "score": 0}, {"id":"wdhy9d2", "name": "Rick", "score": 0}, {"id":"02sj92", "name": "Gerry", "score": 0}, {"id":"n9q0x", "name": "Chris", "score": 0}, {"id":"8d3h80", "name": "Dave", "score": 0}]
                    });

@app.route('/api/game/start', methods = ["POST"])
def start_game():
    # TODO:
    # If the user is not hoting a game
    # If the game is in the STARTING state move onto DRAWNING and broadcast notify
    request_data = parse_request_data();

    res = make_response(jsonify({"success": True, "end_time": int(time.time() + DRAW_TIME)}));
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
        db = Database();
        data["user_id"] = db.create_user(request.remote_addr);

    return data;

if __name__ == "__main__":
    app.run()
