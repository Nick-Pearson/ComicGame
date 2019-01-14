from .database_base import DatabaseBase
import settings
import pymongo
from bson.objectid import ObjectId
import time

# Base class for all database implementations
class MongoDatabase(DatabaseBase):
    def __init__(this):
        print("Initialising Mongo DB database...");
        print("- Trying to connect to " + settings.MONGO_HOST + ":27017 ...");
        this.client = pymongo.MongoClient("mongodb://" + settings.MONGO_HOST + ":27017/", replicaset=settings.MONGO_RS);
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
        data = {"code": game_id, "host": host_user, "state":0, "round_end": 0, "players": [], "create_time": int(time.time()), "vote":""}
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
        data["vote"] = doc["vote"];

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
            if str(player["id"]) == user_id:
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

    def get_panels_in_game(this, game_id):
        query = {"game_id": game_id, "role": 0};

        out = [];

        for doc in this.db["images"].find(query):
            data = {"id": str(doc["_id"]), "created_by": doc["created_by"]};
            out.append(data);

        return out;

    def get_panels_by_user(this, user_id, limit):
        query = {"created_by": user_id, "role": 0};
        out = [];
        count = 0;

        for doc in this.db["images"].find(query):
            if count >= limit and limit >= 0:
                break;

            out.append(str(doc["_id"]));
            count = count + 1;

        return out;

    def get_assignments_for(this, game_id, user_id):
        query = {"code": game_id};
        doc = this.db["games"].find_one(query);

        if doc is None:
            return None;

        assignments = doc["assignments"];

        if user_id not in assignments:
            return None;

        return assignments[user_id];

    def store_assignments(this, game_id, assignments):
        query = {"code": game_id};
        this.db["games"].update_one(query, {"$set": {"assignments": assignments}});

    def add_comic_to_game(this, game_id, user_id, comic):
        iid = this.create_image(user_id, 1, game_id);

        query = {"code": game_id};
        data = {"id": iid, "created_by": user_id, "panels": comic};
        this.db["games"].update_one(query, {"$push": {"comics": data}});
        return iid;

    def set_cur_vote(this, game_id, vote_id):
        query = {"code": game_id};
        this.db["games"].update_one(query, {"$set": {"vote": vote_id}});

    def get_comics_in_game(this, game_id):
        query = {"code": game_id};
        doc = this.db["games"].find_one(query);

        if doc is None:
            return None;

        comics = doc["comics"];
        out = [];

        for i in range(0, len(comics)):
            data = {};
            data["id"] = comics[i]["id"];
            data["by"] = comics[i]["created_by"];
            data["panels"] = comics[i]["panels"];
            out.append(data);

        return out;

    def get_vote_info(this, vote_id):
        query = {"_id": ObjectId(vote_id)};
        doc = this.db["votes"].find_one(query);

        if doc is None:
            return None;

        data = {};
        data["id"] = str(doc["_id"]);
        data["game_id"] = doc["game_id"];
        data["index"] = doc["index"];
        data["complete"] = doc["complete"];
        data["forA"] = doc["forA"];
        data["forB"] = doc["forB"];
        data["comicA"] = doc["comicA"];
        data["comicB"] = doc["comicB"];

        return data;

    def create_vote(this, game_id, comicA, comicB, index, votes_expected):
        data = {"game_id": game_id, "index": index, "complete": False, "expected": votes_expected, "forA": 0, "forB": 0, "players": [], "comicA": comicA, "comicB": comicB};
        doc = this.db["votes"].insert_one(data);
        return str(doc.inserted_id);


    def add_vote(this, vote_id, user_id, forA):
        query = {"_id": ObjectId(vote_id)};
        doc = this.db["votes"].find_one(query);

        if doc is None:
            return False

        for player in doc["players"]:
            if player == user_id:
                return False

        if forA:
            data = {"forA": 1};
        else:
            data = {"forB": 1};

        this.db["votes"].update_one(query, {"$inc": data, "$push": {"players": user_id}});

        doc = this.db["votes"].find_one(query);

        complete = doc["forA"] + doc["forB"] >= doc["expected"];

        if complete != doc["complete"]:
            this.db["votes"].update_one(query, {"$set": {"complete": complete}});

        return complete
