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
    port = Int(None, allow_none=True)

    #: the id that will go in the URL of the container
    url_id = Unicode()

    @property
    def url(self):
        """Returns the relative url of the Container."""
        return "containers/{}".format(self.url_id)

    @property
    def host_url(self):
        """Returns the docker host where this server can be reached,
        in url form."""
        return "http://{ip}:{port}".format(
            ip=self.ip,
            port=self.port,
        )

    def __repr__(self):
        return ('<Container(docker_id={0}, name={1}, image_name={2}, '
                'image_id={3}, ip={4}, port={5}>').format(
                    self.docker_id, self.name,
                    self.image_name, self.image_id,
                    self.ip, self.port)

    @classmethod
    def from_docker_dict(cls, docker_dict):
        """Returns a Container object with the info given by a
        docker Client.

        Parameters
        ----------
        docker_dict : dict
            One item from the result of docker.Client.containers

        Returns
        -------
        container : Container

        Examples
        --------
        >>> # containers is a list of dict
        >>> containers = docker.Client().containers()

        >>> Container.from_docker_dict(containers[0])
        """
        if docker_dict.get('Ports'):
            ip = docker_dict['Ports'][0].get('IP', "")
            port = docker_dict['Ports'][0].get('PublicPort')
        else:
            ip = ""
            port = None

        return cls(docker_id=docker_dict.get('Id', ''),
                   name=docker_dict.get('Names', ('',))[0],
                   image_name=docker_dict.get('Image', ''),
                   image_id=docker_dict.get('ImageID', ''),
                   ip=ip, port=port)
