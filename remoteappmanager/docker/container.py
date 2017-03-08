from remoteappmanager.docker.docker_labels import SIMPHONY_NS_RUNINFO
from traitlets import Unicode, HasTraits, Int, validate, TraitError


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

    #: Mapping identifier
    mapping_id = Unicode()

    #: The ip address...
    ip = Unicode()

    #: ...and port where the container service will be listening
    port = Int(80)

    #: The id that will go in the URL of the container.
    #: This is a de-facto replacement for the container docker id. The reason
    #: why we don't use that instead is because the container id is difficult
    #: to obtain reliably from inside the container, and because we want more
    #: flexibility in the form of the user-exposed id.
    #: Important: must be globally unique, not just per-user unique.
    url_id = Unicode()

    #: The user currently running the container
    user = Unicode()

    #: The url path of the container as it is exported to the user.
    #: e.g. "/home/test/containers/12345"
    #: Must not have an end slash.
    urlpath = Unicode()

    # The docker realm under which the container is running.
    realm = Unicode()

    @validate("urlpath")
    def _urlpath_validate(self, proposal):
        if proposal['value'].endswith('/'):
            raise TraitError("urlpath cannot end with a /")
        return proposal['value']

    @property
    def host_url(self):
        """Returns the docker host where this server can be reached,
        in url form."""
        return "http://{ip}:{port}".format(
            ip=self.ip,
            port=self.port,
        )

    def __repr__(self):
        return (
            '<Container(' +
            ", ".join(
                "{}={}".format(name, getattr(self, name))
                for name in self.trait_names()
                ) +
            ")>")

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
        container : remoteappmanager.docker.container.Container

        Examples
        --------
        >>> # containers is a list of dict
        >>> containers = docker.Client().containers()

        >>> Container.from_docker_dict(containers[0])
        """

        is_inspect_container_output = ("Config" in docker_dict)

        kwargs = dict(
            docker_id=docker_dict.get('Id') or '',
            ip=cls.ip.default_value,
            port=cls.port.default_value,
        )

        if is_inspect_container_output:
            # It's a client.inspect_container() output

            network_settings = docker_dict.get("NetworkSettings") or {}
            ports = network_settings.get("Ports") or {}
            # unfortunately, in the case of a running container, we don't have
            # a single list. Instead, we have a dict where the keys are
            # the "port identifier" (e.g. 8888/tcp) and the value is a list
            # of dictionaries.
            # We assume that we only have one, as above
            if len(ports) > 1:
                raise ValueError("Container Ports had more than one element.")

            if len(ports):
                port_values = list(ports.values())[0]
                if len(port_values) > 1:
                    raise ValueError("Container Ports values had "
                                     "more than one element.")

                if len(port_values):
                    kwargs["ip"] = port_values[0].get("HostIp") or kwargs["ip"]
                    kwargs["port"] = int(port_values[0].get("HostPort") or
                                         kwargs["port"])

            config = docker_dict.get("Config", {})
            labels = config.get("Labels")

            kwargs["image_name"] = config.get("Image")
            kwargs["image_id"] = docker_dict["Image"]
            kwargs["name"] = docker_dict["Name"]
        else:
            # It's a client.containers() output, so we have different rules.
            ports = docker_dict.get('Ports') or []
            if len(ports) > 1:
                raise ValueError("Container Ports had more than one element.")

            if len(ports):
                kwargs["ip"] = ports[0].get('IP') or kwargs["ip"]
                kwargs["port"] = int(ports[0].get('PublicPort') or
                                     kwargs["port"])

            labels = docker_dict.get("Labels") or {}

            kwargs["image_name"] = docker_dict.get('Image') or ''
            kwargs["image_id"] = docker_dict.get("ImageID") or ''
            names = docker_dict.get("Names") or ('', )
            kwargs["name"] = names[0]

        kwargs["mapping_id"] = labels.get(SIMPHONY_NS_RUNINFO.mapping_id) or ""
        kwargs["url_id"] = labels.get(SIMPHONY_NS_RUNINFO.url_id) or ""
        kwargs["user"] = labels.get(SIMPHONY_NS_RUNINFO.user) or ""
        kwargs["urlpath"] = labels.get(SIMPHONY_NS_RUNINFO.urlpath) or ""
        kwargs["realm"] = labels.get(SIMPHONY_NS_RUNINFO.realm) or ""

        try:
            return cls(**kwargs)
        except TraitError as e:
            raise ValueError(
                "Data does not satisfy trait constraints. "
                "{}.".format(e))
