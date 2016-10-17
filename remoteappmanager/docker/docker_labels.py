"""Contains established common dictionary of labels
that we use to add information to docker images or containers."""
from traitlets import HasTraits


class DockerLabelNamespace(HasTraits):
    def __init__(self, namespace, labels):
        super().__init__()
        self.namespace = (
            namespace[:-1] if namespace.endswith(".")
            else namespace)

        self.labels = labels

        for label in self.labels:
            setattr(self, label, ".".join([
                self.namespace,
                str(label)]))

    def __getitem__(self, item):
        """Returns the string "namespace.item"
        """
        return ".".join([self.namespace, str(item)])

# Namespaces for our labels.
SIMPHONY_NS = DockerLabelNamespace(
    "eu.simphony-project.docker",
    [
        # User interface name for the image
        "ui_name",
        # A 128x128px icon to represent the image
        "icon_128",
        # A long description of the image
        "description",
        # The type of the image: at the moment, it can be either
        # "vncapp", "webapp" or not present (for legacy apps). This will
        # affect the configurability of the image at startup.
        "type",
    ])

# environment variables that the container accepts.
# This is a sub-namespace. It will hold keys itself.
SIMPHONY_NS_ENV = DockerLabelNamespace(
    SIMPHONY_NS.namespace + ".env",
    [
        # These entries are extracted dynamically from the image
        # and interpreted as an envvar that the container accepts.
        # anything can be there.
    ]
)

SIMPHONY_NS_RUNINFO = DockerLabelNamespace(
    SIMPHONY_NS.namespace + ".runinfo",
    [
        # The jupyterhub user a given container is assigned to
        "user",
        # A unique identifier generated to refer uniquely to a given
        # docker application+configuration option
        "mapping_id",
        # A unique identifier that ends up in the URL to refer to a
        # running container. Could be the docker container ID but in
        # practice this is hard to obtain from inside the container,
        # leading to a chicken/egg situation
        "url_id",
        # The URL path where the container is exposed.
        # For example, if the user accesses it at
        # https://host:8000/user/username/containers/12345/
        # it will be /user/username/containers/12345/.
        # This is also the url that's been added to the reverse proxy.
        "frontend_urlpath"
    ],
)
