import os
import sys

from tornado.options import print_help
from traitlets import TraitError

from remoteappmanager.application import Application
from remoteappmanager.application_config import ApplicationConfig


def main():
    config = ApplicationConfig()

    try:
        config.parse_config()
    except TraitError:
        print_help()
        sys.exit(1)

    config.hub_api_key = os.environ.pop('JPY_API_TOKEN')
    app = Application(config)
    app.start()
