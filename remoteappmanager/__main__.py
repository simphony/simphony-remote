import sys

from remoteappmanager.command_line_config import CommandLineConfig
from remoteappmanager.file_config import FileConfig
from tornado.options import print_help
from traitlets import TraitError

from remoteappmanager.application import Application


def main():
    command_line_config = CommandLineConfig()

    try:
        command_line_config.parse_config()
    except TraitError:
        print_help()
        sys.exit(1)

    file_config = FileConfig()
    file_config.parse_config(command_line_config.config_file)

    app = Application(command_line_config, file_config)
    app.start()
