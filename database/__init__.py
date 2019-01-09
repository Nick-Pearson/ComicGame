#Select the correct database implementation here

def get_database(type):
    if type == "memory":
        from .memory_database import MemoryDatabase
        return MemoryDatabase();
    elif type == "mongo":
        from .mongo_database import MongoDatabase
        return MongoDatabase();
    else:
        raise RuntimeError("Database type " + type + " does not exist");
