# Loads in settings
from dotenv import dotenv_values
import os

__settings = dotenv_values(dotenv_path = "./.env", verbose=True);

if "JWT_SECRET" in __settings:
    JWT_KEY = __settings["JWT_SECRET"];
else:
    raise RuntimeError("Missing JWT secret");

if "PORT" in __settings:
    PORT = int(__settings["PORT"]);
else:
    PORT = 5000

if "IMAGE_STORE_TYPE" in __settings:
    IMAGE_STORE_TYPE = __settings["IMAGE_STORE_TYPE"];
else:
    IMAGE_STORE_TYPE = "folder"
