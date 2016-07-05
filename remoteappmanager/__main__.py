import sys

from remoteappmanager.command_line_config import CommandLineConfig
from remoteappmanager.file_config import FileConfig
from tornado.options import print_help

from remoteappmanager.application import Application


def main():
    command_line_config = CommandLineConfig()

    try:
        command_line_config.parse_config()
        file_config = FileConfig()
        file_config.parse_config(command_line_config.config_file)
    except Exception as e:
        print_help()
        print("Error: {}".format(e))
        sys.exit(1)

    app = Application(command_line_config, file_config)
    app.start()
