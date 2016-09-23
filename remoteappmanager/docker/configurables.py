import abc
# Contains a controlled dictionary of information
# that can be configured by the user at startup time.


class Configurable(metaclass=abc.ABCMeta):
    #: unique, controlled tag string that identifies the configurable.
    tag = None

    @abc.abstractclassmethod
    def supported_by(cls, image):
        """Checks if the passed image supports the configurable.
        Returns True if so, False otherwise"""

    @abc.abstractclassmethod
    def config_dict_to_env(cls, config_dict):
        """
        Extracts the relevant data from a dictionary.
        Returns a dictionary with the environment to transmit to the image
        to set this particular configurable.

        Raises if the config_dict is not in the expected format.

        IMPORTANT: the received dictionary is likely coming from
        hostile environment.
        """


class Resolution(Configurable):
    """Support for images that allow resolution change of the VNC server."""

    tag = "resolution"

    @classmethod
    def supported_by(cls, image):
        return all(x in image.env
                   for x in ["X11_WIDTH", "X11_HEIGHT", "X11_DEPTH"])

    @classmethod
    def config_dict_to_env(cls, config_dict):
        """
        the config dict must contain the following (example)

        {
            "resolution" : "1024x768"
        }

        """
        resolution = config_dict["resolution"]
        w, h = [int(value) for value in resolution.split("x")]
        if w < 0 or h < 0:
            raise ValueError("invalid width or height")

        return {
            "X11_WIDTH": str(w),
            "X11_HEIGHT": str(h),
            "X11_DEPTH": "16"
        }


def for_image(image):
    """Returns the configurables that are available for a specific
    image."""
    available = [Resolution]

    return [conf_class
            for conf_class in available
            if conf_class.supported_by(image)]
