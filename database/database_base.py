import random

# Base class for all database implementations
class DatabaseBase:
    ######################
    # Interface
    ######################

    def user_exists(this, user_id):
        raise NotImplementedError("Method not implemented");


    ######################
    # Methods
    ######################

    def create_user(this, ip_addr):
        user_id = this.generate_user_id();

        while(this.user_exists(user_id)):
            user_id = this.generate_user_id();

        return user_id;

    def generate_user_id(this):
        out_id = '';
        for i in range(0,5):
            choice = random.randint(0, 31)
            
            if choice < 11:
                out_id += chr(ord('0') + choice);
            else:
                out_id += chr(ord('a') + choice - 11);

        return out_id;
