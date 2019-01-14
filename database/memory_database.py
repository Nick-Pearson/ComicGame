# In-Memory database, used for debugging

from .database_base import DatabaseBase
import time

class MemoryDatabase(DatabaseBase):
    def __init__(this):
        print("Initialising memory database...");
        this.__users = {};
        this.__games = {};
        this.__images = {};
        this.__votes = {};

    def user_exists(this, user_id):
        if user_id in this.__users:
            return True;

        return False;

    def add_user_record(this, user_id, ip_addr):
        this.__users[user_id] = [ip_addr];

    def game_exists(this, game_id):
        if game_id in this.__games:
            return True;

        return False;

    def add_game_record(this, game_id, host_user):
        this.__games[game_id] = {"host": host_user, "state":0, "players":[], "panels":[], "comics":[], "round_end": 0, "create_time": int(time.time()), "assignments": {}, "vote": ""};

    def query_game_for_user(this, game_id, user_id):
        if game_id not in this.__games:
            return None

        record = this.__games[game_id];
        data = {};
        data["game_id"] = game_id;
        data["state"] = record["state"];
        data["players"] = record["players"];
        data["is_host"] = (record["host"] == user_id);
        data["is_spectator"] = not data["is_host"];
        data["round_end"] = record["round_end"];
        data["vote"] = record["vote"];

        for player in record["players"]:
            if player["id"] == user_id:
                data["is_spectator"] = False;

        return data;

    def add_user_to_game(this, game_id, user_id, name):
        if game_id not in this.__games:
            return False;

        record = this.__games[game_id];

        if user_id == record["host"] or record["state"] != 0:
            return True;

        for player in record["players"]:
            # Check if we are already in this game
            if player["id"] == user_id:
                return True;

        data = {"id": user_id, "name": name, "score": 0};
        this.__games[game_id]["players"].append(data);

        return True;

    def set_game_state(this, game_id, new_state, end_time):
        if game_id not in this.__games:
            return False;

        this.__games[game_id]["state"] = new_state;

        if new_state == 1:
            this.__games[game_id]["round_end"] = end_time;

        return True;

    def add_panel_to_game(this, game_id, user_id):
        if game_id not in this.__games:
            return None;

        image_id = this.create_image(user_id, 0, game_id);

        this.__games[game_id]["panels"].append(image_id);
        return image_id;

    def add_image_record(this, image_id, created_by, role, game_id):
        this.__images[image_id] = [created_by, role, game_id];

    def image_exists(this, image_id):
        if image_id in this.__images:
            return True;

        return False;

    def create_user(this, ip_addr):
        user_id = this.generate_user_id();

        while(this.user_exists(user_id)):
            user_id = this.generate_user_id();

        this.add_user_record(user_id, ip_addr);

        return user_id;

    def create_image(this, created_by, role, game_id):
        image_id = this.generate_id(6);

        while(this.image_exists(image_id)):
            image_id = this.generate_id(6);

        this.add_image_record(image_id, created_by, role, game_id);

        return image_id;

    def get_panels_in_game(this, game_id):
        if game_id not in this.__games:
            return [];

        ids = this.__games[game_id]["panels"];
        out = [];

        for id in ids:
            data = {"id": id, "created_by": this.__images[id][0]};
            out.append(data);

        return out;

    def get_panels_by_user(this, user_id, limit):
        out = [];
        count = 0;

        for id in this.__images.keys():
            if count >= limit and limit >= 0:
                break;

            if this.__images[id][1] == 0 and this.__images[id][0] == user_id:
                out.append(id);
                count = count + 1;

        return out;

    def get_assignments_for(this, game_id, user_id):
        if game_id not in this.__games:
            return None;

        assignments = this.__games[game_id]["assignments"];

        if user_id not in assignments:
            return None;

        return assignments[user_id];

    def store_assignments(this, game_id, assignments):
        if game_id not in this.__games:
            return;

        this.__games[game_id]["assignments"] = assignments;


    def add_comic_to_game(this, game_id, user_id, comic):
        if game_id not in this.__games:
            return None

        iid = this.create_image(user_id, 1, game_id);
        this.__games[game_id]["comics"].append({"id": iid, "created_by": user_id, "panels": comic});
        return iid;

    def set_cur_vote(this, game_id, vote_id):
        if game_id not in this.__games:
            return None

        this.__games[game_id]["vote"] = vote_id;

    def get_comics_in_game(this, game_id):
        if game_id not in this.__games:
            return [];

        comics = this.__games[game_id]["comics"];
        out = [];

        for i in range(0, len(comics)):
            data = {};
            data["id"] = comics[i]["id"];
            data["by"] = comics[i]["created_by"];
            data["panels"] = comics[i]["panels"];
            out.append(data);

        return out;

    def get_vote_info(this, vote_id):
        if vote_id not in this.__votes:
            return None;

        record = this.__votes[vote_id];

        data = {};
        data["id"] = record["id"];
        data["game_id"] = record["game_id"];
        data["index"] = record["index"];
        data["complete"] = record["complete"];
        data["forA"] = record["forA"];
        data["forB"] = record["forB"];
        data["comicA"] = record["comicA"];
        data["comicB"] = record["comicB"];

        return data;

    def create_vote(this, game_id, comicA, comicB, index, votes_expected):
        vote_id = this.generate_id(10);

        while vote_id in this.__votes:
            vote_id = this.generate_id(10);

        this.__votes[vote_id] = {"id": vote_id, "game_id": game_id, "index": index, "complete": False, "expected": votes_expected, "forA": 0, "forB": 0, "players": [], "comicA": comicA, "comicB": comicB};
        return vote_id;


    def add_vote(this, vote_id, user_id, forA):
        if vote_id not in this.__votes:
            return False;

        record = this.__votes[vote_id];

        for player in record["players"]:
            if player == user_id:
                return False

        if forA:
            this.__votes[vote_id]["forA"] = this.__votes[vote_id]["forA"] + 1;
        else:
            this.__votes[vote_id]["forB"] = this.__votes[vote_id]["forB"] + 1;

        this.__votes[vote_id]["players"].append(user_id);

        record = this.__votes[vote_id];

        complete = record["forA"] + record["forB"] >= record["expected"];
        this.__votes[vote_id]["complete"] = complete;
        return complete
