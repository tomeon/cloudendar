from database import db_session, db_init
from models import User, Group, Event, usergroups, userevents


db_init()


user = User('smithj', 'John', 'Smith', 'Philosophy',
            'smithj@onid.oregonstate.edu')

db_session.add(user)
db_session.commit()

db_session.remove()
