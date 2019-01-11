# Loads in settings
from dotenv import dotenv_values
import os

__settings = dotenv_values(dotenv_path = "./.env");

if "JWT_SECRET" in __settings:
    JWT_KEY = __settings["JWT_SECRET"];
elif os.getenv("JWT_SECRET") is not None:
    JWT_KEY = os.getenv("JWT_SECRET");
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

if "DATABASE_TYPE" in __settings:
    DATABASE_TYPE = __settings["DATABASE_TYPE"];

    if DATABASE_TYPE == "mongo":
        # get mogo credientials
        if "MONGO_HOST" in __settings:
            MONGO_HOST = __settings["MONGO_HOST"];
        elif os.getenv("MONGO_HOST") is not None:
            MONGO_HOST = os.getenv("MONGO_HOST");
        else:
            raise RuntimeError("Missing mongo db host");

        if "MONGO_RS" in __settings:
            MONGO_RS = __settings["MONGO_RS"];
        elif os.getenv("MONGO_RS") is not None:
            MONGO_RS = os.getenv("MONGO_RS");
        else:
            raise RuntimeError("Missing mongo db replica set");
else:
    DATABASE_TYPE = "memory"

if "OCI_CONFIG_TYPE" in __settings:
    OCI_CONFIG_FROM_FILE = True if __settings["OCI_CONFIG_TYPE"] == "file" else False;
else:
    OCI_CONFIG_FROM_FILE = False;

if not OCI_CONFIG_FROM_FILE:
    # look for oci config values
    OCI_SECRET = os.getenv("OCI_SECRET");
    OCI_USER = os.getenv("OCI_USER");
    OCI_TENNANT = os.getenv("OCI_TENNANT");
    OCI_FINGERPRINT = None if "FINGERPRINT" not in __settings else __settings["FINGERPRINT"];

    if OCI_SECRET is None or OCI_USER is None or OCI_TENNANT is None or OCI_FINGERPRINT is None:
        raise RuntimeError("Missing OCI credientials in environment");
