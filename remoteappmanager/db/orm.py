import contextlib
import hashlib
import os

from sqlalchemy import (
    Column, Integer, Boolean, Unicode, ForeignKey, create_engine, Enum,
    event)
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm.exc import DetachedInstanceError, NoResultFound

from remoteappmanager.logging.logging_mixin import LoggingMixin
from remoteappmanager.db.interfaces import ABCAccounting
from remoteappmanager.db import exceptions
from remoteappmanager.utils import parse_volume_string, mergedocs

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
def _set_sqlite_pragma(dbapi_connection, connection_record):
    """ Set pragma for sqlite3 when the engine connects
    Currently it adds support for foreign keys.
    Do nothing if sqlite3 is not available or if the database
    is not using sqlite3.
    """
    try:
        # In case sqlite3 is not compiled?
        import sqlite3
    except ImportError:
        return
    else:
        if isinstance(dbapi_connection, sqlite3.Connection):
            with contextlib.closing(dbapi_connection.cursor()) as cursor:
                cursor.execute("PRAGMA foreign_keys=ON")


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


@mergedocs(ABCAccounting)
class AppAccounting(ABCAccounting):

    def __init__(self, url, **kwargs):
        ''' Initialiser

        Parameters
        ----------
        url : str
            the url for connecting to a database

        **kwargs
            optional keyword arguments for `Database`

        See Also
        --------
        `SQLAlchemy Database Urls <http://docs.sqlalchemy.org/en/
        latest/core/engines.html?highlight=database%20url>`_
        '''
        self.db = Database(url, **kwargs)
        self.check_database_readable()

    def check_database_readable(self):
        ''' Raise IOError if the database url points to a sqlite database
        that is not readable

        TODO: may extend for validating databases in other dialects?
        '''
        db_url = self.db.url

        if db_url.startswith('sqlite:///'):
            file_path = os.path.abspath(db_url[10:])
            if not os.access(file_path, os.R_OK):
                raise IOError(
                    'Sqlite database {} is not readable'.format(file_path))

    def get_user_by_name(self, user_name):
        # We create a session here to make sure it is only
        # used in one thread
        with contextlib.closing(self.db.create_session()) as session:

            with transaction(session):
                user = session.query(User).filter_by(
                    name=user_name).one_or_none()

            # Removing internal references to the session is
            # required such that the object is detached and
            # can be reused in a different thread
            if user:
                session.expunge(user)

        return user

    def get_apps_for_user(self, user):
        # We create a session here to make sure it is only
        # used in one thread
        with contextlib.closing(self.db.create_session()) as session:
            result = apps_for_user(session, user)

            # Removing internal references to the session is
            # required such that the objects can be reused
            # in a different thread
            session.expunge_all()

        return result

    def create_user(self, user_name):
        with detached_session(self.db) as session:

            try:
                with transaction(session):
                    orm_user = User(name=user_name)
                    session.add(orm_user)
            except IntegrityError:
                raise exceptions.Exists()

    def remove_user(self, user_name):
        with detached_session(self.db) as session:
            try:
                with transaction(session):
                    orm_user = session.query(User).filter(
                        User.name == user_name).one()

                    session.delete(orm_user)
            except NoResultFound:
                raise exceptions.NotFound()

    def list_users(self):
        with detached_session(self.db) as session:
            users = session.query(User).all()

        return users

    def create_application(self, app_name):
        with detached_session(self.db) as session:
            try:
                with transaction(session):
                    orm_app = Application(image=app_name)
                    session.add(orm_app)
            except IntegrityError:
                raise exceptions.Exists()

    def remove_application(self, app_name):
        with detached_session(self.db) as session:
            try:
                with transaction(session):
                    app = session.query(Application).filter(
                        Application.image == app_name).one()

                    session.delete(app)
            except NoResultFound:
                raise exceptions.NotFound()

    def list_applications(self):
        with detached_session(self.db) as session:
            applications = session.query(Application).all()

        return applications

    def grant_access(self, app_name, user_name,
                     allow_home, allow_view, volume):
        allow_common = False
        source = target = mode = None

        if volume is not None:
            allow_common = True
            source, target, mode = parse_volume_string(volume)

        with detached_session(self.db) as session:
            with transaction(session):
                try:
                    orm_app = session.query(Application).filter(
                        Application.image == app_name).one()

                    orm_user = session.query(User).filter(
                        User.name == user_name).one()
                except NoResultFound:
                    raise exceptions.NotFound()

                orm_policy = session.query(ApplicationPolicy).filter(
                    ApplicationPolicy.allow_home == allow_home,
                    ApplicationPolicy.allow_common == allow_common,
                    ApplicationPolicy.allow_view == allow_view,
                    ApplicationPolicy.volume_source == source,
                    ApplicationPolicy.volume_target == target,
                    ApplicationPolicy.volume_mode == mode).one_or_none()

                if orm_policy is None:
                    orm_policy = ApplicationPolicy(
                        allow_home=allow_home,
                        allow_common=allow_common,
                        allow_view=allow_view,
                        volume_source=source,
                        volume_target=target,
                        volume_mode=mode,
                    )
                    session.add(orm_policy)

                # Check if we already have the entry
                acc = session.query(Accounting).filter(
                    Accounting.user == orm_user,
                    Accounting.application == orm_app,
                    Accounting.application_policy == orm_policy
                ).one_or_none()

                if acc is None:
                    accounting = Accounting(
                        user=orm_user,
                        application=orm_app,
                        application_policy=orm_policy,
                    )
                    session.add(accounting)

    def revoke_access(self, app_name, user_name,
                      allow_home, allow_view, volume):
        allow_common = False
        source = target = mode = None

        if volume is not None:
            allow_common = True
            source, target, mode = parse_volume_string(volume)

        with detached_session(self.db) as session, \
                transaction(session):
            try:
                orm_app = session.query(Application).filter(
                    Application.image == app_name).one()

                orm_user = session.query(User).filter(
                    User.name == user_name).one()

                orm_policy = session.query(ApplicationPolicy).filter(
                    ApplicationPolicy.allow_home == allow_home,
                    ApplicationPolicy.allow_common == allow_common,
                    ApplicationPolicy.allow_view == allow_view,
                    ApplicationPolicy.volume_source == source,
                    ApplicationPolicy.volume_target == target,
                    ApplicationPolicy.volume_mode == mode).one()
            except NoResultFound:
                raise exceptions.NotFound()

            try:
                session.query(Accounting).filter(
                    Accounting.application == orm_app,
                    Accounting.user == orm_user,
                    Accounting.application_policy == orm_policy,
                    ).delete()
            except NoResultFound:
                pass


@contextlib.contextmanager
def detached_session(db):
    """Creates a session where at the end, the objects retrieved
    are detached from the session itself"""

    with contextlib.closing(db.create_session()) as session:

        yield session

        # Removing internal references to the session is
        # required such that the object is detached and
        # can be reused in a different thread
        session.expunge_all()


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
    """Returns a tuple of tuples, each containing an application and the
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
    A tuple of tuples (mapping_id, orm.Application, orm.ApplicationPolicy)
    """

    if user is None:
        return ()

    try:
        user_name = user.name
    except DetachedInstanceError:
        # If the orm.User object was obtained from
        # another session and that it is detached
        # we need to add it back so that we can refresh
        # its attributes' value
        session.add(user)
        user_name = user.name

    res = session.query(Accounting).join(
        Accounting.user, aliased=True).filter_by(
            name=user_name).all()

    return tuple((hashlib.md5(
                         ("{}_{}".format(
                             acc.application.image,
                             acc.application_policy.id)).encode("utf-8")
                  ).hexdigest(),
                  acc.application,
                  acc.application_policy) for acc in res)
