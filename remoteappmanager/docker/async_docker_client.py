from concurrent.futures import ThreadPoolExecutor

import docker
import functools
from docker.utils import kwargs_from_env

# Common threaded executor for asynchronous jobs.
# Required for the AsyncDockerClient to operate.
_executor = ThreadPoolExecutor(1)


class AsyncDockerClient:
    """Provides an asynchronous interface to dockerpy.
    All Client interface is available as methods returning a future
    instead of the actual result. The resulting future can be yielded.

    This class is thread safe. Note that all instances use the same
    executor.
    """

    def __init__(self, config=None, *args, **kwargs):
        """Initialises the docker async client.

        The client uses a single, module level executor to submit
        requests and obtain futures. The futures must be yielded
        according to the tornado asynchronous interface.

        The exported methods are the same as from the docker-py
        synchronous client, with the exception of their async nature.

        Note that the executor is a ThreadPoolExecutor with a single thread.
        """
        self.config = config
        self.client = None

        super().__init__(*args, **kwargs)

    def _init_client(self):
        """Returns the docker-py synchronous client instance."""
        config = self.config

        # If there is no configuration, we try to obtain it
        # from the envvars
        if config is None:
            kwargs = kwargs_from_env()
            client = docker.Client(version='auto', **kwargs)
        else:
            if config.tls:
                tls_config = True
            elif config.tls_verify or config.tls_ca or config.tls_client:
                tls_config = docker.tls.TLSConfig(
                    client_cert=config.tls_client,
                    ca_cert=config.tls_ca,
                    verify=config.tls_verify,
                    assert_hostname=config.tls_assert_hostname)
            else:
                tls_config = None

            if len(config.docker_host) == 0:
                docker_host = 'unix://var/run/docker.sock'
            else:
                docker_host = config.docker_host

            client = docker.Client(base_url=docker_host,
                                   tls=tls_config,
                                   version='auto')
        self.client = client

    def __getattr__(self, attr):
        """Returns the docker client method, wrapped in an async execution
        environment. The returned method must be used in conjunction with
        the yield keyword."""
        if self.client is None:
            self._init_client()

        if hasattr(self.client, attr):
            return functools.partial(self._submit_to_executor, attr)
        else:
            raise AttributeError(
                "'{}' object has no attribute '{}'".format(
                    type(self).__name__,
                    attr
                )
            )

    # Private

    def _submit_to_executor(self, method, *args, **kwargs):
        """Call a synchronous docker client method in a background thread,
        using the module level executor.

        Parameters
        ----------

        method : string
            A string containing a callable method
        *args, *kwargs:
            Arguments to the invoked method

        Return
        ------

        A future from the ThreadPoolExecutor.
        """
        return _executor.submit(self._invoke, method, *args, **kwargs)

    def _invoke(self, method, *args, **kwargs):
        """wrapper for calling docker methods to be passed to
        ThreadPoolExecutor.
        """
        m = getattr(self.client, method)
        return m(*args, **kwargs)
