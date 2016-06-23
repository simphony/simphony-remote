from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "user"


class Application(Base):
    __tablename__ = "application"


class ApplicationPolicy(Base):
    __tablename__ = "application_policy"


class Accounting(Base):
    __tablename__ = "accounting"


class Team(Base):
    __tablename__ = "team"
