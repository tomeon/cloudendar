..
.. Copyright John Reid 2012
..
.. This is a reStructuredText document. If you are reading this in text format, it can be 
.. converted into a more readable format by using Docutils_ tools such as rst2html.
..

.. _Docutils: http://docutils.sourceforge.net/docs/user/tools.html



Examples
========

We recreate some of the `boost.icl examples`__ in python.

__ http://www.boost.org/doc/libs/1_49_0/libs/icl/doc/html/boost_icl/examples.html




Party
-----

Here is the description from the `boost.icl
C++ documentation`__:

__ http://www.boost.org/doc/libs/1_49_0/libs/icl/doc/html/boost_icl/examples/party.html

	Example party demonstrates the possibilities of an interval map (interval_map or split_interval_map). An interval_map maps intervals to a given content. In this case the content is a set of party guests represented by their name strings.
	
	As time goes by, groups of people join the party and leave later in the evening. So we add a time interval and a name set to the interval_map for the attendance of each group of people, that come together and leave together. On every overlap of intervals, the corresponding name sets are accumulated. At the points of overlap the intervals are split. The accumulation of content is done via an operator += that has to be implemented for the content parameter of the interval_map. Finally the interval_map contains the history of attendance and all points in time, where the group of party guests changed.
	
	Party demonstrates a principle that we call aggregate on overlap: On insertion a value associated to the interval is aggregated with those values in the interval_map that overlap with the inserted value. There are two behavioral aspects to aggregate on overlap: a decompositional behavior and an accumulative behavior.
	
	- The decompositional behavior splits up intervals on the timedimension of the interval_map so that the intervals are split whenever associated values change.
	- The accumulative behavior accumulates associated values on every overlap of an insertion for the associated values.
	
	The aggregation function is += by default. Different aggregations can be used, if desired.
	
First we create some sets representing people who come to the party together.
The standard python set class does not implement += (__iadd__) and -= (__isub__) as the pyicl
package expects. We will use the pyicl package's version of set, pyicl.Set, that plays much nicer
with pyicl.

    >>> import pyicl, datetime
    >>> mary_harry = pyicl.Set(('Mary', 'Harry'))
    >>> diana_susan = pyicl.Set(('Diana', 'Susan'))
    >>> peter = pyicl.Set(('Peter',))
	    
A party is an interval map that maps time intervals to sets of guests.

    >>> party = pyicl.IntervalMap()
    
We add a segment for Mary and Harry's attendance

    >>> party.add(party.Segment(pyicl.Interval(datetime.datetime(2008, 5, 20, 19, 30), datetime.datetime(2008, 5, 20, 23, 00)), mary_harry))
    <pyicl...IntervalMap object at 0x...>
    
We can also use += to add segments

    >>> party += party.Segment(pyicl.Interval(datetime.datetime(2008, 5, 20, 20, 10), datetime.datetime(2008, 5, 21, 00, 00)), diana_susan)
    >>> party += party.Segment(pyicl.Interval(datetime.datetime(2008, 5, 20, 22, 15), datetime.datetime(2008, 5, 21, 00, 30)), peter)

Now we can access the history of party guests

    >>> print 'History of party guests.'
    History of party guests.
    >>> for segment in party:
    ...     when = segment.interval
    ...     who = segment.value
    ...     print '%s: %s' % (when, ', '.join(who))
    [2008-05-20 19:30:00,2008-05-20 20:10:00): Mary, Harry
    [2008-05-20 20:10:00,2008-05-20 22:15:00): Diana, Susan, Mary, Harry
    [2008-05-20 22:15:00,2008-05-20 23:00:00): Diana, Harry, Mary, Peter, Susan
    [2008-05-20 23:00:00,2008-05-21 00:00:00): Diana, Peter, Susan
    [2008-05-21 00:00:00,2008-05-21 00:30:00): Peter




Overlap counter
---------------

Here is the description from the `boost.icl C++ documentation`__:

__ http://www.boost.org/doc/libs/1_49_0/libs/icl/doc/html/boost_icl/examples/overlap_counter.html

	Example overlap counter provides the simplest application of an interval_map that maps intervals to integers. An interval_map<int,int> serves as an overlap counter if we only add interval value pairs that carry 1 as associated value.

	Doing so, the associated values that are accumulated in the interval_map are just the number of overlaps of all added intervals.

Define a function to print which intervals overlap
	
	>>> def print_overlaps(overlap_counter):
	...     for segment in overlap_counter:
	...         if segment.value == 1:
	...             print 'in interval %s intervals do not overlap' % segment.interval
	...         else:
	...             print 'in interval %s: %d intervals overlap' % (segment.interval, segment.value)

Create an interval map and add some intervals to it, each with a value of one.

	>>> overlap_counter = pyicl.IntervalMap()
	>>> overlap_counter += overlap_counter.Segment(pyicl.Interval(4, 8), 1)
	>>> print_overlaps(overlap_counter)
	in interval [4,8) intervals do not overlap
	
	>>> overlap_counter += overlap_counter.Segment(pyicl.Interval(6, 9), 1)
	>>> print_overlaps(overlap_counter)
	in interval [4,6) intervals do not overlap
	in interval [6,8): 2 intervals overlap
	in interval [8,9) intervals do not overlap

	>>> overlap_counter += overlap_counter.Segment(pyicl.Interval(1, 9), 1)
	>>> print_overlaps(overlap_counter)
	in interval [1,4) intervals do not overlap
	in interval [4,6): 2 intervals overlap
	in interval [6,8): 3 intervals overlap
	in interval [8,9): 2 intervals overlap




Party's height average
----------------------

Here is the description from the `boost.icl C++ documentation`__:

__ http://www.boost.org/doc/libs/1_49_0/libs/icl/doc/html/boost_icl/examples/partys_height_average.html

	In the example partys_height_average.cpp we compute yet another aggregation: The average height of guests. This is done by defining a class counted_sum that sums up heights and counts the number of guests via an operator +=.
	
	Based on the operator += we can aggregate counted sums on addition of interval value pairs into an interval_map.

Define a class to keep track of the sum of the height of the guests and the number of guests present.

    >>> class CountedSum(object):
    ...
    ...     def __init__(self):
    ...         self.count = 0
    ...         self.sum = 0.
    ...
    ...     def __init__(self, sum, count=1):
    ...         self.count = count
    ...         self.sum = sum
    ...
    ...     def average(self):
    ...         return self.count and (self.sum / self.count) or 0.
    ...
    ...     def __iadd__(self, other):
    ...         return CountedSum(self.sum + other.sum, self.count + other.count)
    ...
    ...     def __eq__(self, other):
    ...         return pyicl.identity_element != other and self.count == other.count and self.sum == other.sum
    
Create an IntervalMap to keep track of the party's average height and the relevant information to it

    >>> from datetime import datetime
    >>> height_sums = pyicl.IntervalMap()
    >>> height_sums += height_sums.Segment(pyicl.Interval(datetime(2008, 05, 20, 19, 30), datetime(2008, 05, 20, 23, 00)), CountedSum(165.))
    >>> height_sums += height_sums.Segment(pyicl.Interval(datetime(2008, 05, 20, 19, 30), datetime(2008, 05, 20, 23, 00)), CountedSum(180.))
    >>> height_sums += height_sums.Segment(pyicl.Interval(datetime(2008, 05, 20, 20, 10), datetime(2008, 05, 21, 00, 00)), CountedSum(170.))
    >>> height_sums += height_sums.Segment(pyicl.Interval(datetime(2008, 05, 20, 20, 10), datetime(2008, 05, 21, 00, 00)), CountedSum(165.))
    >>> height_sums += height_sums.Segment(pyicl.Interval(datetime(2008, 05, 20, 22, 15), datetime(2008, 05, 21, 00, 30)), CountedSum(200.))
    
Print the average height at each segment of the party.

	>>> for segment in height_sums:
	...     print '[%s - %s): %.2f cm = %.2f ft' % (
	...         segment.interval.lower, segment.interval.upper, 
	...         segment.value.average(), segment.value.average() / 30.48
	...     )
	[2008-05-20 19:30:00 - 2008-05-20 20:10:00): 172.50 cm = 5.66 ft
	[2008-05-20 20:10:00 - 2008-05-20 22:15:00): 170.00 cm = 5.58 ft
	[2008-05-20 22:15:00 - 2008-05-20 23:00:00): 176.00 cm = 5.77 ft
	[2008-05-20 23:00:00 - 2008-05-21 00:00:00): 178.33 cm = 5.85 ft
	[2008-05-21 00:00:00 - 2008-05-21 00:30:00): 200.00 cm = 6.56 ft





Party's tallest guests
----------------------

Here is the description from the `boost.icl C++ documentation`__:

__ http://www.boost.org/doc/libs/1_49_0/libs/icl/doc/html/boost_icl/examples/partys_height_average.html

	Defining operator += (and -=) is probably the most important method to implement arbitrary kinds of user defined aggregations. An alternative way to choose a desired aggregation is to instantiate an interval_map class template with an appropriate aggregation functor. For the most common kinds of aggregation the icl provides such functors as shown in the example.
	
	Example partys_tallest_guests.cpp also demonstrates the difference between an interval_map that joins intervals for equal associated values and a split_interval_map that preserves all borders of inserted intervals. 

Define a function to add the guests

    >>> from datetime import datetime
    >>> def add_guests(interval_map):
    ...     # Mary & Harry : Harry is 1.80m tall
    ...     interval_map += interval_map.Segment(pyicl.Interval(datetime(2008, 05, 20, 19, 30), datetime(2008, 05, 20, 23, 00)), pyicl.Max(180))
    ...     # Diana & Susan : Diana is 1.70m tall
    ...     interval_map += interval_map.Segment(pyicl.Interval(datetime(2008, 05, 20, 20, 10), datetime(2008, 05, 21, 00, 00)), pyicl.Max(170))
    ...     # Peter : Peter is 2.00m tall
    ...     interval_map += interval_map.Segment(pyicl.Interval(datetime(2008, 05, 20, 22, 15), datetime(2008, 05, 21, 00, 30)), pyicl.Max(200))

Define a function to print the tallest guest heights

	>>> def print_tallest(tallest_guest):
	...     for segment in tallest_guest:
	...         print '[%s - %s): %d cm = %.2f ft' % (
	...             segment.interval.lower, segment.interval.upper, 
	...             segment.value.value, segment.value.value / 30.48
	...         )
    
Maintain a record of the tallest guest

	>>> tallest_guest = pyicl.IntervalMap()
	>>> add_guests(tallest_guest)
	>>> print_tallest(tallest_guest)
	[2008-05-20 19:30:00 - 2008-05-20 22:15:00): 180 cm = 5.91 ft
	[2008-05-20 22:15:00 - 2008-05-21 00:30:00): 200 cm = 6.56 ft

    
Now do the same but with an interval map that remembers where the interval boundaries are

	>>> tallest_guest = pyicl.SplitIntervalMap()
	>>> add_guests(tallest_guest)
	>>> print_tallest(tallest_guest)
	[2008-05-20 19:30:00 - 2008-05-20 20:10:00): 180 cm = 5.91 ft
	[2008-05-20 20:10:00 - 2008-05-20 22:15:00): 180 cm = 5.91 ft
	[2008-05-20 22:15:00 - 2008-05-20 23:00:00): 200 cm = 6.56 ft
	[2008-05-20 23:00:00 - 2008-05-21 00:00:00): 200 cm = 6.56 ft
	[2008-05-21 00:00:00 - 2008-05-21 00:30:00): 200 cm = 6.56 ft

	
	
	
Time grids for months and weeks
-------------------------------

Here is the description from the `boost.icl C++ documentation`__:

__ http://www.boost.org/doc/libs/1_49_0/libs/icl/doc/html/boost_icl/examples/time_grids.html

	A split_interval_set preserves all interval borders on insertion and intersection operations. So given a split_interval_set and an addition of an interval::
	
		x =  {[1,     3)}
		x.add(     [2,     4)) 
	
	then the intervals are split at their borders::
	
		x == {[1,2)[2,3)[3,4)}
	
	Using this property we can intersect split_interval_maps in order to iterate over intervals accounting for all occurring changes of interval borders.
	
	In this example we provide an intersection of two split_interval_sets representing a month and week time grid.


Define a function that splits an interval of dates into a grid of months. That is, every month contained in the interval
is represented as a separate interval in the result.

    >>> from datetime import timedelta
    >>> def next_month(date):
    ...     while True:
    ...         date += timedelta(1)
    ...         if 1 == date.day:
    ...             return date
    ...
    >>> def make_grid(interval, next):
    ...     result = pyicl.SplitIntervalSet()
    ...     date = interval.lower
    ...     while date in interval:
    ...         end = next(date)
    ...         result += pyicl.Interval(date, min(interval.upper, end))
    ...         date = end
    ...     return result 

Define a function so we can do the same for weeks.

    >>> def next_week(date):
    ...     return date + timedelta(8 - date.weekday())

Create the grids.

	>>> from datetime import date
	>>> someday = date(2008, 6, 22)
	>>> thenday = date(2008, 8, 22)
	>>> month_and_week_grid = make_grid(pyicl.Interval(someday, thenday), next_month)
	>>> month_and_week_grid &= make_grid(pyicl.Interval(someday, thenday), next_week)
	>>> for interval in month_and_week_grid:
	...     if 1 == interval.lower.day:
	...         print 'new month:', interval
	...     elif 1 == interval.lower.weekday():
	...         print 'new week: ', interval
	...     elif month_and_week_grid.lower == interval.lower:
	...         print 'first day:', interval
	first day: [2008-06-22,2008-06-24)
	new week:  [2008-06-24,2008-07-01)
	new month: [2008-07-01,2008-07-08)
	new week:  [2008-07-08,2008-07-15)
	new week:  [2008-07-15,2008-07-22)
	new week:  [2008-07-22,2008-07-29)
	new week:  [2008-07-29,2008-08-01)
	new month: [2008-08-01,2008-08-05)
	new week:  [2008-08-05,2008-08-12)
	new week:  [2008-08-12,2008-08-19)
	new week:  [2008-08-19,2008-08-22)
    
   

User groups
-----------

Here is the description from the `boost.icl C++ documentation`__:

__ http://www.boost.org/doc/libs/1_49_0/libs/icl/doc/html/boost_icl/examples/user_groups.html

	Example user groups shows the availability of set operations on interval_maps.
	
	In the example there is a user group med_users of a hospital staff that has the authorisation to handle medical data of patients. User group admin_users has access to administrative data like health insurance and financial data.
	
	The membership for each user in one of the user groups has a time interval of validity. The group membership begins and ends.
	
	- Using a union operation + we can have an overview over the unified user groups and the membership dates of employees.
	- Computing an intersection & shows who is member of both med_users and admin_users at what times.


Define some sets of users.

    >>> mary_harry = pyicl.Set(['Mary', 'Harry'])
    >>> diana_susan = pyicl.Set(['Diana', 'Susan'])
    >>> chief_physician = pyicl.Set(['Dr.Jekyll'])
    >>> director_of_admin = pyicl.Set(['Mr.Hyde'])
    
Create med_users group.

    >>> from datetime import date
    >>> med_users = pyicl.IntervalMap()
    >>> med_users += med_users.Segment(pyicl.Interval(date(2008,  1,  1), date(2009,  1,  1)), mary_harry)
    >>> med_users += med_users.Segment(pyicl.Interval(date(2008,  1, 15), date(2009,  1,  1)), chief_physician)
    >>> med_users += med_users.Segment(pyicl.Interval(date(2008,  2,  1), date(2008, 10, 16)), director_of_admin)

Create admin_users group.

    >>> admin_users = pyicl.IntervalMap()
    >>> admin_users += med_users.Segment(pyicl.Interval(date(2008,  3, 20), date(2008, 10,  1)), diana_susan)
    >>> admin_users += med_users.Segment(pyicl.Interval(date(2008,  1, 15), date(2009,  1,  1)), chief_physician)
    >>> admin_users += med_users.Segment(pyicl.Interval(date(2008,  2,  1), date(2008, 10, 16)), director_of_admin)

Use the union and the intersection operations.

    >>> all_users = med_users + admin_users
    >>> super_users = med_users & admin_users

Show the membership of the medical staff.

    >>> for segment in med_users:
    ...     print segment
    [2008-01-01,2008-01-15); Set(['Mary', 'Harry'])
    [2008-01-15,2008-02-01); Set(['Dr.Jekyll', 'Mary', 'Harry'])
    [2008-02-01,2008-10-16); Set(['Dr.Jekyll', 'Mary', 'Mr.Hyde', 'Harry'])
    [2008-10-16,2009-01-01); Set(['Dr.Jekyll', 'Mary', 'Harry'])
    
Show the membership of the admin staff.

    >>> for segment in admin_users:
    ...     print segment
    [2008-01-15,2008-02-01); Set(['Dr.Jekyll'])
    [2008-02-01,2008-03-20); Set(['Dr.Jekyll', 'Mr.Hyde'])
    [2008-03-20,2008-10-01); Set(['Diana', 'Dr.Jekyll', 'Mr.Hyde', 'Susan'])
    [2008-10-01,2008-10-16); Set(['Dr.Jekyll', 'Mr.Hyde'])
    [2008-10-16,2009-01-01); Set(['Dr.Jekyll'])
    
Show the membership of the all users.

    >>> for segment in all_users:
    ...     print segment
    [2008-01-01,2008-01-15); Set(['Mary', 'Harry'])
    [2008-01-15,2008-02-01); Set(['Dr.Jekyll', 'Mary', 'Harry'])
    [2008-02-01,2008-03-20); Set(['Mr.Hyde', 'Harry', 'Dr.Jekyll', 'Mary'])
    [2008-03-20,2008-10-01); Set(['Susan', 'Diana', 'Dr.Jekyll', 'Mr.Hyde', 'Harry', 'Mary'])
    [2008-10-01,2008-10-16); Set(['Mr.Hyde', 'Harry', 'Dr.Jekyll', 'Mary'])
    [2008-10-16,2009-01-01); Set(['Dr.Jekyll', 'Mary', 'Harry'])
    
Show the membership of the super users.

    >>> for segment in super_users:
    ...     print segment
    [2008-01-15,2008-02-01); Set(['Dr.Jekyll'])
    [2008-02-01,2008-10-16); Set(['Dr.Jekyll', 'Mr.Hyde'])
    [2008-10-16,2009-01-01); Set(['Dr.Jekyll'])
    