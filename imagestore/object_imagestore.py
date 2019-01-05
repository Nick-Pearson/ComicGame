from .imagestore_base import ImageStoreBase

import oci

#Image store using oracle object storage
class ObjectImageStore(ImageStoreBase):
    def __init__(this):
        print("Initialising object storage...");
        config = oci.config.from_file("~/.oci/config", "DEFAULT");
        this.obj = oci.object_storage.ObjectStorageClient(config);

    ######################
    # Interface
    ######################

    def get_image(this, image_id):
        r = this.obj.get_object("npcloud", "images", image_id);

        if r.status is not 200:
            return None;

        return r.data.raw.read()

    def store_image(this, image_id, image_data):
        r = this.obj.put_object("npcloud", "images", image_id, image_data.decode('base64'));
