import click
from remoteappmanager.db import orm


def database(db):
    if ":" not in db:
        db_url = "sqlite:///"+db
    else:
        db_url = db

    return orm.Database(url=db_url)


@click.group()
def cli():
    pass


@cli.command()
@click.option("--db", type=click.STRING, default="sqlite:///sqlite.db")
def init(db):
    db_obj = database(db)
    db_obj.reset()


@cli.group()
def user():
    pass


@cli.group()
def team():
    pass


@cli.group()
def app():
    pass


@user.command()
@click.argument("user")
@click.option("--db", type=click.STRING, default="sqlite:///sqlite.db")
def create(user, db):
    db_obj = database(db)
    session = db_obj.create_session()
    orm_user = orm.User(name=user)
    orm_team = orm.Team(name=user)
    orm_user.teams.append(orm_team)
    with orm.transaction(session):
        session.add(orm_user)
        session.add(orm_team)

    print(orm_user.id)


@user.command()
@click.option("--db", type=click.STRING, default="sqlite:///sqlite.db")
def list(db):
    db_obj = database(db)
    session = db_obj.create_session()
    with orm.transaction(session):
        for user in session.query(orm.User).all():
            teams = ["{}:{}".format(t.id, t.name) for t in user.teams]
            apps = orm.apps_for_user(session, user)
            for app, policy in apps:
                appstring = "{} {} {} {}".format(app.image,
                                                 policy.volume_source,
                                                 policy.volume_target,
                                                 policy.volume_mode)
                print("{}:{} | {} | {}".format(
                    user.id,
                    user.name,
                    ",".join(teams),
                    appstring
                    ))



@team.command()
@click.argument("team")
@click.option("--db", type=click.STRING, default="sqlite:///sqlite.db")
def create(team, db):
    db_obj = database(db)
    session = db_obj.create_session()
    orm_team = orm.Team(name=team)
    with orm.transaction(session):
        session.add(orm_team)

    print(orm_team.id)


@team.command()
@click.option("--db", type=click.STRING, default="sqlite:///sqlite.db")
def list(db):
    db_obj = database(db)
    session = db_obj.create_session()
    with orm.transaction(session):
        for team in session.query(orm.Team).all():
            print("{}:{}".format(team.id, team.name))


@team.command()
@click.argument("user")
@click.argument("team")
@click.option("--db", type=click.STRING, default="sqlite:///sqlite.db")
def adduser(user, team, db):
    db_obj = database(db)
    session = db_obj.create_session()
    with orm.transaction(session):
        orm_team = session.query(orm.Team).filter(
            orm.Team.name == team).first()
        orm_user = session.query(orm.User).filter(
            orm.User.name == user).first()
        orm_team.users.append(orm_user)


@app.command()
@click.argument("image")
@click.option("--db", type=click.STRING, default="sqlite:///sqlite.db")
def create(image, db):
    db_obj = database(db)
    session = db_obj.create_session()
    with orm.transaction(session):
        orm_app = orm.Application(image=image)
        session.add(orm_app)

    print(orm_app.id)


@app.command()
@click.option("--db", type=click.STRING, default="sqlite:///sqlite.db")
def list(db):
    db_obj = database(db)
    session = db_obj.create_session()
    with orm.transaction(session):
        for orm_app in session.query(orm.Application).all():
            print("{}:{}".format(orm_app.id, orm_app.image))


@app.command()
@click.argument("image")
@click.argument("team")
@click.option("--db", type=click.STRING, default="sqlite:///sqlite.db")
@click.option("--allow-home", type=click.BOOL, default=False)
@click.option("--allow-team-view", type=click.BOOL, default=False)
@click.option("--volume", type=click.STRING)
def expose(image, team, db, allow_home, allow_team_view, volume):

    allow_common = False
    source = target = mode = None

    if volume is not None:
        allow_common = True
        source, target, mode = volume.split(":")

    db_obj = database(db)
    session = db_obj.create_session()
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
    cli()
