import abc


class Configurable(metaclass=abc.ABCMeta):
    """Base class for Configurables.
    They describe startup configuration entry points for images.
    Injection of the configurables data is done through a defined
    set of environment variables that the image accepts.
    """
    #: Unique, controlled tag string that identifies the configurable.
    tag = None

    @abc.abstractclassmethod
    def supported_by(cls, image):
        """Checks if the passed image supports the configurable.
        Returns True if so, False otherwise.

        Parameters
        ----------
        image: remoteappmanager.docker.Image
            The image to check if it supports this configurable

        Returns
        -------
        bool: True if the image supports the configurable.

        """

    @abc.abstractclassmethod
    def config_dict_to_env(cls, config_dict):
        """
        Extracts the relevant data from a dictionary.
        Returns a dictionary with the environment to transmit to the image
        to set this particular configurable. Values must be strings.

        Raises various exceptions if the config_dict is not in the expected
        format.

        IMPORTANT: the received dictionary is likely coming from
        hostile environment. Validate the contents strictly.

        Parameters
        ----------
        config_dict: Dict
            A dictionary containing data that the Configurable class
            understands.

        Returns
        -------
        Dict(Str, Str):
            A dictionary of environment variables to pass to the
            image at startup.
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
        """the config dict must contain the following (example)

        {
            "resolution" : "1024x768"
        }

        Observe that the key used has nothing to do with the tag.
        They are only accidentally the same.
        """
        resolution = config_dict["resolution"]
        w, h = [int(value) for value in resolution.split("x")]
        if w <= 0 or h <= 0:
            raise ValueError("invalid width or height")

        return {
            "X11_WIDTH": str(w),
            "X11_HEIGHT": str(h),
            "X11_DEPTH": "16"
        }


def for_image(image):
    """Returns the configurables that are available for a specific
    image.

    Parameters
    ----------
    image: remoteappmanager.docker.Image
        The image to check.

    Returns
    -------
    List
        A list of Configurable classes supported by the given image.

    """
    # We lack automatic registration. Add here new configurables
    available = [Resolution]

    return [conf_class
            for conf_class in available
            if conf_class.supported_by(image)]
