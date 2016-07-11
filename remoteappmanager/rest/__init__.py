from remoteappmanager.rest.rest_handler import RESTItemHandler, \
    RESTCollectionHandler
from remoteappmanager.utils import url_path_join


def api_handlers(base_url, version="v1"):
    return [
        (url_path_join(base_url, "api", version, "(.*)", "(.*)"),
         RESTItemHandler
         ),
        (url_path_join(base_url, "api", version, "(.*)"),
         RESTCollectionHandler
         ),
        ]
