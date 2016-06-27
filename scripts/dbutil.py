#!/usr/bin/env python
"""Script to perform operations on the database of our application."""
import click
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
        db_url = "sqlite:///"+db_url
    else:
        db_url = db_url

    return orm.Database(url=db_url)


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
    """Creates a user USER and its associated team in the database."""
    db = ctx.obj["db"]
    session = db.create_session()
    orm_user = orm.User(name=user)
    orm_team = orm.Team(name=user)
    orm_user.teams.append(orm_team)

    with orm.transaction(session):
        session.add(orm_user)
        session.add(orm_team)

    # Print out the id, so that we can use it if desired.
    print(orm_user.id)


@user.command()
@click.pass_context
def list(ctx):
    """Show a list of the available users."""
    db = ctx.obj["db"]
    session = db.create_session()
    with orm.transaction(session):
        for user in session.query(orm.User).all():
            teams = ["{}:{}".format(t.id, t.name) for t in user.teams]
            apps = ["{} {} {} {}".format(app.image,
                                         policy.volume_source,
                                         policy.volume_target,
                                         policy.volume_mode)
                    for app, policy in orm.apps_for_user(session, user)]

            print("{}:{} | {} | {}".format(
                user.id,
                user.name,
                ",".join(teams),
                ",".join(apps)
            ))


# -------------------------------------------------------------------------
# Team commands


@cli.group()
def team():
    """Subcommand to manage teams."""
    pass


@team.command()  # noqa
@click.argument("team")
@click.pass_context
def create(ctx, team):
    """Creates a new team TEAM."""
    db = ctx.obj["db"]
    session = db.create_session()
    orm_team = orm.Team(name=team)
    with orm.transaction(session):
        session.add(orm_team)

    print(orm_team.id)


@team.command()  # noqa
@click.pass_context
def list(ctx):
    """Show the current teams."""
    db = ctx.obj["db"]
    session = db.create_session()
    with orm.transaction(session):
        for team in session.query(orm.Team).all():
            print("{}:{}".format(team.id, team.name))


@team.command()
@click.argument("user")
@click.argument("team")
@click.pass_context
def adduser(ctx, user, team):
    """Add a user USER to a team TEAM."""
    db = ctx.obj["db"]
    session = db.create_session()
    with orm.transaction(session):
        orm_team = session.query(orm.Team).filter(
            orm.Team.name == team).first()
        orm_user = session.query(orm.User).filter(
            orm.User.name == user).first()
        orm_team.users.append(orm_user)

# -------------------------------------------------------------------------
# App commands


@cli.group()
def app():
    """Subcommand to manage applications."""
    pass


@app.command()  # noqa
@click.argument("image")
@click.pass_context
def create(ctx, image):
    """Creates a new application for image IMAGE."""
    db = ctx.obj["db"]
    session = db.create_session()
    with orm.transaction(session):
        orm_app = orm.Application(image=image)
        session.add(orm_app)

    print(orm_app.id)


@app.command()  # noqa
@click.pass_context
def list(ctx):
    """List all registered applications."""
    db = ctx.obj["db"]
    session = db.create_session()
    with orm.transaction(session):
        for orm_app in session.query(orm.Application).all():
            print("{}:{}".format(orm_app.id, orm_app.image))


@app.command()
@click.argument("image")
@click.argument("team")
@click.option("--allow-home", type=click.BOOL, default=False)
@click.option("--allow-team-view", type=click.BOOL, default=False)
@click.option("--volume", type=click.STRING)
@click.pass_context
def expose(ctx, image, team, db, allow_home, allow_team_view, volume):
    """Exposes a given application identified by IMAGE to a specific
    team TEAM."""
    db = ctx.obj["db"]
    allow_common = False
    source = target = mode = None

    if volume is not None:
        allow_common = True
        try:
            source, target, mode = volume.split(":")
        except ValueError:
            raise click.BadOptionUsage(
                "volume",
                "Volume string must be in the form source:target:mode")

        if mode not in ('rw', 'ro'):
            raise click.BadOptionUsage(
                "volume",
                "Volume mode must be either 'ro' or 'rw'")

    session = db.create_session()
    with orm.transaction(session):
        orm_app = session.query(orm.Application).filter(
            orm.Application.image == image).first()
        orm_team = session.query(orm.Team).filter(
            orm.Team.name == team).first()

        orm_policy = orm.ApplicationPolicy(
            allow_home=allow_home,
            allow_common=allow_common,
            allow_team_view=allow_team_view,
            volume_source=source,
            volume_target=target,
            volume_mode=mode,
        )

        session.add(orm_policy)

        accounting = orm.Accounting(
            team=orm_team,
            application=orm_app,
            application_policy=orm_policy,
        )

        session.add(accounting)


if __name__ == '__main__':
    cli(obj={})
