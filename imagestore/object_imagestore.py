from .imagestore_base import ImageStoreBase

import oci
import settings

#Image store using oracle object storage
class ObjectImageStore(ImageStoreBase):
    def __init__(this):
        print("Initialising object storage...");

        if settings.OCI_CONFIG_FROM_FILE:
            print(" - grabbing OCI config from file");
            config = oci.config.from_file("~/.oci/config", "DEFAULT");
        else:
            print(" - grabbing OCI config from environment variables");
            config = {
                'region': 'us-ashburn-1',
                'log_requests': False,
                'tenancy': settings.OCI_TENNANT,
                'user': settings.OCI_USER,
                'pass_phrase': settings.OCI_SECRET,
                'fingerprint': settings.OCI_FINGERPRINT,
                'additional_user_agent': '',
                'key_file': '/root/.oci/oci_api_key.pem'
            };

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
