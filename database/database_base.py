import random

# Base class for all database implementations
class DatabaseBase:
    ######################
    # Interface
    ######################

    def user_exists(this, user_id):
        raise NotImplementedError("Method not implemented");

    def create_user(this, ip_addr):
        raise NotImplementedError("Method not implemented");

    def game_exists(this, game_id):
        raise NotImplementedError("Method not implemented");

    def add_game_record(this, game_id, host_user):
        raise NotImplementedError("Method not implemented");

    def query_game_for_user(this, game_id, user_id):
        raise NotImplementedError("Method not implemented");

    def add_user_to_game(this, game_id, user_id, name):
        raise NotImplementedError("Method not implemented");

    def set_game_state(this, game_id, new_state, end_time):
        raise NotImplementedError("Method not implemented");

    def add_panel_to_game(this, game_id, user_id):
        raise NotImplementedError("Method not implemented");

    def image_exists(this, image_id):
        raise NotImplementedError("Method not implemented");

    def get_panels_in_game(this, game_id):
        raise NotImplementedError("Method not implemented");

    def get_panels_by_user(this, user_id, limit):
        raise NotImplementedError("Method not implemented");


    ######################
    # Methods
    ######################

    def create_game(this, user_id):
        game_id = this.generate_id(4);

        while(this.game_exists(game_id)):
            game_id = this.generate_id(4);

        this.add_game_record(game_id, user_id);

        # Update the user record with the new game id

        return game_id;

    def generate_user_id(this):
        out_id = '';
        for i in range(0,5):
            choice = random.randint(0, 31)

            if choice < 11:
                out_id += chr(ord('0') + choice);
            else:
                out_id += chr(ord('a') + choice - 11);

        return out_id;

    def generate_id(this, size):
        out_id = '';

        for i in range(0,size):
            choice = random.randint(0, 25)
            out_id += chr(ord('a') + choice);

        return out_id;
