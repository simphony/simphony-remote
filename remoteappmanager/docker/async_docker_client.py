from concurrent.futures import ThreadPoolExecutor

import docker
import functools

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

    def __init__(self, *args, **kwargs):
        """Initialises the docker async client.

        The client uses a single, module level executor to submit
        requests and obtain futures. The futures must be yielded
        according to the tornado asynchronous interface.

        The exported methods are the same as from the docker-py
        synchronous client, with the exception of their async nature.

        Note that the executor is a ThreadPoolExecutor with a single thread.
        """
        self._sync_client = docker.APIClient(*args, **kwargs)

    def __getattr__(self, attr):
        """Returns the docker client method, wrapped in an async execution
        environment. The returned method must be used in conjunction with
        the yield keyword."""
        if hasattr(self._sync_client, attr):
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
        m = getattr(self._sync_client, method)
        return m(*args, **kwargs)
