from sqlalchemy import Column, Integer, String
from database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    email = Column(String(120), unique=120)

    def __init__(self, name=None, email=None):
        self.name = name
        self.email = email

    def __repr__(self):
        return '<User %r>' % (self.name)


class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime)

    def __init__(self, datatime=None):
        self.datetime = datetime

    def __repr__(self):
        return '<Event %r>' % (self.datetime)


class UserEvent(Base):
    __tablename__ = 'userevent'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    event_id = Column(Integer)
