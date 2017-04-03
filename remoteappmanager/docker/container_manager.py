import os
import string
from urllib.parse import urlparse
import uuid
import random

from docker.errors import APIError, NotFound
from escapism import escape
from remoteappmanager.docker.async_docker_client import AsyncDockerClient
from remoteappmanager.docker.container import Container
from remoteappmanager.docker.docker_labels import SIMPHONY_NS_RUNINFO

from remoteappmanager.docker.image import Image
from remoteappmanager.logging.logging_mixin import LoggingMixin
from remoteappmanager.utils import (
    url_path_join,
    without_end_slash)


from tornado import gen
from traitlets import (
    Int,
    Dict,
    Set,
    Instance,
    Unicode,
    default)


#: Set of characters that are safe to use and should not be escaped by escapism

_CONTAINER_SAFE_CHARS = set(string.ascii_letters + string.digits + '-.')
_CONTAINER_ESCAPE_CHAR = '_'


class OperationInProgress(Exception):
    """Exception raised when the operation for the requested image or
    container is already in progress."""
    pass


class MultipleResultsFound(Exception):
    """Raised when we are asking for a specific container, but more than
    one result is found."""


class ContainerManager(LoggingMixin):

    #: The container (not host) port. We decided it's 8888 by default. It will
    #: be mapped to a random port on the host, so that our reverse proxy can
    #: refer to it.
    container_port = Int(8888)

    #: The docker client configuration
    docker_config = Dict()

    # Docker realm this container manager handles. Useful to have
    # different instances of simphony-remote access the same docker.
    realm = Unicode("remoteexec")

    #: Tracks if a given mapping id is starting up.
    _start_pending = Set()

    #: Tracks if a given container id is stopping down.
    _stop_pending = Set()

    #: The asynchronous docker client.
    _docker_client = Instance(AsyncDockerClient)

    def __init__(self, docker_config, *args, **kwargs):
        """Initializes the Container manager.

        Parameters
        ----------
        docker_config: Dict
            A dictionary containing the keywords for the configuration of
            the docker client in agreement to docker py documentation.
        realm: Unicode
            The docker realm
        """
        self.docker_config = docker_config
        super().__init__(*args, **kwargs)

    @gen.coroutine
    def start_container(self,
                        user_name,
                        image_name,
                        mapping_id,
                        base_urlpath,
                        volumes,
                        environment=None):
        """
        Starts a container using the given image name.

        Parameters
        ----------

        user_name: string
            The name of the user
        image_name: string
            A string identifying the image name.
        mapping_id: str
            A generic id used to recognize the container.
            it is expected to be unique (and persistent) for a specific
            combination of docker image (i.e. application) and setup
            (i.e. configuration).
        base_urlpath: str
            The base urlpath for the current user.
        volumes: dict or None
            {volume_source: {'bind': volume_target, 'mode': volume_mode}
        environment: dict or None
            Contains additional keyvalue pairs that will be exported
            as environment variables inside the container.

        Return
        ------
        A container object containing information about the started container.

        Raises
        ------
        OperationInProgres:
            if the requested mapping id is already scheduled for addition

        """

        if mapping_id in self._start_pending:
            raise OperationInProgress("start {}".format(mapping_id))

        if environment is None:
            environment = {}

        try:
            self._start_pending.add(mapping_id)
            result = yield self._start_container(user_name,
                                                 image_name,
                                                 mapping_id,
                                                 base_urlpath,
                                                 volumes,
                                                 environment)
        finally:
            self._start_pending.remove(mapping_id)

        return result

    @gen.coroutine
    def stop_and_remove_container(self, container_id):
        """Idempotent removal of a container by id.
        If the container is there, it will be removed. If it's not
        there, the unexpected conditions will be logged.

        Parameters
        ----------
        container_id : str
            A string containing the container identifier.

        Raises
        ------
        OperationInProgres:
            if the requested container id is already scheduled for removal.
        """

        if container_id in self._stop_pending:
            raise OperationInProgress("stop {}".format(container_id))

        try:
            self._stop_pending.add(container_id)
            yield self._stop_and_remove_container(container_id)
        finally:
            self._stop_pending.remove(container_id)

    @gen.coroutine
    def containers_with_labels(self, labels):
        filters = {
            'label': ['{0}={1}'.format(k, v) for k, v in labels.items()]}

        containers = yield self.containers_from_filters(filters)
        return containers

    @gen.coroutine
    def containers_from_filters(self, filters):
        """Returns the currently running containers for a given filter

        Parameters
        ----------
        filters: dict
            A dictionary of filters as in dockerpy

        Return
        ------
        A list of Container objects, or an empty list if nothing is found.
        """
        containers = []
        infos = yield self._docker_client.containers(filters=filters)
        for info in infos:
            try:
                container = Container.from_docker_dict(info)
            except ValueError:
                self.log.exception("Unable to parse container info.")
                continue

            # override the ip and port obtained by the docker info with the
            # appropriate ip and port, considering that we might be using a
            # separate docker machine
            try:
                ip, port = yield from self._get_ip_and_port(
                    container.docker_id)
            except RuntimeError:
                self.log.exception(
                    "Unable to retrieve ip/port "
                    "for container {}".format(container.docker_id))
                continue

            container.ip = ip
            container.port = port
            containers.append(container)

        return containers

    @gen.coroutine
    def find_containers(self,
                        *,
                        url_id=None,
                        mapping_id=None,
                        user_name=None):
        """Finds and returns containers matching all the specified arguments.
        """
        labels = {
            SIMPHONY_NS_RUNINFO.realm: self.realm
        }

        if url_id is not None:
            labels[SIMPHONY_NS_RUNINFO.url_id] = url_id

        if mapping_id is not None:
            labels[SIMPHONY_NS_RUNINFO.mapping_id] = mapping_id

        if user_name is not None:
            labels[SIMPHONY_NS_RUNINFO.user] = user_name

        containers = yield self.containers_with_labels(labels)

        return containers

    @gen.coroutine
    def find_container(self,
                       *,
                       url_id=None,
                       mapping_id=None,
                       user_name=None):
        """Find and returns a container matching the specified
        arguments.

        Returns the found container or None. If multiple containers
        match the query, it will raise MultipleResultsFound"""
        containers = yield self.find_containers(url_id=url_id,
                                                mapping_id=mapping_id,
                                                user_name=user_name)
        if len(containers) > 1:
            raise MultipleResultsFound()

        if len(containers) == 1:
            return containers[0]

        return None

    @gen.coroutine
    def image(self, image_id_or_name):
        """Returns the Image object associated to a given id
        """
        try:
            image_dict = yield self._docker_client.inspect_image(
                image_id_or_name)
        except NotFound:
            return None

        return Image.from_docker_dict(image_dict)

    # Private

    @gen.coroutine
    def _start_container(self,
                         user_name,
                         image_name,
                         mapping_id,
                         base_urlpath,
                         volumes,
                         environment):
        """Helper method that performs the physical operation of starting
        the container.

        If successful, returns a Container object.
        If any exception occurs, it logs it and re-raises an exception.
        """

        try:
            image_info = yield self._docker_client.inspect_image(image_name)
            image_id = image_info["Id"]
        except NotFound as e:
            self.log.error('Could not find requested image {}'.format(
                image_name))
            raise e
        except Exception as e:
            self.log.exception("Could not inspect image {}".format(
                image_name
            ))
            raise e

        self.log.info('Got container image: {}'.format(image_name))

        # Check if the container is present.
        container = yield self.find_containers(
            user_name=user_name, mapping_id=mapping_id)

        if container is not None:
            # Make sure we stop and remove it if by any chance is already
            # there. This will guarantee a fresh start every time.
            self.log.info('Container for image {} '
                          'already present. Stopping.'.format(image_name))
            yield self.stop_and_remove_container(container.docker_id)

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

        self.log.info(
            'Mounting these volumes: \n%s',
            '\n'.join('{0} -> {1}'.format(source, target['bind'])
                      for source, target in filtered_volumes.items()))

        container_url_id = _generate_container_url_id()
        container_urlpath = without_end_slash(
            url_path_join(base_urlpath,
                          "containers",
                          container_url_id))
        container_name = _generate_container_name(self.realm,
                                                  user_name,
                                                  mapping_id)
        create_kwargs = dict(
            image=image_name,
            name=container_name,
            environment=_get_container_env(user_name,
                                           container_url_id,
                                           environment,
                                           base_urlpath),
            volumes=volume_targets,
            labels=_get_container_labels(user_name,
                                         mapping_id,
                                         container_url_id,
                                         container_urlpath,
                                         self.realm))

        # build the dictionary of keyword arguments for host_config
        host_config = dict(
            port_bindings={
                self.container_port: None
            },
            binds=filtered_volumes
        )

        self.log.debug("Starting host with config: %s", host_config)
        host_config = yield self._docker_client.create_host_config(
            **host_config)

        # Get the host_config configuration in create_kwargs.
        # If it's not there, create an empty one.
        # Then update it with the current configuration.
        create_kwargs.setdefault('host_config', {}).update(host_config)

        resp = yield self._docker_client.create_container(**create_kwargs)

        container_id = resp['Id']

        self.log.info("Created container '%s' (id: %s) from image %s",
                      container_name, container_id, image_name)

        # start the container
        try:
            yield self._docker_client.start(container_id)
        except Exception as e:
            self.log.exception("Could not start container {}".format(
                container_id))
            yield self.stop_and_remove_container(container_id)
            raise e

        try:
            ip, port = yield from self._get_ip_and_port(container_id)
        except Exception as e:
            self.log.exception(
                "Could not retrieve ip/port information "
                "for container {}".format(container_id))
            yield self.stop_and_remove_container(container_id)
            raise e

        container = Container(
            docker_id=container_id,
            name=container_name,
            image_name=image_name,
            image_id=image_id,
            mapping_id=mapping_id,
            ip=ip,
            port=port,
            url_id=container_url_id,
            urlpath=container_urlpath,
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

        return container

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

        Raises
        ------
        RuntimeError:
            If for some reason it cannot retrieve the information
        """

        # retrieve the actual port binding
        try:
            resp = yield self._docker_client.port(container_id,
                                                  self.container_port)
        except Exception as e:
            raise RuntimeError("Failed to get port info for {}. "
                               "Exception: {}.".format(container_id,
                                                       str(e)))

        if resp is None:
            raise RuntimeError("Failed to get port info for {}. "
                               "Port response was None.".format(container_id))

        # We assume we are running on linux without any additional docker
        # machine. The container will therefore be reachable at 127.0.0.1.
        # If we instead have a docker machine configuration, we use the
        # docker url to extract the ip.
        ip = '127.0.0.1'

        base_url = self.docker_config.get("base_url")
        if base_url:
            url = urlparse(base_url)
            if url.scheme != 'unix':
                ip = url.hostname

        try:
            port = int(resp[0]['HostPort'])
        except (KeyError, IndexError, ValueError, TypeError) as e:
            raise RuntimeError("Failed to get port info for {}. "
                               "Exception: {}.".format(container_id,
                                                       str(e)))

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
            container_info = yield self._docker_client.inspect_container(
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
    def _stop_and_remove_container(self, container_id):
        """Idempotent removal of a container by id.
        If the container is there, it will be removed. If it's not
        there, the unexpected conditions will be logged.

        Note: The container is only stopped if it belongs to the same
        realm.
        """

        self.log.info("Stopping container {}".format(container_id))

        container_info = yield self._get_container_info(container_id)

        if container_info is None:
            self.log.error('Could not find requested container {} '
                           'during removal'.format(container_id))
            return

        container = Container.from_docker_dict(container_info)
        if container.realm != self.realm:
            self.log.error(
                'Container {} belongs to realm {} '
                'instead of {}. Refusing to stop.'.format(
                    container_id,
                    container.realm,
                    self.realm)
            )
            return

        # Technically, we have a race condition here, but it's pretty much
        # impossible to solve, and would only affect us if the container
        # id is identical.

        # Stop the container
        try:
            yield self._docker_client.stop(container_id)
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
            yield self._docker_client.remove_container(container_id)
        except NotFound:
            self.log.error('Could not find requested container {} '
                           'during removal'.format(container_id))
        except APIError:
            self.log.exception(
                "Removal failed for container '{}'.".format(container_id)
            )
        else:
            self.log.info("Container '{}' is removed.".format(container_id))

    @default("_docker_client")
    def _docker_client_default(self):
        return AsyncDockerClient(**self.docker_config)


def _get_container_env(user_name, url_id, environment, base_urlpath):
    """Introduces the environment variables that are available
    at container startup time.

    Parameters
    ----------
    user_name: str
        The user name

    url_id: str
        A string containing the container identifier that will be used
        in the user-exposed URL.

    environment: dict
        Additional environment keys to add to the final result.
        Note that these will not take precedence.

    base_urlpath: str
        the user's base urlpath

    Return
    ------
    a dictionary containing the envvars to export.
    """

    result = {}
    if environment:
        result.update(environment)

    result.update(dict(
        # Username used to login to jupyterhub. Generally an email address.
        JPY_USER=user_name,
        # The base url. We use this one because the JPY username might
        # have been escaped.
        JPY_BASE_USER_URL=without_end_slash(base_urlpath),
        # A unix username. used in the container to create the user.
        USER=_unix_user(user_name),
        # The identifier that will be used for the URL.
        URL_ID=url_id,
    ))
    return result


def _get_container_labels(user_name, mapping_id, url_id, urlpath, realm):
    """Returns a dictionary that will become container run-time labels.
    Each of these labels must be namespaced in reverse DNS style, in agreement
    to docker guidelines."""

    return {
        SIMPHONY_NS_RUNINFO.user: user_name,
        SIMPHONY_NS_RUNINFO.mapping_id: mapping_id,
        SIMPHONY_NS_RUNINFO.url_id: url_id,
        SIMPHONY_NS_RUNINFO.urlpath: urlpath,
        SIMPHONY_NS_RUNINFO.realm: realm
    }


def _generate_container_name(realm, user_name, mapping_id):
    """Generates a proper name for the container.
    It combines the prefix, username and image name after escaping.

    Parameters
    ----------
    realm : string
        The docker realm
    user_name: string
        the user name
    mapping_id: string
        the mapping id

    Return
    ------
    A string combining the three parameters in an appropriate container name,
    plus a random token to prevent collisions with a similarly named rogue
    container.

    NOTE: the container name is not meant for parsing. It's only for human
    consumption in the docker list. All information and all searching should
    be extracted from labels.
    """
    escaped_realm = escape(realm,
                           safe=_CONTAINER_SAFE_CHARS,
                           escape_char=_CONTAINER_ESCAPE_CHAR)
    escaped_user_name = escape(user_name,
                               safe=_CONTAINER_SAFE_CHARS,
                               escape_char=_CONTAINER_ESCAPE_CHAR)
    escaped_mapping_id = escape(mapping_id,
                                safe=_CONTAINER_SAFE_CHARS,
                                escape_char=_CONTAINER_ESCAPE_CHAR)
    random_token = ''.join(random.choice(string.ascii_lowercase)
                           for _ in range(10))

    return "{}-{}-{}-{}".format(escaped_realm,
                                escaped_user_name,
                                escaped_mapping_id,
                                random_token
                                )


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
