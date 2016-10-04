import string
from traitlets import Unicode, HasTraits, Dict, List

from remoteappmanager.docker.docker_labels import SIMPHONY_NS, SIMPHONY_NS_ENV
from remoteappmanager.docker import configurables

# Characters that are allowed in the environment variables.
_ALLOWED_ENVCHARS = set(string.ascii_lowercase + string.digits + "-")


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

    #: The type of the image.
    type = Unicode()

    # A dictionary of supported environment variables that the
    # container can accept as parameters. Note that the labels
    # use a different notation, so a conversion takes place:
    # dashes are converted to underscores, and letters are capitalized.
    # e.g. x11-width -> X11_WIDTH
    # Only keys are used at the moment.
    env = Dict()

    # A list of configurables that the image supports.
    configurables = List()

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
            self.type = labels.get(SIMPHONY_NS.type, '')

            env_prefix = SIMPHONY_NS_ENV.namespace+"."
            for env in [lab[len(env_prefix):]
                        for lab in labels.keys()
                        if lab.startswith(env_prefix)]:

                if len(set(env) - _ALLOWED_ENVCHARS) != 0:
                    # Skip badly formed stuff.
                    continue

                env = env.upper().replace("-", "_")
                # Docker does not allow unexistent values in
                # labels, but we should not rely on them anyway,
                # as only presence of the env key has a clear
                # meaning, hence we force the value to empty.
                self.env[env] = ""

        self.configurables = configurables.for_image(self)
        return self
