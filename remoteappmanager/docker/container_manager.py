import os
import string
from urllib.parse import urlparse
import uuid

from docker.errors import APIError, NotFound
from escapism import escape
from remoteappmanager.docker.async_docker_client import AsyncDockerClient
from remoteappmanager.docker.container import Container
from remoteappmanager.docker.docker_client_config import DockerClientConfig
from remoteappmanager.docker.image import Image
from remoteappmanager.logging.logging_mixin import LoggingMixin
from tornado import gen
from traitlets import (
    Dict,
    Int,
    Set,
    Instance,
    default)


#: Set of characters that are safe to use and should not be escaped by escapism
_CONTAINER_SAFE_CHARS = set(string.ascii_letters + string.digits + '-.')
_CONTAINER_ESCAPE_CHAR = '_'


class ContainerManager(LoggingMixin):
    #: The configuration of the docker client.
    #: Can be None. If that's the case, it will use the environment variables.
    docker_config = Instance(DockerClientConfig,
                             allow_none=True)

    #: Mapping of container_id to containers that are started by this
    #: manager (they may or may not be still running)
    containers = Dict()

    #: The asynchronous docker client.
    docker_client = Instance(AsyncDockerClient)

    #: The container (not host) port. We decided it's 8888 by default. It will
    #: be mapped to a random port on the host, so that our reverse proxy can
    #: refer to it.
    container_port = Int(8888)

    #: Keeps association of the containers for each image that this manager
    #: has started.
    _containers_for_image = Dict()

    #: Tracks if a given container is starting up.
    _start_pending = Set()

    #: Tracks if a given container is stopping down.
    _stop_pending = Set()

    @gen.coroutine
    def start_container(self, user_name, image_name, volumes=None):
        """Starts a container using the given image name.

        Parameters
        ----------
        user_name: string
            The name of the user
        image_name: string
            A string identifying the image name.
        volumes: dict
            {volume_source: {'bind': volume_target, 'mode': volume_mode}

        Return
        ------
        A container object containing information about the started container.
        """

        if image_name in self._start_pending:
            return None

        try:
            self._start_pending.add(image_name)
            result = yield self._start_container(user_name, image_name,
                                                 volumes)
        finally:
            self._start_pending.remove(image_name)

        return result

    @gen.coroutine
    def stop_and_remove_container(self, container_id):
        if container_id in self._stop_pending:
            return

        try:
            self._stop_pending.add(container_id)
            yield self._stop_and_remove_container(container_id)
        finally:
            self._stop_pending.remove(container_id)

    @gen.coroutine
    def containers_for_image(self, image_id_or_name, user_name=None):
        """Returns the currently running containers for a given image.

        If `user_name` is given, only returns containers started by the
        given user name.

        It is a coroutine because we might want to run an inquire to the docker
        service if not present.

        Parameters
        ----------
        image_id_or_name: str
            The image id or name

        Optional parameters
        -------------------
        user_name : str
            Name of the user who started the container

        Return
        ------
        A list of container objects, or an empty list if not present.
        """
        if user_name:
            user_labels = _get_container_labels(user_name)
            if user_labels:
                filters = {'label': '{0}={1}'.format(*user_labels.popitem())}
        else:
            filters = {}

        filters['ancestor'] = image_id_or_name

        containers = yield self.docker_client.containers(filters=filters)
        return [Container.from_docker_dict(container)
                for container in containers
                # Require further filtering as ancestor include grandparents
                if (container.get('Image') == image_id_or_name or
                    container.get('ImageID') == image_id_or_name)]

    @gen.coroutine
    def all_images(self):
        """Inquires all available images. Returns a list of Image objects.
        """
        image_dicts = yield self.docker_client.images(
            filters=dict(dangling=False))

        images = []
        for image_dict in image_dicts:
            image = Image.from_docker_dict(image_dict)
            images.append(image)

        return images

    @gen.coroutine
    def image(self, image_id_or_name):
        """Returns the Image object associated to a given id
        or name. If the image is not found, it returns None."""
        try:
            image_dict = yield self.docker_client.inspect_image(
                image_id_or_name)
        except NotFound:
            return None

        return Image.from_docker_dict(image_dict)

    # Private

    @gen.coroutine
    def _start_container(self, user_name, image_name, volumes):
        """Helper method that performs the physical operation of starting
        the container."""

        try:
            image_info = yield self.docker_client.inspect_image(image_name)
        except NotFound:
            self.log.error('Could not find requested image {}'.format(
                image_name))
            return None

        self.log.info('Got container image: {}'.format(image_name))
        # build the dictionary of keyword arguments for create_container
        container_name = _generate_container_name("remoteexec",
                                                  user_name,
                                                  image_name)
        container_url_id = _generate_container_url_id()

        # Check if the container is present. If not, create it
        container_info = yield self._get_container_info(container_name)

        if container_info is not None:
            # Make sure we stop and remove the container if by any change
            # is already there. This will guarantee a fresh start every time.
            self.log.info('Container for image {} '
                          'already present. Stopping.'.format(image_name))
            container_id = container_info["Id"]
            self.stop_and_remove_container(container_id)

        # Data volume binding to be used with Docker Client
        # volumes = {volume_source: {'bind': volume_target,
        #                            'mode': volume_mode}
        volumes = volumes if volumes else {}

        # Filter away the volume sources that do not exist,
        # otherwise Docker would create non-existing host directory
        # See Docker PR #21666
        filtered_volumes = {source: volumes[source]
                            for source in volumes
                            if os.path.exists(source)}

        volume_targets = [binding['bind']
                          for binding in filtered_volumes.values()]

        # Log the paths that are not being mounted
        if volumes.keys() - filtered_volumes.keys():
            self.log.error('Path(s) does not exist, not mounting:\n%s',
                           '\n'.join(volumes.keys() - filtered_volumes.keys()))

        create_kwargs = dict(
            image=image_name,
            name=container_name,
            environment=_get_container_env(user_name, container_url_id),
            volumes=volume_targets,
            labels=_get_container_labels(user_name))

        # build the dictionary of keyword arguments for host_config
        host_config = dict(
            port_bindings={
                self.container_port: None
            },
            binds=filtered_volumes
        )

        self.log.debug("Starting host with config: %s", host_config)
        host_config = yield self.docker_client.create_host_config(
            **host_config)

        # Get the host_config configuration in create_kwargs.
        # If it's not there, create an empty one.
        # Then update it with the current configuration.
        create_kwargs.setdefault('host_config', {}).update(host_config)

        resp = yield self.docker_client.create_container(**create_kwargs)

        container_id = resp['Id']

        self.log.info("Created container '%s' (id: %s) from image %s",
                      container_name, container_id, image_name)

        # start the container
        yield self.docker_client.start(container_id)

        ip, port = yield from self._get_ip_and_port(container_id)
        image_id = image_info["Id"]
        container = Container(
            docker_id=container_id,
            name=container_name,
            image_name=image_name,
            image_id=image_id,
            ip=ip,
            port=port,
            url_id=container_url_id,
        )

        self.log.info(
            ("Started container '{}' (id: {}). "
             "Exported port reachable at {}:{}").format(
                container_name,
                container_id,
                ip,
                port
            )
        )

        # Do the bookkeeping. Add the information to the internal data structs.
        # For now we can only have one container per image, but the interface
        # allows us to extend it.
        self.containers[container_id] = container
        self._containers_for_image[image_id] = [container]

        return container

    @gen.coroutine
    def _stop_and_remove_container(self, container_id):
        """Stops and removes the container identified by container_id.

        Parameters
        ----------
        container_id : string
            The unique identifier string identifying the container.
        """

        self.log.info("Stopping container {}".format(container_id))

        yield self._remove_container(container_id)

        # The container is gone from docker.
        # Do the ordinary internal bookkeeping.
        try:
            container = self.containers.pop(container_id)
        except KeyError:
            self.log.error(
                "Container id {} was not found in the "
                "container registry.".format(container_id))
            return

        # Remove the container from the internal pool
        image_id = container.image_id
        try:
            self._containers_for_image[image_id].clear()
        except KeyError:
            self.log.error(
                "Image '{}' was not found in the "
                "internal container_for_image pool.".format(
                    container.name))

    def _get_ip_and_port(self, container_id):
        """Returns the ip and port where the container service can be
        reached. Note that this is _not_ equivalent to docker port.
        docker port may return 0.0.0.0 as ip when the binding is on all
        interfaces of the docker container. We want the public ip of the
        exported port of a given container.

        If the container is no longer present, raises RuntimeError.

        Parameters
        ----------
        container_id: str
            The container id

        Return
        ------
        A tuple (ip, port)
        """

        # retrieve the actual port binding
        resp = yield self.docker_client.port(container_id, self.container_port)

        if resp is None:
            raise RuntimeError("Failed to get port info for %s" % container_id)

        # We assume we are running on linux without any additional docker
        # machine. The container will therefore be reachable at 127.0.0.1.
        # If we instead have a docker machine configuration, we use the
        # docker url to extract the ip.
        ip = '127.0.0.1'

        if self.docker_config and self.docker_config.docker_host != '':
            url = urlparse(self.docker_config.docker_host)
            if url.scheme == 'tcp':
                ip = url.hostname

        port = int(resp[0]['HostPort'])
        return ip, port

    @gen.coroutine
    def _get_container_info(self, container_id):
        """Retrieves the information about the given container id or name,
        and returns it. If the container is not available anymore, returns
        None.

        Parameters
        ----------
        container_id: str
            The container id. The name is accepted as well

        Return
        ------
        The container information as a dictionary, or None if not found
        """

        self.log.debug("Getting container '%s'", container_id)

        try:
            container_info = yield self.docker_client.inspect_container(
                container_id
            )
        except APIError as e:
            if e.response.status_code == 404:
                self.log.error("Container '%s' is gone", container_id)
                container_info = None
            elif e.response.status_code == 500:
                self.log.error("Container '%s' is on unhealthy node",
                               container_id)
                container_info = None
            else:
                raise
        return container_info

    @gen.coroutine
    def _remove_container(self, container_id):
        """Idempotent removal of a container by id.
        If the container is there, it will be removed. If it's not
        there, the unexpected conditions will be logged."""
        # Stop the container
        try:
            yield self.docker_client.stop(container_id)
        except APIError:
            self.log.exception(
                "Container '{}' could not be stopped.".format(
                    container_id,
                )
            )
        else:
            self.log.info("Container '{}' is stopped.".format(container_id))

        # Remove the container from docker
        try:
            yield self.docker_client.remove_container(container_id)
        except NotFound:
            self.log.error('Could not find requested container {} '
                           'during removal'.format(container_id))
        except APIError:
            self.log.exception(
                "Removal failed for container '{}'.".format(container_id)
            )
        else:
            self.log.info("Container '{}' is removed.".format(container_id))

    @default("docker_client")
    def _docker_client_default(self):
        return AsyncDockerClient(config=self.docker_config)


def _get_container_env(user_name, url_id):
    """Introduces the environment variables that are available
    at container startup time.

    Parameters
    ----------
    user_name: str
        The user name

    url_id: str
        A string containing the container identifier that will be used
        in the user-exposed URL.

    Return
    ------
    a dictionary containing the envvars to export.
    """

    return dict(
        # Username used to login to jupyterhub. Generally an email address.
        JPY_USER=user_name,
        # The base url. We use this one because the JPY username might
        # have been escaped.
        JPY_BASE_USER_URL="/user/"+user_name,
        # A unix username. used in the container to create the user.
        USER=_unix_user(user_name),
        # The identifier that will be used for the URL.
        URL_ID=url_id,
    )


def _get_container_labels(user_name):
    """Returns a dictionary that will become container run-time labels.
    Each of these labels must be namespaced in reverse DNS style, in agreement
    to docker guidelines."""

    return {
        "eu.simphony-project.docker.user": user_name,
    }


def _generate_container_name(prefix, user_name, image_name):
    """Generates a proper name for the container.
    It combines the prefix, username and image name after escaping.

    Parameters
    ----------
    prefix : string
        An arbitrary prefix for the container name.
    user_name: string
        the user name
    image_name: string
        The image name

    Return
    ------
    A string combining the three parameters in an appropriate container name
    """
    escaped_user_name = escape(user_name,
                               safe=_CONTAINER_SAFE_CHARS,
                               escape_char=_CONTAINER_ESCAPE_CHAR)
    escaped_image_name = escape(image_name,
                                safe=_CONTAINER_SAFE_CHARS,
                                escape_char=_CONTAINER_ESCAPE_CHAR)

    return "{}-{}-{}".format(prefix, escaped_user_name, escaped_image_name)


def _generate_container_url_id():
    """Generates a unique string to identify the container through a url"""
    return uuid.uuid4().hex


def _unix_user(username):
    """Converts a username from the jupyterhub login to a proper username
    for the docker virtual machine"""

    if '@' in username:
        return username.split('@')[0]

    # The username in the container is not critical, it's mostly a gimmick.
    # If it's not an email address (which is what we use to authenticate
    # users, we just prevent it to return a potentially invalid username
    # and just return the string user, which is good enough
    return 'user'
