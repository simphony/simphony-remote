from traitlets import Unicode, HasTraits, Int


class Container(HasTraits):
    """Class representing a container.
    Note that its existence just describes a container.
    It does not imply that the associated container is still
    running, registered, or anything"""

    #: The docker id of the container
    docker_id = Unicode()

    #: The practical name of the container
    name = Unicode()

    #: The image name
    image_name = Unicode()

    #: And the image docker id
    image_id = Unicode()

    #: The ip address...
    ip = Unicode()

    #: ...and port where the container service will be listening
    port = Int()

    @property
    def url(self):
        """Returns the relative url of the Container."""
        return "containers/{}".format(self.docker_id)

    @property
    def host_url(self):
        """Returns the docker host where this server can be reached,
        in url form."""
        return "http://{ip}:{port}".format(
            ip=self.ip,
            port=self.port,
        )
