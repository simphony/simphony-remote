import socket
import errno

from tornado import gen, ioloop
from tornado.httpclient import AsyncHTTPClient, HTTPError
from tornado.log import app_log


@gen.coroutine
def wait_for_http_server_2xx(url, timeout=10):
    """Wait for an HTTP Server to respond at url and respond with a 2xx code.
    """
    loop = ioloop.IOLoop.current()
    tic = loop.time()
    client = AsyncHTTPClient()

    while loop.time() - tic < timeout:
        try:
            response = yield client.fetch(url, follow_redirects=True)
        except HTTPError as e:
            # Skip code 599 because it's expected and we don't want to
            # pollute the logs.
            if e.code != 599:
                app_log.warning("Server at %s responded with: %s", url, e.code)
        except (OSError, socket.error) as e:
            if e.errno not in {errno.ECONNABORTED,
                               errno.ECONNREFUSED,
                               errno.ECONNRESET}:
                app_log.warning("Failed to connect to %s (%s)", url, e)
        except Exception as e:
            # In case of any unexpected exception, we just log it and keep
            # trying until eventually we timeout.
            app_log.warning("Unknown exception occurred connecting to "
                            "%s (%s)", url, e)
        else:
            app_log.info("Server at %s responded with: %s", url, response.code)
            return

        print("round")
        yield gen.sleep(0.1)

    raise TimeoutError("Server at {} didn't respond in {} seconds".format(
        url, timeout))
