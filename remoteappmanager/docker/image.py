from remoteappmanager.docker import docker_labels
from traitlets import Unicode, HasTraits


class Image(HasTraits):
    """Wrap class for the docker client images dict result.
    Extracts the relevant information in a convenient interface
    """
    #: The docker id of the image
    docker_id = Unicode()

    #: The name of the
    name = Unicode()

    #: The user interface (web) name of the image.
    ui_name = Unicode()

    #: A visual icon to associate to the image.
    icon_128 = Unicode()

    #: A long description of the image.
    description = Unicode()

    @classmethod
    def from_docker_dict(cls, docker_dict):
        """Converts the dict response from the dockerpy library into an
        instance of this class, extracting the relevant information."""
        self = cls()
        self.docker_id = docker_dict["Id"]

        try:
            self.name = docker_dict["RepoTags"][0]
        except (KeyError, IndexError):
            self.name = ''

        labels = (docker_dict.get("Labels") or
                  docker_dict.get("Config", {}).get("Labels"))

        if labels is not None:
            self.ui_name = labels.get(docker_labels.UI_NAME, '')
            self.icon_128 = labels.get(docker_labels.ICON_128, '')
            self.description = labels.get(docker_labels.DESCRIPTION, '')

        return self
