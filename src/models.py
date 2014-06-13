from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Interval,
    PickleType,
    String,
    Table,
)
from sqlalchemy.orm import backref, relationship
from database import Base


user_event = Table(
    'user_event',
    Base.metadata,
    Column('onid', Integer, ForeignKey('user.onid')),
    Column('eid', Integer, ForeignKey('event.id')),
)


user_group = Table(
    'user_group',
    Base.metadata,
    Column('onid', Integer, ForeignKey('user.onid')),
    Column('gid', Integer, ForeignKey('group.id')),
)


class User(Base):
    __tablename__ = 'user'
    onid = Column(String, primary_key=True, unique=True, index=True)
    fname = Column(String(40), nullable=False)
    mname = Column(String(40))
    lname = Column(String(40), nullable=False)
    dept = Column(String(40), index=True)
    email = Column(String(40))
    credentials = Column(PickleType())
    events = relationship("Event",
                          secondary=user_event,
                          backref=backref('user', lazy='dynamic'),
                          lazy='dynamic')
    groups = relationship("Group",
                          secondary=user_group,
                          backref=backref('user', lazy='dynamic'),
                          lazy='dynamic')

    def __init__(self, onid=None, fname=None, mname=None, lname=None, dept=None,
                 email=None, credentials=None):
        self.onid = onid
        self.fname = fname
        self.mname = mname
        self.lname = lname
        self.dept = dept
        self.email = email
        self.credentials = credentials

    def __repr__(self):
        return "<User {0} {1}>".format(self.fname, self.lname)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.onid)


class Event(Base):
    __tablename__ = 'event'
    id = Column(Integer, primary_key=True)
    start_date = Column(DateTime, index=True)
    end_date = Column(DateTime)
    attrb_name = Column(String(40))
    location = Column(String(40))
    description = Column(String(80))
    allday = Column(Boolean, default=False)
    duration = Column(Interval)

    def __init__(self, start_date=None, end_date=None, attrb_name=None,
                 location=None, description=None, allday=False):
        self.start_date = start_date
        self.end_date = end_date
        self.attrb_name = attrb_name
        self.location = location
        self.description = description
        self.allday = allday

    def __repr__(self):
        return '<Event %r - %r>' % (self.start_date, self.end_date)


class Group(Base):
    __tablename__ = 'group'
    id = Column(Integer, primary_key=True)
    name = Column(String(40))

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):

        return '<Group %r>' % (self.name)
