from database import db_init, db_session
from models import User, Event

import datetime
import pprint


if __name__ == "__main__":
    db_init()

    # Create users to insert into the database
    abby_dearing = User(onid='dearina', fname='Abby', lname='Dearing',
                        dept='Philosophy')
    wanda_fisher = User(onid='fisherw', fname='Wanda', lname='Fisher',
                        dept='Zoology')
    john_smith = User(onid='smithj', fname='John', lname='Smith',
                      dept='Philosophy')

    # Create an event to insert into the database
    # Grab the current time, UTC, and create another
    # datetime for an hour later
    now = datetime.datetime.utcnow()
    one_hour = now + datetime.timedelta(hours=1)

    # Create an event
    dept_meeting = Event(start_date=now, end_date=one_hour,
                         location="Main office",
                         description="Department meeting")

    # Add the mapping of users to events. Here, John Smith and Abby Dearing
    # will be going to the meeting.  The attribute takes a Python list as a value.
    abby_dearing.events = [dept_meeting]
    john_smith.events = [dept_meeting]

    # Add the users and event to the database
    db_session.add(john_smith)
    db_session.add(abby_dearing)
    db_session.add(wanda_fisher)
    db_session.add(dept_meeting)

    wanda_fisher.events = [dept_meeting]

    # Commit transaction
    db_session.commit()

    # Now we query!

    # Get all users and events
    user_list = User.query.all()
    event_list = Event.query.all()
    print("Users: {}".format(pprint.pformat(user_list)))
    print("Events: {}".format(pprint.pformat(event_list)))

    # Get all events for Abby Dearing
    abby_events = Event.query.filter(Event.user.any(fname='Abby',
                                                    lname='Dearing')).all()
    print("Abby's events: {}".format(pprint.pformat(abby_events)))

    # Get all events for Wanda Fisher.  The list should be empty.
    wanda_events = Event.query.filter(Event.user.any(fname='Wanda',
                                                    lname='Fisher')).all()
    print("Wanda's events: {}".format(pprint.pformat(wanda_events)))

    # Checking that I understand querying...
    print("Wanda's ID: {}".format(wanda_fisher.onid))
    wanda_2 = User.query.filter(User.onid == wanda_fisher.onid).first()
    wanda_2_events = Event.query.filter(Event.user.any(fname=wanda_2.fname,
                                                    lname=wanda_2.lname)).all()
    print("Wanda 2's events: {}".format(pprint.pformat(wanda_2_events)))

    # Close the database session
    db_session.remove()
