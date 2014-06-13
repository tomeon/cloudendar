import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


# Set up path to database file
basedir = os.path.abspath(os.path.dirname(__file__))
db_uri = 'sqlite:///' + os.path.join(basedir, 'data/data.db')


# Set up scoped session
engine = create_engine(db_uri, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))


# Declare base object for subclassing tables
Base = declarative_base()
Base.query = db_session.query_property()


# This is the function to import and call when initializing a database session
def db_init():
    import models
    Base.metadata.create_all(bind=engine)
