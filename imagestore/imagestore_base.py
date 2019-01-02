#Base class for image storage implementations
class ImageStoreBase:

    ######################
    # Interface
    ######################

    def has_image(this, image_id):
        raise NotImplementedError("Method not implemented");

    def get_image(this, image_id):
        raise NotImplementedError("Method not implemented");

    def store_image(this, image_id, image_data):
        raise NotImplementedError("Method not implemented");
