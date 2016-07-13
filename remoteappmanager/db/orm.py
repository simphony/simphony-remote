import contextlib
import sqlite3

from sqlalchemy import (
    Column, Integer, Boolean, Unicode, ForeignKey, create_engine, Enum,
    literal, event)
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from remoteappmanager.logging.logging_mixin import LoggingMixin
from remoteappmanager.db.interfaces import ABCAccounting

Base = declarative_base()


class IdMixin(object):
    """Base class to provide an id"""
    id = Column(Integer, primary_key=True)

    @classmethod
    def from_id(cls, session, id):
        return session.query(cls).filter(cls.id == id).one()


class User(IdMixin, Base):
    """ Table for users. """
    __tablename__ = "user"

    #: The name of the user as specified by jupyterhub.
    #: This entry must be unique and is, for all practical purposes,
    #: a primary key.
    name = Column(Unicode, index=True, unique=True)


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

    #: If the container should be accessible by other people
    allow_view = Column(Boolean)

    # Which volume to mount
    volume_source = Column(Unicode, nullable=True)

    # Where to mount it in the container
    volume_target = Column(Unicode, nullable=True)

    # In which mode
    volume_mode = Column(Enum("ro", "rw"), nullable=True)


class Accounting(Base):
    """Holds the information about who is allowed to run what."""
    __tablename__ = "accounting"

    user_id = Column(Integer,
                     ForeignKey("user.id", ondelete="CASCADE"),
                     primary_key=True)

    application_id = Column(Integer,
                            ForeignKey("application.id", ondelete="CASCADE"),
                            primary_key=True)

    application_policy_id = Column(
        Integer,
        ForeignKey("application_policy.id", ondelete="CASCADE"),
        primary_key=True)

    user = relationship("User")

    application = relationship("Application")

    application_policy = relationship("ApplicationPolicy")


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if type(dbapi_connection) is sqlite3.Connection:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


class Database(LoggingMixin):
    def __init__(self, url, **kwargs):
        """Initialises a database connection to a given database url.

        Parameters
        ----------
        url : url
            A sqlalchemy url to connect to a specified database.
        kwargs : dict
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


class AppAccounting(ABCAccounting):

    def __init__(self, url, **kwargs):
        self.db = Database(url, **kwargs)

        # We keep the same session for all transactions
        # so that the session remains on one thread
        self.session = self.db.create_session()

    def get_user_by_name(self, user_name):
        """ Return an orm.User given a user name.  Return None
        if the user name is not found in the database
        """
        with transaction(self.session):
            return self.session.query(User).filter_by(
                name=user_name).one_or_none()

    def get_apps_for_user(self, user):
        """ Return a tuple of tuples, each containing an application
        and the associated policy that a user, defined by the user_name,
        is allowed to run.  If user is None, an empty tuple is returned.

        Parameters
        ----------
        user : orm.User

        Returns
        -------
        tuple
           tuples of tuples
           (mapping_id, orm.Application, orm.ApplicationPolicy)
           The mapping_id is a unique string identifying the combination
           of application and policy. It is not unique per user.
        """
        if user is None:
            return ()

        with transaction(self.session):
            res = self.session.query(Accounting).join(
                Accounting.user, aliased=True).filter_by(
                    name=user.name).all()

        return tuple(("_".join((acc.application.image,
                                str(acc.application_policy.id))),
                      acc.application,
                      acc.application_policy) for acc in res)


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
    user : User or None
        the orm User, or None.

    Returns
    -------
    A list of tuples (mapping_id, orm.Application, orm.ApplicationPolicy)
    """

    if user is None:
        return []

    res = session.query(Accounting).filter(
        Accounting.user == user).all()

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
    user : orm.User or None
        the orm User, or None.
    application : orm.Application
        The application object
    policy : orm.ApplicationPolicy
        The application policy

    Returns
    -------
    boolean

    """
    if user is None:
        return False

    query = session.query(Accounting) \
        .filter(Accounting.user == user,
                Accounting.application == application,
                Accounting.application_policy == policy)

    return session.query(literal(True)).filter(query.exists()).scalar()
