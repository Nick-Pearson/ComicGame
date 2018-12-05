from flask import *
from database import Database
import jwt
import settings

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
    return render_template('game.html')

@app.route('/api/game', methods = ["POST"])
def create_game():
    # TODO:
    # If this user is already hosting a game, cancel it and notify players
    # Add a new game record setting this user as the host
    # Update the user record with the new game id
    request_data = parse_request_data();

    return jsonify({"game_id": "effg"});

@app.route("/api/game/<gamd_id>", methods = ["GET"])
def get_game_info(game_id):
    return jsonify({"game_id": game_id, "players": ["Simon", "Rick", "Gerry", "Chris", "Dave"], "is_host": True});

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
