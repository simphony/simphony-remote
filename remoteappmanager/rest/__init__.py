from remoteappmanager.rest.rest_handler import RESTResourceHandler, \
    RESTCollectionHandler
from remoteappmanager.utils import url_path_join, with_end_slash


def api_handlers(base_urlpath, version="v1"):
    """Returns the API handlers for the REST interface.
    Add these handlers to your application to provide a
    REST interface to your Resources.


    Parameters
    ----------
    base_urlpath: str
        The base url path to serve
    version: str
        A string identifying the version of the API.

    Notes
    -----
    The current implementation does not support multiple API versions yet.
    The version option is only provided for futureproofing.
    """
    return [
        (with_end_slash(
            url_path_join(base_urlpath, "api", version, "(.*)", "(.*)")),
         RESTResourceHandler
         ),
        (with_end_slash(
            url_path_join(base_urlpath, "api", version, "(.*)")),
         RESTCollectionHandler
         ),
        ]
