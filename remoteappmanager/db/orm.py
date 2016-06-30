import contextlib

from sqlalchemy import (
    Column, Integer, Boolean, Unicode, ForeignKey, create_engine, Enum)
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from remoteappmanager.logging.logging_mixin import LoggingMixin

Base = declarative_base()


class IdMixin(object):
    """Base class to provide an id"""
    id = Column(Integer, primary_key=True)

    @classmethod
    def from_id(cls, session, id):
        return session.query(cls).filter(cls.id == id).one()


class UserTeam(Base):
    """ The user (n <-> n) team association table """
    __tablename__ = "user_team"
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    team_id = Column(Integer, ForeignKey('team.id'), primary_key=True)


class User(IdMixin, Base):
    """ Table for users. """
    __tablename__ = "user"

    #: The name of the user as specified by jupyterhub.
    #: This entry must be unique and is, for all practical purposes,
    #: a primary key.
    name = Column(Unicode, index=True, unique=True)


class Team(IdMixin, Base):
    """ Teams of users. """
    __tablename__ = "team"

    #: The name of the group. Note that, differently from users, we can have
    #: multiple teams with the same name. The reason is that we would obtain
    #: unusual behavior if user A creates a group with name B, and then B
    #: creates a user. Users are automatically assigned a group with their
    #: own name when first created.
    name = Column(Unicode)

    #: The users parts of this team (n <-> n)
    users = relationship("User", secondary="user_team", backref="teams")


class Application(IdMixin, Base):
    """ Describes an application that should be available for startup """
    __tablename__ = "application"

    #: The docker image name where the application can be found
    image = Column(Unicode, unique=True)

    @staticmethod
    def from_image_name(session, image_name):
        return session.query(Application).filter(
            Application.image == image_name
        ).one()


class ApplicationPolicy(IdMixin, Base):
    __tablename__ = "application_policy"
    #: If the home directory should be mounted in the container
    allow_home = Column(Boolean)

    #: If a common workarea should be mounted in the container
    allow_common = Column(Boolean)

    #: If the container should be accessible from other members of the team
    allow_team_view = Column(Boolean)

    # Which volume to mount
    volume_source = Column(Unicode, nullable=True)

    # Where to mount it in the container
    volume_target = Column(Unicode, nullable=True)

    # In which mode
    volume_mode = Column(Enum("ro", "rw"), nullable=True)


class Accounting(Base):
    """Holds the information about who is allowed to run what."""
    __tablename__ = "accounting"

    team_id = Column(Integer,
                     ForeignKey("team.id"),
                     primary_key=True)

    application_id = Column(Integer,
                            ForeignKey("application.id"),
                            primary_key=True)

    application_policy_id = Column(Integer,
                                   ForeignKey("application_policy.id"),
                                   primary_key=True)

    team = relationship("Team")

    application = relationship("Application")

    application_policy = relationship("ApplicationPolicy")


class Database(LoggingMixin):
    def __init__(self, url, **kwargs):
        """Initialises a database connection to a given database url.

        Parameters
        ----------
        url : url
            A sqlalchemy url to connect to a specified database.
        **kwargs : dict
            Additional keys will be passed at create_engine.
        """
        super().__init__()

        self.url = url

        self.log.info("Creating session to db: {}".format(self.url))
        self.engine = create_engine(self.url, **kwargs)
        try:
            self.session_class = sessionmaker(bind=self.engine)
        except OperationalError:
            self.log.exception(
                "Failed to connect db session: {}".format(self.url)
            )
            raise

    def create_session(self):
        """Create a new session class at the database url with the current
        engine.
        """
        return self.session_class()

    def reset(self):
        """Completely resets the content of the database, removing
        and reinitializing the tables. Should be used only if the database
        does not already exist, or if its contents are irrelevant or obsolete.
        """
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)


@contextlib.contextmanager
def transaction(session):
    """handles a transaction in a session."""
    # Note that we don't need to explicitly start the session
    # transaction. we are not using autocommit.
    try:
        yield
    except Exception:
        session.rollback()
        raise
    finally:
        session.commit()


def apps_for_user(session, user):
    """Returns a list of tuples, each containing an application and the
    associated policy that the specified orm user is allowed to run.
    If the user is None, the default is to return an empty list.
    The mapping_id is a unique string identifying the combination of
    application and policy. It is not unique per user.

    Parameters
    ----------
    session : Session
        The current session
    user : User
        the orm User, or None.

    Returns
    -------
    A list of tuples (mapping_id, orm.Application, orm.ApplicationPolicy)
    """

    if user is None:
        return []

    teams = user.teams

    res = session.query(Accounting).filter(
        Accounting.team_id.in_([team.id for team in teams])).all()

    return [(acc.application.image + "_" + str(acc.application_policy.id),
             acc.application,
             acc.application_policy) for acc in res]


def user_can_run(session, user, application, policy):
    """Returns True if the user can run a given application with a specific
    policy. False otherwise. Note that the user can be None.
    In that case, returns False.

    Parameters
    ----------
    session : Session
        The current session
    user : User
        the orm User, or None.
    application : Application
        The application object
    policy : ApplicationPolicy
        The application policy

    Returns
    -------
    boolean

    """
    if user is None:
        return False

    team_ids = [team.id for team in user.teams]
    return session.query(Accounting) \
        .filter(Accounting.team_id.in_(team_ids)) \
        .filter(Accounting.application == application) \
        .filter(Accounting.application_policy == policy) \
        .exists()
