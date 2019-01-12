# In-Memory database, used for debugging

from .database_base import DatabaseBase
import time

class MemoryDatabase(DatabaseBase):
    def __init__(this):
        print("Initialising memory database...");
        this.__users = {};
        this.__games = {};
        this.__images = {};

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
        this.__games[game_id] = {"host": host_user, "state":0, "players":[], "panels":[], "round_end": 0, "create_time": int(time.time())};

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
