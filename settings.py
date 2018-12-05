# Loads in settings
from dotenv import dotenv_values
import os

__settings = dotenv_values(dotenv_path = "./.env", verbose=True);

if "JWT_SECRET" in __settings:
    JWT_KEY = __settings["JWT_SECRET"];
else:
    raise RuntimeError("Invalid or missing JWT secret");
