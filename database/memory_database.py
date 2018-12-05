# In-Memory database, used for debugging

from database_base import DatabaseBase

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
        this.__games[game_id] = {"host": host_user, "players":[]};
