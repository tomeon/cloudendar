from database import db_init, db_session
from models import User, Event

import datetime
import pprint


if __name__ == "__main__":
    db_init()

    # Create a user to insert into the database
    u = User(onid='smithj', fname='John', lname='Smith', dept='Philosophy',
             email='smithj@onid.oregonstate.edu')

    # Create an event to insert into the database
    # Grab the current time, UTC
    now = datetime.datetime.utcnow()
    # Create another dattime
    one_hour = datetime.timedelta(hours=1)
    e = Event(now, one_hour)

    # Add the user and event to the database
    db_session.add(u)
    db_session.add(e)

    # Commit transaction
    db_session.commit()

    # Now we query!
    user_list = User.query.all()
    event_list = Event.query.all()
    print("Users: {}".format(pprint.pformat(user_list)))
    print("Events: {}".format(pprint.pformat(event_list)))
