#Select the correct imagestore implementation here

def get_image_store(type):
    if type == "folder":
        from .folder_imagestore import FolderImageStore
        return FolderImageStore();
    elif type == "object":
        from .object_imagestore import ObjectImageStore
        return ObjectImageStore();
    else:
        raise RuntimeError("Imagetore type " + type + " does not exist");
