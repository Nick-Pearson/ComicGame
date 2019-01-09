from .database_base import DatabaseBase
import settings
import pymongo
from bson.objectid import ObjectId

# Base class for all database implementations
class MongoDatabase(DatabaseBase):
    def __init__(this):
        print("Initialising Mongo DB database...");
        this.client = pymongo.MongoClient("mongodb://" + settings.MONGO_HOST + ":27017/");
        print ("- Connected to: " + settings.MONGO_HOST + ":27017 v" + this.client.server_info()["version"]);
        this.db = this.client["comicgame"];

    def user_exists(this, user_id):
        query = {"_id": ObjectId(user_id)};
        doc = this.db["users"].find_one(query);
        return doc is not None

    def create_user(this, ip_addr):
        data = {"ip": ip_addr};
        doc = this.db["users"].insert_one(data);
        return str(doc.inserted_id);

    def game_exists(this, game_id):
        query = {"code": game_id};
        doc = this.db["games"].find_one(query);
        return doc is not None;

    def add_game_record(this, game_id, host_user):
        data = {"code": game_id, "host": host_user, "state":0, "round_end": 0, "players": []}
        doc = this.db["games"].insert_one(data);

    def query_game_for_user(this, game_id, user_id):
        query = {"code": game_id};
        doc = this.db["games"].find_one(query);

        if doc is None:
            return None;

        data = {};
        data["game_id"] = game_id;
        data["state"] = doc["state"];
        data["players"] = doc["players"];
        data["is_host"] = (str(doc["host"]) == user_id);
        data["is_spectator"] = not data["is_host"];
        data["round_end"] = doc["round_end"];

        for player in data["players"]:
            player["id"] = str(player["id"]);
            if player["id"] == user_id:
                data["is_spectator"] = False;

        return data;

    def add_user_to_game(this, game_id, user_id, name):
        query = {"code": game_id};
        doc = this.db["games"].find_one(query);

        if doc is None:
            return None;

        if user_id == doc["host"] or doc["state"] != 0:
            return True;

        for player in doc["players"]:
            # Check if we are already in this game
            if player["id"] == user_id:
                return True;

        player = {"id": ObjectId(user_id), "name": name, "score": 0};
        this.db["games"].update_one(query, {"$push": {"players": player}});
        return True;

    def set_game_state(this, game_id, new_state, end_time):
        query = {"code": game_id};
        this.db["games"].update_one(query, {"$set": {"state": new_state, "round_end": end_time}});

    def image_exists(this, image_id):
        query = {"_id": ObjectId(image_id)};
        doc = this.db["images"].find_one(query);
        return doc is not None;

    def create_image(this, created_by, role, game_id):
        data = {"created_by": created_by, "role": role, "game_id": game_id};
        doc = this.db["images"].insert_one(data);
        return str(doc.inserted_id);

    def add_panel_to_game(this, game_id, user_id):
        return this.create_image(user_id, 0, game_id);
