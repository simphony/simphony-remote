from remoteappmanager.logging.logging_mixin import LoggingMixin
from sqlalchemy import Column, Integer, Boolean, Unicode
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(Unicode)
    #t stateams = relationship()


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


class Team(Base):
    __tablename__ = "team"
    id = Column(Integer, primary_key=True)
    name = Column(Unicode)
    #users = relationship()


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
        does not already exist, of if its contents are irrelevant or obsolete.
        """
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)
