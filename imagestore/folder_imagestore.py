from .imagestore_base import ImageStoreBase
import os

class FolderImageStore(ImageStoreBase):
    def __init__(this):
        print("Initialising folder storage...");
        this.folder = os.getcwd() + "/data";
        if not os.access(this.folder, os.F_OK):
            os.mkdir(this.folder);

    def get_image(this, image_id):
        path = this.folder + "/" + image_id + ".png";

        try:
            fd = open(path, 'r');
        except IOError as e:
            if e.errno == errno.EACCES:
                return None
            else:
                raise
        else:
            with fd:
                return fd.read()

    def store_image(this, image_id, image_data):
        path = this.folder + "/" + image_id + ".png";

        fd = open(path, 'wb');
        fd.write(image_data.decode('base64'));
        fd.close();
