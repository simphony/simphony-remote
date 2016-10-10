import sys   # pragma: no cover

from remoteappmanager.command_line_config import (
    CommandLineConfig)   # pragma: no cover
from remoteappmanager.environment_config import (
    EnvironmentConfig)  # pragma: no cover
from remoteappmanager.file_config import FileConfig   # pragma: no cover
from tornado.options import print_help   # pragma: no cover

from remoteappmanager.admin_application import (
    AdminApplication)  # pragma: no cover


def main():    # pragma: no cover
    try:
        command_line_config = CommandLineConfig()
        command_line_config.parse_config()
        file_config = FileConfig()

        if command_line_config.config_file:
            file_config.parse_config(command_line_config.config_file)

        environment_config = EnvironmentConfig()
        environment_config.parse_config()

    except Exception as e:
        print_help()
        print("Error: {}".format(e))
        sys.exit(1)

    app = AdminApplication(
        command_line_config,
        file_config,
        environment_config)

    app.start()
