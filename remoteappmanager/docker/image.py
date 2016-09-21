from remoteappmanager.docker.docker_labels import SIMPHONY_NS
from traitlets import Unicode, HasTraits


class Image(HasTraits):
    """Wrap class for the docker client images dict result.
    Extracts the relevant information in a convenient interface
    """
    #: The docker id of the image
    docker_id = Unicode()

    #: The name of the image.
    name = Unicode()

    #: The user interface (web) name of the image.
    ui_name = Unicode()

    #: A visual icon to associate to the image.
    icon_128 = Unicode()

    #: A long description of the image.
    description = Unicode()

    #: The type of the image. This allows to differentiate image behavior
    #: once started.
    type = Unicode()

    @classmethod
    def from_docker_dict(cls, docker_dict):
        """Converts the dict response from the dockerpy library into an
        instance of this class, extracting the relevant information.

        Parameters
        ----------
        docker_dict : dict
           Results of `docker.client.inspect_image` or an item of the
           result of `docker.client.images`
        """
        self = cls()
        self.docker_id = docker_dict["Id"]

        try:
            self.name = docker_dict["RepoTags"][0]
        except (KeyError, IndexError):
            self.name = ''

        labels = (docker_dict.get("Labels") or
                  docker_dict.get("Config", {}).get("Labels"))

        if labels is not None:
            self.ui_name = labels.get(SIMPHONY_NS.ui_name, '')
            self.icon_128 = labels.get(SIMPHONY_NS.icon_128, '')
            self.description = labels.get(SIMPHONY_NS.description, '')

        return self
