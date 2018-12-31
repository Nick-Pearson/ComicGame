# In-Memory database, used for debugging

from .database_base import DatabaseBase

class Database(DatabaseBase):
    def __init__(this):
        this.__users = {};
        this.__games = {};

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
        this.__games[game_id] = {"host": host_user, "state":0, "players":[], "round_end": 0};

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
                player["name"] = name;
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
