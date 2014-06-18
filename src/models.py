from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Interval,
    PickleType,
    String,
    Table,
    Time,
    types,
)
from database import Base
from datetime import datetime
from dateutil.relativedelta import *
from dateutil.rrule import *
from sqlalchemy.orm import backref, relationship


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


class WeekdayList(types.TypeDecorator):
    """ Class for storing a list of dateutil.relativedelta 'weekday' types """
    impl = types.PickleType

    def convert_bind_param(self, weekdays, engine):
        return self.impl.convert_bind_param([(weekday.weekday, weekday.n) for
                                             weekday in weekday], engine)

    def convert_result_value(self, value, engine):
        weekdays = self.impl.convert_result_value(value, engine)
        return [weekday(weekday.weekday, weekday.n) for weekday in weekdays]


class User(Base):
    __tablename__ = 'user'
    onid = Column(String, primary_key=True, unique=True, index=True)
    fname = Column(String(40), nullable=False)
    mname = Column(String(40))
    lname = Column(String(40), nullable=False)
    dept = Column(String(40), index=True)
    email = Column(String(40))
    phone = Column(Integer)
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
                 email=None, phone=None, credentials=None):
        self.onid = onid
        self.fname = fname
        self.mname = mname
        self.lname = lname
        self.dept = dept
        self.email = email
        self.phone = phone
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

    #def is_free(self, start_dt, end_dt):
    #    events = Event.query.filter(Event.user.any(onid=self.onid)
    #                                .filter()


class Event(Base):
    __tablename__ = 'event'
    id = Column(Integer, primary_key=True)
    start_date = Column(Date, index=True)
    end_date = Column(Date, index=True)
    start_time = Column(Time)
    end_time = Column(Time)
    weekdays = Column(WeekdayList)
    description = Column(String(80))
    duration = Column(Interval)
    crn = Column(Integer)
    sec = Column(String)
    term = Column(String)

    def __init__(self, start_date=None, end_date=None, start_time=None,
                 end_time=None, weekdays=None, duration=None, description=None,
                 crn=None, sec=None, term=None):
        self.start_date = start_date
        self.end_date = end_date
        self.start_time = start_time
        self.end_time = end_time
        self.weekdays = weekdays
        self.duration = duration
        self.description = description
        self.crn = crn
        self.sec = sec
        self.term = term

    def __repr__(self):
        return '<Event %r - %r>' % (self.start_date, self.end_date)

    def get_freebusy(self, dtstart=None, until=None):
        own_dtstart = datetime.combine(self.start_time, self.start_time)
        own_until = datetime.combine(self.end_time, self.end_time)

        dtstart = dtstart or own_dtstart
        until = until or own_until

        recur = rrule(WEEKLY, dtstart=dtstart, until=until,
                      byweekday=self.weekdays)

        freebusy_list = []
        for start in recur:
            end = start + self.duration
            if end > until:
                end = until
            freebusy_list.append({'start': start, 'end': end})

        # Return the list of busy times in the form that Google returns a
        # freebusy query calendar
        return {'busy': freebusy_list}



class Group(Base):
    __tablename__ = 'group'
    id = Column(Integer, primary_key=True)
    name = Column(String(40))

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):

        return '<Group %r>' % (self.name)
