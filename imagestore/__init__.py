#Select the correct imagestore implementation here
from .object_imagestore import ObjectImageStore
from .folder_imagestore import FolderImageStore

def get_image_store(type):
    if type == "folder":
        return FolderImageStore();
    elif type == "object":
        return ObjectImageStore();
    else:
        raise RuntimeError("Imagetore type " + type + " does not exist");
