..
.. Copyright John Reid 2012
..
.. This is a reStructuredText document. If you are reading this in text format, it can be 
.. converted into a more readable format by using Docutils_ tools such as rst2html.
..

.. _Docutils: http://docutils.sourceforge.net/docs/user/tools.html



Definition and Basic Usage
==========================


Definition
----------

The main classes in the pyicl package are :ref:`Intervals`, :ref:`IntervalSets` and :ref:`IntervalMaps`.

- An interval is a set of contiguous elements. 
- An interval set is a set that is implemented as a set of intervals.
- An interval map is a map (or in python-esque, a dict) that is implemented as a
  map of interval-value pairs. 




Basic usage
-----------

In this section we demonstrate basic usage of the PyICL module. We follow the examples given
in the `Boost Interval Container Library`__ documentation. First import the module:

__ http://www.boost.org/libs/icl/doc/html

    >>> import pyicl

Intervals are half-open by default:
    
    >>> interval = pyicl.Interval(0, 10)
    >>> print interval
    [0,10)
    >>> print 0 in interval
    True
    >>> print 10 in interval
    False





Two aspects: fundamental and segmental
--------------------------------------

Interval sets and maps can be viewed in 2 complementary ways or aspects. The first aspect treats
interval sets and maps as containers of elements and is called the **fundamental aspect**. The second
aspect treats interval sets and maps as containers of intervals (or segments) and is called the
**segmental aspect**. The fundamental aspect supports inserting elements into a set or map and testing
for their presence:

    >>> myset = pyicl.IntervalSet()
    >>> myset += 42
    >>> print 42 in myset
    True


The segmental aspect supports efficiently iterating over a interval set or map. We would
rather not visit each element, we would rather visit whole segments at a time:

	>>> from datetime import time
	>>> news = pyicl.Interval(time(20, 00, 00), time(20, 15, 00))
	>>> talk = pyicl.Interval(time(22, 45, 30), time(23, 30, 50))
	>>> myTvPrograms = pyicl.IntervalSet()
	>>> myTvPrograms.add(news).add(talk)
	<pyicl...IntervalSet object at 0x...>
	>>> for segment in myTvPrograms:
	...     print segment
	[20:00:00,20:15:00)
	[22:45:30,23:30:50)


We can test for an element's inclusion in an interval set just as we can in an interval:

	>>> time(20, 10, 00) in myTvPrograms
	True
	>>> time(21, 00, 00) in myTvPrograms
	False
	>>> time(23, 00, 00) in myTvPrograms
	True



Addability and subtractability
------------------------------

For interval sets, addability is implemented as set union and subtractability is
implemented as set difference:

    >>> interval1 = pyicl.Interval( 0, 10)
    >>> interval2 = pyicl.Interval( 5, 15)
    >>> interval3 = pyicl.Interval(20, 30)
    >>> intervalsetA = pyicl.IntervalSet()
    >>> intervalsetA += interval1
    >>> intervalsetA += interval3
    >>> print intervalsetA
    {[0,10)[20,30)}
    >>> intervalsetB = pyicl.IntervalSet()
    >>> intervalsetB += interval2
    >>> print intervalsetB
    {[5,15)}
    >>> print intervalsetA + intervalsetB
    {[0,15)[20,30)}
    >>> print intervalsetA - intervalsetB
    {[0,5)[20,30)}
    >>> print intervalsetB - intervalsetA
    {[10,15)}


For interval maps, addability and subtractability are more interesting, especially
when elements of the two maps collide:

    >>> map = pyicl.IntIntervalMap()
    >>> map += map.Segment(pyicl.IntInterval(0,10), 1)
    >>> map += map.Segment(pyicl.IntInterval(5,15), 2)
    >>> for segment in map:
    ...     print segment
    [0,5); 1
    [5,10); 3
    [10,15); 2
    >>> map -= map.Segment(pyicl.IntInterval(5,15), 2)
    >>> for segment in map:
    ...     print segment
    [0,10); 1
    [10,15); 0
    




Aggregate on overlap
--------------------

Here we use an example of a party to demonstrate the *aggregate on overlap* principle on IntervalMaps.

    >>> from datetime import time
    >>> map = pyicl.IntervalMap()
    >>> map += map.Segment(pyicl.Interval(time(20,00), time(22,00)), pyicl.Set(['Mary',]))
    >>> map += map.Segment(pyicl.Interval(time(21,00), time(23,00)), pyicl.Set(['Harry',]))
    >>> for segment in map:
    ...     print segment
    [20:00:00,21:00:00); Set(['Mary'])
    [21:00:00,22:00:00); Set(['Mary', 'Harry'])
    [22:00:00,23:00:00); Set(['Harry'])



Here we have used the pyicl.Set class to store the guests at the party. This is important as the default
python set class does not interact well with the pyicl package.
 
We may wish to perform other operations on aggregation. For example, we could store the guests heights 
rather than their names and use the pyicl package to infer the maximum height of the guests at the party
at any given time. 

    >>> map = pyicl.IntervalMap()
    >>> map += map.Segment(pyicl.Interval(time(20,00), time(22,00)), pyicl.Max(1.72))
    >>> map += map.Segment(pyicl.Interval(time(21,00), time(23,00)), pyicl.Max(1.85))
    >>> for segment in map:
    ...     print segment
    [20:00:00,21:00:00); 1.72
    [21:00:00,23:00:00); 1.85




Custom aggregators
------------------

In the previous example we used the pyicl.Max class that implements += as maximisation. We could also define a
custom class that performs minimisation or any other operation we care to use.

    >>> class Min(object):
    ...     def __init__(self, value):
    ...         self.value = value
    ...     def __iadd__(self, other):
    ...          return Min(min(self.value, other.value))
    ...     def __eq__(self, other):
    ...          return None != other and self.value == other.value
    ...     def __str__(self):
    ...          return str(self.value)
    >>> map = pyicl.IntervalMap()
    >>> map += map.Segment(pyicl.Interval(time(20,00), time(22,00)), Min(1.72))
    >>> map += map.Segment(pyicl.Interval(time(21,00), time(23,00)), Min(1.85))
    >>> for segment in map:
    ...     print segment
    [20:00:00,22:00:00); 1.72
    [22:00:00,23:00:00); 1.85


The pyicl package supplies an Aggregator class to simplify this. The above code can be replaced by

    >>> map = pyicl.IntervalMap()
    >>> map += map.Segment(pyicl.Interval(time(20,00), time(22,00)), pyicl.Aggregator(1.72, min))
    >>> map += map.Segment(pyicl.Interval(time(21,00), time(23,00)), pyicl.Aggregator(1.85, min))
    >>> for segment in map:
    ...     print segment
    [20:00:00,22:00:00); 1.72
    [22:00:00,23:00:00); 1.85


There is also a slightly simpler alternative with the drawback that the values are not pickle-able.

    >>> MyAggregator = pyicl.make_aggregator(min)
    >>> map = pyicl.IntervalMap()
    >>> map += map.Segment(pyicl.Interval(time(20,00), time(22,00)), MyAggregator(1.72))
    >>> map += map.Segment(pyicl.Interval(time(21,00), time(23,00)), MyAggregator(1.85))
    >>> for segment in map:
    ...     print segment
    [20:00:00,22:00:00); 1.72
    [22:00:00,23:00:00); 1.85



Interval combining styles
-------------------------


When we add intervals or interval value pairs to interval containers, the intervals can be added 
in different ways: Intervals can be joined or split or kept separate. The different interval 
combining styles are shown by example.

Joining intervals are the default and are joined on overlap or touch.

    >>> myset = pyicl.IntervalSet()
    >>> myset += pyicl.Interval(0, 10)
    >>> myset += pyicl.Interval(5, 15)
    >>> for interval in myset:
    ...     print interval
    [0,15)
    

Splitting intervals are are split on overlap.
All interval borders are preserved.

    >>> myset = pyicl.SplitIntervalSet()
    >>> myset += pyicl.Interval(0, 10)
    >>> myset += pyicl.Interval(5, 15)
    >>> for interval in myset:
    ...     print interval
    [0,5)
    [5,10)
    [10,15)
    

Separating intervals are joined on overlap, not on touch.

    >>> myset = pyicl.SeparateIntervalSet()
    >>> myset += pyicl.Interval(0, 10)
    >>> myset += pyicl.Interval(5, 15)
    >>> myset += pyicl.Interval(15, 20)
    >>> for interval in myset:
    ...     print interval
    [0,15)
    [15,20)
    
    