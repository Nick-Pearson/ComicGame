from flask import *
from database import Database

app = Flask(__name__)

@app.route('/', methods = ['GET'])
def index():
    res = make_response(render_template('index.html'));

    user_id = get_or_generate_userid();
    # res.co
    return res;

@app.route('/game', methods = ['GET'])
def game():
    # TODO: Check the user belongs to a game
    return render_template('game.html')

def get_or_generate_userid():
    if "cg_userid" in request.cookies:
        return request.cookies("cg_userid");

    # create a new user ID
    db = Database();
    return db.create_user(request.remote_addr);

if __name__ == "__main__":
    app.run()
