#!/usr/bin/python

import os
import sqlite3

conn = sqlite3.connect('database/schedule.db')
print "Opened database successfully";


# Kayla -- These are great sources of examples for us to use. 
# http://www.tutorialspoint.com/sqlite/sqlite_python.htm
# http://pymotw.com/2/sqlite3/


# Insert command in phython

conn.execute("insert into user values('clampitl','Laurye','Clampitt','Student')");
conn.execute("insert into event values('clampitl',' 2014-05-02 03:30:00',' 2014-05-02 09:00:00','Some Atrrib','Intel Innovation','PhotoShoot',0);");

conn.commit()
print "Records created successfully";
conn.close()


conn = sqlite3.connect('database/schedule.db')
print "Opened database successfully";

# example of a select command by ordinal value (so row 0, 1, 2,... )

cursor = conn.execute("SELECT * from user")
for row in cursor:
   print "This Contacts onid_id: ", row[0]
   print "First name: ", row[1]
   print "Last name: ", row[2]
   print "Department: ", row[3], "\n"

print "Operation done successfully";
conn.close()



conn = sqlite3.connect('database/schedule.db')
print "Opened database successfully";

# example of a select command by Field name such as onid_id, fname, lname ....

cursor = conn.execute("SELECT onid_id, fname, lname, dept from user")
for onid_id, fname, lname, dept in cursor:
   print 'This Contacts onid_id: ', onid_id
   print 'First name: ', fname
   print 'Last name: ', lname
   print 'Department: ', dept, "\n"

print "Operation done successfully";
conn.close()


# Example of Update Statement

with sqlite3.connect('database/schedule.db') as conn:
    cursor = conn.cursor()
    query = "update user set dept = 'I was updated!' where dept = 'Student'"
    cursor.execute(query)


# Delete statement

#conn.execute("DELETE from user where dept = 'I was updated';")
#conn.commit
#print "Total number of rows deleted :", conn.total_changes



