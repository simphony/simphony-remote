#!/usr/bin/env python
"""Script to perform operations on the database of our application."""
import os
import sys
from requests.exceptions import ConnectionError

import sqlalchemy.exc
import sqlalchemy.orm.exc
import click
import tabulate

from remoteappmanager.db import orm


def database(db_url):
    """Retrieves the orm.Database object from the
       passed db url. It also accepts absolute or relative disk paths.
       In that case, the database will be assumed to be a sqlite one.

    Parameters
    ----------
    db_url : str
        A string containing a db sqlalchemy url, or a disk path.

    Returns
    -------
    orm.Database instance.
    """
    if ":" not in db_url:
        db_url = "sqlite:///"+os.path.expanduser(db_url)
    else:
        db_url = db_url

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
        raise

    return client


@click.group()
@click.option("--db",
              type=click.STRING,
              help='The database sqlalchemy string to connect to, '
                   'or an absolute or relative disk path.',
              default="sqlite:///sqlite.db")
@click.pass_context
def cli(ctx, db):
    """Main click group placeholder."""
    ctx.obj["db"] = database(db)


@cli.command()
@click.pass_context
def init(ctx):
    """Initializes the database."""
    db = ctx.obj["db"]
    db.reset()

# -------------------------------------------------------------------------
# User commands


@cli.group()
def user():
    """Subcommand to manage users."""
    pass


@user.command()
@click.argument("user")
@click.pass_context
def create(ctx, user):
    """Creates a user USER in the database."""
    db = ctx.obj["db"]
    session = db.create_session()
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
def remove(ctx, user):
    """Removes a user."""
    db = ctx.obj["db"]
    session = db.create_session()

    try:
        with orm.transaction(session):
            orm_user = session.query(orm.User).filter(
                orm.User.name == user).one()

            # Unfortunately sqlite does not support cascading, so we need to
            # perform the cleanup of the accounting manually.
            session.query(orm.Accounting).filter(
                orm.Accounting.user == orm_user).delete()

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
def list(ctx, no_decoration, show_apps):
    """Show a list of the available users."""

    if no_decoration:
        format = "plain"
        headers = []
    else:
        format = "simple"
        headers = ["ID", "Name"]
        if show_apps:
            headers += ["App", "Home", "View", "Common", "Vol. Source",
                        "Vol. Target", "Vol. Mode"]

    db = ctx.obj["db"]
    session = db.create_session()

    table = []
    with orm.transaction(session):
        for user in session.query(orm.User).all():
            cur = [user.id, user.name]
            table.append(cur)
            if show_apps:
                apps = [[app.image,
                         policy.allow_home,
                         policy.allow_view,
                         policy.allow_common,
                         policy.volume_source,
                         policy.volume_target,
                         policy.volume_mode]
                        for _, app, policy in orm.apps_for_user(session, user)]

                if len(apps) == 0:
                    apps = [['']*7]

                cur.extend(apps[0])
                for app in apps[1:]:
                    table.append(['', ''] + app)

    print(tabulate.tabulate(table, headers=headers, tablefmt=format))

# -------------------------------------------------------------------------
# App commands


@cli.group()
def app():
    """Subcommand to manage applications."""
    pass


@app.command()  # noqa
@click.argument("image")
@click.option('--verify/--no-verify', default=True)
@click.pass_context
def create(ctx, image, verify):
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

    db = ctx.obj["db"]
    session = db.create_session()
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
def remove(ctx, image):
    """Removes an application from the list."""
    db = ctx.obj["db"]
    session = db.create_session()

    try:
        with orm.transaction(session):
            app = session.query(orm.Application).filter(
                orm.Application.image == image).one()

            session.query(orm.Accounting).filter(
                orm.Accounting.application_id == app.id).delete()
            session.delete(app)
    except sqlalchemy.orm.exc.NoResultFound:
        print_error("Could not find application for image {}".format(image))


@app.command()  # noqa
@click.option('--no-decoration', is_flag=True,
              help="Disable table decorations")
@click.pass_context
def list(ctx, no_decoration):
    """List all registered applications."""
    db = ctx.obj["db"]

    if no_decoration:
        tablefmt = "plain"
        headers = []
    else:
        tablefmt = "simple"
        headers = ["ID", "Image"]

    table = []
    session = db.create_session()
    with orm.transaction(session):
        for orm_app in session.query(orm.Application).all():
            table.append([orm_app.id, orm_app.image])

    print(tabulate.tabulate(table, headers=headers, tablefmt=tablefmt))


@app.command()
@click.argument("image")
@click.argument("user")
@click.option("--allow-home",
              is_flag=True,
              help="Enable mounting of home directory")
@click.option("--allow-view",
              is_flag=True,
              help="Enable third-party visibility of the running container.")
@click.option("--volume", type=click.STRING,
              help="Application data volume, format=SOURCE:TARGET:MODE, "
                   "where mode is 'ro' or 'rw'.")
@click.pass_context
def grant(ctx, image, user, allow_home, allow_view, volume):
    """Grants access to application identified by IMAGE to a specific
    user USER and specified access policy."""
    db = ctx.obj["db"]
    allow_common = False
    source = target = mode = None

    if volume is not None:
        allow_common = True
        source, target, mode = _parse_volume_string(volume)

    session = db.create_session()
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
            orm.ApplicationPolicy.allow_home == allow_home,
            orm.ApplicationPolicy.allow_common == allow_common,
            orm.ApplicationPolicy.allow_view == allow_view,
            orm.ApplicationPolicy.volume_source == source,
            orm.ApplicationPolicy.volume_target == target,
            orm.ApplicationPolicy.volume_mode == mode).one_or_none()

        if orm_policy is None:
            orm_policy = orm.ApplicationPolicy(
                allow_home=allow_home,
                allow_common=allow_common,
                allow_view=allow_view,
                volume_source=source,
                volume_target=target,
                volume_mode=mode,
            )
            session.add(orm_policy)

        # Check if we already have the entry
        acc = session.query(orm.Accounting).filter(
            orm.Accounting.user == orm_user,
            orm.Accounting.application == orm_app,
            orm.Accounting.application_policy == orm_policy
        ).one_or_none()

        if acc is None:
            accounting = orm.Accounting(
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
@click.pass_context
def revoke(ctx, image, user, revoke_all, allow_home, allow_view, volume):
    """Revokes access to application identified by IMAGE to a specific
    user USER and specified parameters."""
    db = ctx.obj["db"]

    allow_common = False
    source = target = mode = None

    if volume is not None:
        allow_common = True
        source, target, mode = _parse_volume_string(volume)

    session = db.create_session()
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
                orm.ApplicationPolicy.allow_home == allow_home,
                orm.ApplicationPolicy.allow_common == allow_common,
                orm.ApplicationPolicy.allow_view == allow_view,
                orm.ApplicationPolicy.volume_source == source,
                orm.ApplicationPolicy.volume_target == target,
                orm.ApplicationPolicy.volume_mode == mode).one()

            session.query(orm.Accounting).filter(
                orm.Accounting.application == orm_app,
                orm.Accounting.user == orm_user,
                orm.Accounting.application_policy == orm_policy,
            ).delete()


def main():
    cli(obj={})


def _parse_volume_string(volume_string):
    """Parses a volume specification string SOURCE:TARGET:MODE into
    its components, or raises click.BadOptionUsage if not according
    to format."""
    try:
        source, target, mode = volume_string.split(":")
    except ValueError:
        raise click.BadOptionUsage(
            "volume",
            "Volume string must be in the form source:target:mode")

    if mode not in ('rw', 'ro'):
        raise click.BadOptionUsage(
            "volume",
            "Volume mode must be either 'ro' or 'rw'")

    return source, target, mode

if __name__ == '__main__':
    main()
