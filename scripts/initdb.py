import sys
from textwrap import dedent

from tornado.options import define, options, print_help

from remoteappmanager.db.orm import Database


def main():
    """
    Initializes the database at the appropriate url.
    Use this program only once, to create the common remoteappmanager.db
    """
    define("db_url",
           default="sqlite:///remoteappmanager.db",
           type=str,
           help="The database url")

    options.parse_command_line()

    db_url = options["db_url"]
    if db_url is None:
        print(dedent(main.__doc__))
        print_help()
        sys.exit(0)

    db = Database(url=db_url, echo=True)
    db.reset()

if __name__ == '__main__':
    main()
