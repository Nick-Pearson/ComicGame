# Loads in settings
from dotenv import dotenv_values
import os

__settings = dotenv_values(dotenv_path = "./.env", verbose=True);

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
