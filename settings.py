# Loads in settings
from dotenv import dotenv_values
import os

__settings = dotenv_values(dotenv_path = "./.env", verbose=True);

if "JWT_SECRET" in __settings:
    JWT_KEY = __settings["JWT_SECRET"];
else:
    raise RuntimeError("Missing JWT secret");

if "PORT" in __settings:
    PORT = __settings["PORT"];
else:
    PORT = 5000
