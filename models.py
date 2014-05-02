from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Interval,
    String,
    Table
)
from sqlalchemy.orm import backref, relationship
from database import Base


userevents = Table(
    'userevents',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('event_id', Integer, ForeignKey('events.id')),
)


usergroups = Table(
    'usergroups',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('group_id', Integer, ForeignKey('groups.id')),
)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    onid = Column(String, unique=True, index=True)
    fname = Column(String(50))
    lname = Column(String(50))
    dept = Column(String(50), index=True, nullable=True)
    email = Column(String(120), unique=120)
    events = relationship("Event",
                          secondary=userevents,
                          backref=backref('users', lazy='dynamic'),
                          lazy='dynamic')
    groups = relationship("Group",
                          secondary=usergroups,
                          backref=backref('users', lazy='dynamic'),
                          lazy='dynamic')

    def __init__(self, name=None, email=None):
        self.name = name
        self.email = email

    def __repr__(self):
        return '<User %r %r>' % (self.fname, self.lname)


class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime, index=True)
    duration = Column(Interval)

    def __init__(self, datetime=None):
        self.datetime = datetime

    def __repr__(self):
        return '<Event %r>' % (self.datetime)


class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return '<Group %r>' % (self.name)
