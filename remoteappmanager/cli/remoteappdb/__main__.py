#!/usr/bin/env python
"""Script to perform operations on the database of our application."""
import os
import sys
import uuid
from requests.exceptions import ConnectionError

import sqlalchemy.exc
import sqlalchemy.orm.exc
import click
import tabulate

from remoteappmanager.db import orm
from remoteappmanager.utils import parse_volume_string


def sqlite_url_to_path(url):
    """Converts a sqlalchemy sqlite url to the disk path.

    Parameters
    ----------
    url: str
        A "sqlite:///" path

    Returns
    -------
    str:
        The disk path.
    """
    if not url.startswith("sqlite:///"):
        raise ValueError("Cannot find sqlite")
    return url[len("sqlite:///"):]


def normalise_to_url(url_or_path):
    """Normalises a disk path to a sqlalchemy url

    Parameters
    ----------
    url_or_path: str
        a sqlalchemy url or a disk path

    Returns
    -------
    str
        A sqlalchemy url
    """
    if ":" not in url_or_path:
        db_url = "sqlite:///"+os.path.expanduser(url_or_path)
    else:
        db_url = url_or_path

    return db_url


def database(db_url):
    """Retrieves the orm.Database object from the passed db url.

    Parameters
    ----------
    db_url : str
        A string containing a db sqlalchemy url.

    Returns
    -------
    orm.Database instance.
    """
    return orm.Database(url=db_url)


def print_error(error):
    """Prints an error message to stderr"""
    print("Error: {}".format(error), file=sys.stderr)


def get_docker_client():
    """ Returns docker.client object using the local environment variables
    """
    # dependencies of docker-py is optional for this script
    try:
        import docker
    except ImportError:
        print_error('docker-py is not installed. '
                    'Try pip install docker-py')
        raise

    client = docker.from_env()
    try:
        client.info()
    except ConnectionError as exception:
        # ConnectionError occurs, say, if the docker machine is not running
        # or if the shell is not in a docker VM (for Mac/Windows)
        print_error('docker client fails to connect.')
        raise exception

    return client


def is_sqlitedb_url(db_url):
    """Returns True if the url refers to a sqlite database"""
    return db_url.startswith("sqlite:///")


def sqlitedb_present(db_url):
    """Checks if the db url is present.
    Remote urls are always assumed to be present, so this method
    concerns mostly sqlite databases."""

    if not db_url.startswith("sqlite:///"):
        raise ValueError("db_url {} does not refer to a "
                         "sqlite database.".format(db_url))

    path = sqlite_url_to_path(db_url)
    return os.path.exists(path)


class RemoteAppDBContext(object):
    def __init__(self, db_url):
        db_url = normalise_to_url(db_url)
        self.db = database(db_url)


@click.group()
@click.argument("db",
                type=click.STRING,
                default="sqlite:///sqlite.db")
@click.pass_context
def cli(ctx, db):
    """Remote application database manager.
    Performs administrative operations on the database contents."""
    ctx.obj = RemoteAppDBContext(db_url=db)
    ctx.obj.session = ctx.obj.db.create_session()

    @ctx.call_on_close
    def close_session():
        ctx.obj.session.close()


@cli.command()
@click.pass_context
def init(ctx):
    """Initializes the database."""
    db = ctx.obj.db
    db_url = db.url

    # Check if the database already exists
    if is_sqlitedb_url(db_url) and sqlitedb_present(db_url):
        raise click.UsageError("Refusing to overwrite database "
                               "at {}".format(db_url))
    db.reset()


# -------------------------------------------------------------------------
# User commands


@cli.group()
@click.pass_context
def user(ctx):
    """Subcommand to manage users."""
    db = ctx.obj.db
    db_url = db.url

    # sqlite driver for sqlalchemy creates an empty file on commit as a side
    # effect. We don't want this creation to happen, so before attempting
    # the creation we stop short if we already find out that the file is
    # missing and cannot possibly be initialized.
    if is_sqlitedb_url(db_url) and not sqlitedb_present(db_url):
        raise click.UsageError("Could not find database at {}".format(db_url))


@user.command()
@click.argument("user")
@click.pass_context
def create(ctx, user):  # noqa: F811
    """Creates a user USER in the database."""
    session = ctx.obj.session
    orm_user = orm.User(name=user)

    try:
        with orm.transaction(session):
            session.add(orm_user)
    except sqlalchemy.exc.IntegrityError:
        print_error("User {} already exists".format(user))
    else:
        # Print out the id, so that we can use it if desired.
        print(orm_user.id)


@user.command()
@click.argument("user")
@click.pass_context
def remove(ctx, user):  # noqa: F811
    """Removes a user."""
    session = ctx.obj.session

    try:
        with orm.transaction(session):
            orm_user = session.query(orm.User).filter(
                orm.User.name == user).one()

            session.delete(orm_user)

    except sqlalchemy.orm.exc.NoResultFound:
        print_error("Could not find user {}".format(user))


@user.command()
@click.option('--no-decoration', is_flag=True,
              help="Disable table decorations")
@click.option('--show-apps', is_flag=True,
              help="Shows the applications each user "
                   "is allowed to run")
@click.pass_context
def list(ctx, no_decoration, show_apps):  # noqa: F811
    """Show a list of the available users."""

    if no_decoration:
        format = "plain"
        headers = []
    else:
        format = "simple"
        headers = ["ID", "Name"]
        if show_apps:
            headers += ["App", "License", "Home", "View", "Common",
                        "Vol. Source", "Vol. Target", "Vol. Mode",
                        "Allow Startup Data"]

    session = ctx.obj.session

    table = []
    with orm.transaction(session):
        for user in session.query(orm.User).all():
            cur = [user.id, user.name]
            table.append(cur)
            if show_apps:
                apps = [[entry.application.image,
                         entry.application_policy.app_license,
                         entry.application_policy.allow_home,
                         entry.application_policy.allow_view,
                         entry.application_policy.allow_common,
                         entry.application_policy.volume_source,
                         entry.application_policy.volume_target,
                         entry.application_policy.volume_mode,
                         entry.application_policy.allow_startup_data]
                        for entry in orm.accounting_for_user(session, user)]

                if len(apps) == 0:
                    apps = [['']*8]

                cur.extend(apps[0])
                for app in apps[1:]:
                    table.append(['', ''] + app)

    print(tabulate.tabulate(table, headers=headers, tablefmt=format))

# -------------------------------------------------------------------------
# App commands


@cli.group()
@click.pass_context
def app(ctx):
    """Subcommand to manage applications."""
    db = ctx.obj.db
    db_url = db.url

    if is_sqlitedb_url(db_url) and not sqlitedb_present(db_url):
        raise click.UsageError("Could not find database at {}".format(db_url))


@app.command()  # noqa
@click.argument("image")
@click.option('--verify/--no-verify',
              default=True,
              help="Verify image name against docker.")
@click.pass_context
def create(ctx, image, verify):  # noqa: F811
    """Creates a new application for image IMAGE."""

    # Verify if `image` is an existing docker image
    # in this machine
    if verify:
        msg = ('{error}. You may consider skipping verifying '
               'image name against docker with --no-verify.')
        try:
            client = get_docker_client()
            client.inspect_image(image)
        except Exception as exception:
            raise click.BadParameter(msg.format(error=str(exception)),
                                     ctx=ctx)

    session = ctx.obj.session
    try:
        with orm.transaction(session):
            orm_app = orm.Application(image=image)
            session.add(orm_app)
    except sqlalchemy.exc.IntegrityError:
        print_error("Application for image {} already exists".format(image))
    else:
        print(orm_app.id)


@app.command()  # noqa
@click.argument("image")
@click.pass_context
def remove(ctx, image):  # noqa: F811
    """Removes an application from the list."""
    session = ctx.obj.session

    try:
        with orm.transaction(session):
            app = session.query(orm.Application).filter(
                orm.Application.image == image).one()

            session.delete(app)
    except sqlalchemy.orm.exc.NoResultFound:
        print_error("Could not find application for image {}".format(image))


@app.command()  # noqa
@click.option('--no-decoration', is_flag=True,
              help="Disable table decorations")
@click.pass_context
def list(ctx, no_decoration):  # noqa: F811
    """List all registered applications."""
    if no_decoration:
        tablefmt = "plain"
        headers = []
    else:
        tablefmt = "simple"
        headers = ["ID", "Image"]

    table = []
    session = ctx.obj.session
    with orm.transaction(session):
        for orm_app in session.query(orm.Application).all():
            table.append([orm_app.id, orm_app.image])

    print(tabulate.tabulate(table, headers=headers, tablefmt=tablefmt))


@app.command()
@click.argument("image")
@click.argument("user")
@click.option("--app_license", type=click.STRING,
              help="Application license (if required)")
@click.option("--allow-home",
              is_flag=True,
              help="Enable mounting of home directory")
@click.option("--allow-view",
              is_flag=True,
              help="Enable third-party visibility of the running container.")
@click.option("--volume", type=click.STRING,
              help="Application data volume, format=SOURCE:TARGET:MODE, "
                   "where mode is 'ro' or 'rw'.")
@click.option("--allow-startup-data",
              is_flag=True,
              help="Allow user to provide a file for the container to load"
                   "at startup.")
@click.pass_context
def grant(ctx, image, user, app_license, allow_home, allow_view, volume,
          allow_startup_data):
    """Grants access to application identified by IMAGE to a specific
    user USER and specified access policy."""
    allow_common = False
    source = target = mode = None

    if volume is not None:
        allow_common = True
        try:
            source, target, mode = parse_volume_string(volume)
        except ValueError as e:
            raise click.BadOptionUsage("volume", str(e))

    session = ctx.obj.session
    with orm.transaction(session):
        orm_app = session.query(orm.Application).filter(
            orm.Application.image == image).one_or_none()

        if orm_app is None:
            raise click.BadParameter("Unknown application image {}".format(
                image), param_hint="image")

        orm_user = session.query(orm.User).filter(
            orm.User.name == user).one_or_none()

        if orm_user is None:
            raise click.BadParameter("Unknown user {}".format(user),
                                     param_hint="user")

        orm_policy = session.query(orm.ApplicationPolicy).filter(
            orm.ApplicationPolicy.app_license == app_license,
            orm.ApplicationPolicy.allow_home == allow_home,
            orm.ApplicationPolicy.allow_common == allow_common,
            orm.ApplicationPolicy.allow_view == allow_view,
            orm.ApplicationPolicy.volume_source == source,
            orm.ApplicationPolicy.volume_target == target,
            orm.ApplicationPolicy.volume_mode == mode,
            orm.ApplicationPolicy.allow_startup_data == allow_startup_data
        ).one_or_none()

        if orm_policy is None:
            orm_policy = orm.ApplicationPolicy(
                app_license=app_license,
                allow_home=allow_home,
                allow_common=allow_common,
                allow_view=allow_view,
                volume_source=source,
                volume_target=target,
                volume_mode=mode,
                allow_startup_data=allow_startup_data,
            )
            session.add(orm_policy)

        # Check if we already have the entry
        acc = session.query(orm.Accounting).filter(
            orm.Accounting.user == orm_user,
            orm.Accounting.application == orm_app,
            orm.Accounting.application_policy == orm_policy
        ).one_or_none()

        if acc is None:
            id = uuid.uuid4().hex
            accounting = orm.Accounting(
                id=id,
                user=orm_user,
                application=orm_app,
                application_policy=orm_policy,
            )
            session.add(accounting)


@app.command()
@click.argument("image")
@click.argument("user")
@click.option("--revoke-all",
              is_flag=True,
              help="revoke all grants for that specific user and application, "
                   "regardless of policy.")
@click.option("--app_license", type=click.STRING,
              help="Application license (if required)")
@click.option("--allow-home",
              is_flag=True,
              help="Policy for mounting of home directory")
@click.option("--allow-view",
              is_flag=True,
              help="Policy for third-party visibility "
                   "of the running container.")
@click.option("--volume", type=click.STRING,
              help="Application data volume, format=SOURCE:TARGET:MODE, "
                   "where mode is 'ro' or 'rw'.")
@click.option("--allow-startup-data",
              is_flag=True,
              help="Allow user to provide a file for the container to load"
                   "at startup.")
@click.pass_context
def revoke(
        ctx, image, user, revoke_all, app_license,
        allow_home, allow_view, volume, allow_startup_data):
    """Revokes access to application identified by IMAGE to a specific
    user USER and specified parameters."""
    allow_common = False
    source = target = mode = None

    if volume is not None:
        allow_common = True
        try:
            source, target, mode = parse_volume_string(volume)
        except ValueError as e:
            raise click.BadOptionUsage("volume", str(e))

    session = ctx.obj.session
    with orm.transaction(session):
        orm_app = session.query(orm.Application).filter(
            orm.Application.image == image).one()

        orm_user = session.query(orm.User).filter(
            orm.User.name == user).one()

        if revoke_all:
            session.query(orm.Accounting).filter(
                orm.Accounting.application == orm_app,
                orm.Accounting.user == orm_user,
                ).delete()

        else:
            orm_policy = session.query(orm.ApplicationPolicy).filter(
                orm.ApplicationPolicy.app_license == app_license,
                orm.ApplicationPolicy.allow_home == allow_home,
                orm.ApplicationPolicy.allow_common == allow_common,
                orm.ApplicationPolicy.allow_view == allow_view,
                orm.ApplicationPolicy.volume_source == source,
                orm.ApplicationPolicy.volume_target == target,
                orm.ApplicationPolicy.volume_mode == mode,
                orm.ApplicationPolicy.allow_startup_data == allow_startup_data
            ).one()

            session.query(orm.Accounting).filter(
                orm.Accounting.application == orm_app,
                orm.Accounting.user == orm_user,
                orm.Accounting.application_policy == orm_policy,
            ).delete()


def main():
    cli(obj={})


if __name__ == '__main__':
    main()
