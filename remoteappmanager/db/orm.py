from remoteappmanager.logging.logging_mixin import LoggingMixin
from sqlalchemy import Column, Integer, Boolean, Unicode, ForeignKey
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine

Base = declarative_base()


class UserTeam(Base):
    """ The user (n <-> n) team association table """
    __tablename__ = "user_team"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    team_id = Column(Integer, ForeignKey('team.id'))


class User(Base):
    """ Table for users. """
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)

    #: The name of the user as specified by jupyterhub.
    #: This entry must be unique and is, for all practical purposes,
    #: a primary key.
    name = Column(Unicode, index=True, unique=True)

    #: The teams this user belongs to (n <-> n)
    teams = relationship("Team", secondary="user_team", back_populates="users")


class Team(Base):
    """ Teams of users. """
    __tablename__ = "team"
    id = Column(Integer, primary_key=True)

    #: The name of the group. Note that, differently from users, we can have
    #: multiple teams with the same name. The reason is that we would obtain
    #: unusual behavior if user A creates a group with name B, and then B
    #: creates a user. Users are automatically assigned a group with their
    #: own name when first created.
    name = Column(Unicode)

    #: The users parts of this team (n <-> n)
    users = relationship("User", secondary="user_team", back_populates="teams")


class Application(Base):
    __tablename__ = "application"
    id = Column(Integer, primary_key=True)
    image = Column(Unicode)


class ApplicationPolicy(Base):
    __tablename__ = "application_policy"
    id = Column(Integer, primary_key=True)
    allow_home = Column(Boolean)
    allow_common = Column(Boolean)
    allow_team_view = Column(Boolean)


class Accounting(Base):
    __tablename__ = "accounting"
    id = Column(Integer, primary_key=True)


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
        self.engine = create_engine(self.url, **kwargs)

    def create_session_factory(self):
        """Create a new session class at the database url with the current
        engine.
        """
        self.log.info("Creating session to db: {}".format(self.url))
        try:
            return sessionmaker(bind=self.engine)
        except OperationalError:
            self.log.exception(
                "Failed to connect db session: {}".format(self.url)
            )
            raise

    def reset(self):
        """Completely resets the content of the database, removing
        and reinitializing the tables. Should be used only if the database
        does not already exist, or if its contents are irrelevant or obsolete.
        """
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)
