..
.. Copyright John Reid 2012
..
.. This is a reStructuredText document. If you are reading this in text format, it can be 
.. converted into a more readable format by using Docutils_ tools such as rst2html.
..

.. _Docutils: http://docutils.sourceforge.net/docs/user/tools.html



Types
=====



.. _Intervals:

Intervals
---------


Intervals represent a contiguous set of elements. They are right-open by default
    
    >>> from pyicl import Interval
    >>> interval = Interval(0, 10)
    >>> print interval
    [0,10)
    >>> 0 in interval
    True
    >>> 9 in interval
    True
    >>> 10 in interval
    False
    

This is shown by square and round brackets in the string representation. The bounds
are accessed via the bounds property.

	>>> from pyicl import IntervalBounds
	>>> print Interval(0, 3)
	[0,3)
	>>> print Interval(0, 3, IntervalBounds.LEFT_OPEN)
	(0,3]
	>>> print Interval(0, 3, IntervalBounds.CLOSED)
	[0,3]
	>>> print Interval(0, 3, IntervalBounds.OPEN)
	(0,3)
	>>> print Interval(0, 3, IntervalBounds.OPEN).bounds
	OPEN

    
Empty intervals and intervals with exactly one element in them can be constructed

    >>> Interval().empty
    True
    >>> 1 in Interval(1)
    True


The bounds can be accessed as lower and upper

    >>> Interval(0, 3).lower
    0
    >>> Interval(0, 3).upper
    3


Intervals over discrete domains such as integers have first and last properties.

    >>> from pyicl import IntInterval
    >>> IntInterval(0, 3).first
    0
    >>> IntInterval(0, 3).last
    2


Intervals are false if empty

    >>> bool(Interval())
    False
    >>> Interval().empty
    True
    >>> bool(Interval(1, 10))
    True


Element and interval membership is straightforward

    >>> 1 in Interval(0, 2)
    True
    >>> 3 in Interval(0, 2)
    False
    >>> Interval(0, 2) in Interval(0, 2)
    True
    >>> Interval(0, 3) in Interval(0, 2)
    False


Equivalence works as expected

    >>> Interval(0, 2) == Interval(0, 2)
    True
    >>> Interval(0, 3) != Interval(0, 2)
    True


Ordering works thus

    >>> Interval(1, 3) < Interval(5, 6)
    True
    >>> Interval(1, 3) < Interval(1, 6)
    True
    >>> Interval(1, 6) < Interval(1, 3)
    False
    >>> Interval(5, 6) > Interval(1, 3)
    True
    >>> Interval(1, 3) < Interval(1, 5)
    True
    >>> Interval(1, 5) > Interval(1, 3)
    True
    >>> Interval(1, 3) <= Interval(5, 6)
    True
    >>> Interval(5, 6) >= Interval(1, 3)
    True
    >>> Interval(1, 3) <= Interval(1, 5)
    True
    >>> Interval(1, 5) >= Interval(1, 3)
    True
    >>> Interval(1, 3) > Interval(5, 6)
    False
    >>> Interval(5, 6) < Interval(1, 3)
    False
    >>> Interval(1, 3) > Interval(1, 5)
    False
    >>> Interval(1, 5) < Interval(1, 3)
    False


There are also tests for exclusive ordering

    >>> IntInterval(1, 3).exclusive_less(IntInterval(1, 5))
    False
    >>> IntInterval(1, 5).exclusive_less(IntInterval(5, 7))
    True
    >>> IntInterval(1, 5).lower_less(IntInterval(2, 7))
    True
    >>> IntInterval(1, 5).lower_less(IntInterval(1, 7))
    False
    >>> IntInterval(1, 5).lower_equal(IntInterval(1, 7))
    True
    >>> IntInterval(1, 5).lower_equal(IntInterval(0, 7))
    False
    >>> IntInterval(1, 5).lower_less_equal(IntInterval(2, 7))
    True
    >>> IntInterval(1, 5).lower_less_equal(IntInterval(0, 7))
    False
    >>> IntInterval(1, 5).upper_less(IntInterval(2, 7))
    True
    >>> IntInterval(1, 5).upper_less(IntInterval(1, 5))
    False
    >>> IntInterval(1, 5).upper_equal(IntInterval(1, 5))
    True
    >>> IntInterval(1, 5).upper_equal(IntInterval(0, 7))
    False
    >>> IntInterval(1, 5).upper_less_equal(IntInterval(2, 7))
    True
    >>> IntInterval(1, 5).upper_less_equal(IntInterval(0, 3))
    False


Size comes in different forms. Discrete data types have a cardinality property

    >>> from pyicl import FloatInterval
    >>> IntInterval(1, 5).size
    4
    >>> IntInterval(1, 5).cardinality
    4
    >>> len(Interval(1, 5))
    4
    >>> len(FloatInterval(1, 5))
    4


Intervals can be subtracted from the left or the right

    >>> print Interval(1, 5).right_subtract(Interval(3, 5))
    [1,3)
    >>> print Interval(1, 5).left_subtract(Interval(1, 3))
    [3,5)


Intervals can be intersected and tested for intersections and disjointedness

    >>> print Interval(1, 5).intersection(Interval(0, 3))
    [1,3)
    >>> Interval(1, 3) == Interval(1, 5) & Interval(0, 3)
    True
    >>> interval = Interval(1, 5)
    >>> interval &= Interval(0, 3)
    >>> Interval(1, 3) == interval 
    True
    >>> Interval(3, 5).intersects(Interval(1, 4))
    True
    >>> Interval(3, 5).intersects(Interval(1, 3))
    False
    >>> Interval(3, 5).disjoint(Interval(1, 4))
    False
    >>> Interval(3, 5).disjoint(Interval(1, 3))
    True

    
Intervals can be tested whether they touch one another. "Touches" is not a reflexive operation.

    >>> Interval(0, 3).touches(Interval(3, 5))
    True
    >>> Interval(0, 3).touches(Interval(4, 5))
    False
    >>> Interval(0, 3).touches(Interval(2, 5))
    False
    >>> Interval(3, 5).touches(Interval(0, 3))
    False

    
The interval between two intervals can be calculated.

    >>> print Interval(0, 3).inner_complement(Interval(6, 9))
    [3,6)
    >>> print Interval(6, 9).inner_complement(Interval(0, 3))
    [3,6)
    
    
The distance between two intervals can be calculated.

    >>> print Interval(0, 3).distance(Interval(6, 9))
    3
    >>> print Interval(6, 9).distance(Interval(0, 3))
    3
    
    
    
    
    
.. _IntervalSets:
    
IntervalSets
------------

An interval set is a set that is implemented as a set of elements. They can be constructed empty, with a single
element, with an interval or with another interval set

	>>> from pyicl import IntervalSet, Interval, IntervalSet
	>>> IntervalSet().empty
	True
	>>> .1 in IntervalSet(.1)
	True
	>>> interval_set = IntervalSet(Interval(1, 9))
	>>> 5 in interval_set
	True
	>>> 5 in IntervalSet(interval_set)
	True


Iteration over intervals occurs at a segmental level. That is the members of the interval set
are presented as distinct whole intervals

	>>> for interval in IntervalSet(Interval(1, 9)).add(Interval(20, 29)):
	...     print interval
	[1,9)
	[20,29)


It is possible to look for the interval that an element is in

	>>> print IntervalSet(Interval(1, 9)).find(5)
	[1,9)
	>>> print IntervalSet(Interval(1, 9)).find(10)
	None
	

Similarly to intervals, there are tests for emptyness

	>>> bool(IntervalSet())
	False
	>>> bool(IntervalSet(1))
	True
	>>> IntervalSet().empty
	True
	>>> IntervalSet(1).empty
	False

	
Containedness is as expected

	>>> 1 in IntervalSet(1)
	True
	>>> 2 in IntervalSet(1)
	False
	>>> 2 in IntervalSet(Interval(1, 9))
	True
	>>> Interval(1, 9) in IntervalSet(Interval(1, 9))
	True
	>>> IntervalSet(Interval(1, 9)) in IntervalSet(Interval(1, 9))
	True
	

Equivalences and orderings are also as expected

	>>> from pyicl import IntIntervalSet
	>>> IntIntervalSet(1) == IntIntervalSet(1)
	True
	>>> IntIntervalSet(1) == IntIntervalSet(IntInterval(1))
	True
	>>> IntIntervalSet(1) == IntIntervalSet(IntInterval(1, 3))
	False
	>>> IntIntervalSet(1) != IntIntervalSet(IntInterval(1, 3))
	True
	>>> IntIntervalSet(1) < IntIntervalSet(IntInterval(1, 3))
	True
	>>> IntIntervalSet(1) > IntIntervalSet(IntInterval(1, 3))
	False
	

Discrete data types have a size and cardinality. Interval sets also have an iterative size
describing how many intervals they are composed of

	>>> IntIntervalSet(IntInterval(1, 5)).size
	4
	>>> IntIntervalSet(IntInterval(1, 5)).cardinality
	4
	>>> len(IntIntervalSet(IntInterval(1, 5)))
	4
	>>> IntIntervalSet(IntInterval(1, 5)).iterative_size
	1
	>>> IntIntervalSet(IntInterval(1, 5)).add(IntInterval(7,10)).iterative_size
	2
	>>> IntIntervalSet(IntInterval(1, 5)).add(IntInterval(5,10)).iterative_size
	1
	>>> IntIntervalSet(IntInterval(1, 5)).interval_count
	1


As with intervals, interval sets have bounds. Discrete data types also have a first and a last element
	
	>>> IntervalSet(Interval(1, 5)).lower
	1
	>>> IntervalSet(Interval(1, 5)).upper
	5
	>>> IntIntervalSet(IntInterval(1, 5)).first
	1
	>>> IntIntervalSet(IntInterval(1, 5)).last
	4
	




.. _IntervalMaps:

IntervalMaps
------------

An interval map is a map (or in python-esque, a dict) that is implemented as a map of interval-value pairs. Each element has a particular value associated with it.
The collection of elements is stored as a set of intervals such that each element of an interval
maps to the same value.

The *domain* of an interval map is the domain of the intervals in the map. The *codomain* of an interval
map is the data type of the values that the intervals map to. An *element* of an interval map is a pair mapping
an element of the domain to a value in the codomain.

	>>> from pyicl import IntervalMap
	>>> print IntervalMap.Element(1, "value")
	1; value


A *segment* of an interval map is a pair mapping an interval in the domain to a value in the codomain.

	>>> print IntervalMap.Segment(Interval(1, 5), 10.4)
	[1,5); 10.4


Interval maps can be constructed empty or from a segment
	
	>>> IntervalMap().empty
	True
	>>> 3 in IntervalMap(IntervalMap.Segment(Interval(1, 5), object()))
	True


Interval maps can be populated in several ways. The add method will combine values in the codomain.

	>>> map = IntervalMap(IntervalMap.Segment(Interval(1, 5), "X"))
	>>> print map.add(IntervalMap.Segment(Interval(3, 8), "Y"))
	{([1,3)->X)([3,5)->XY)([5,8)->Y)}


+= acts in the same way as add.

	>>> map = IntervalMap(IntervalMap.Segment(Interval(1, 5), "X"))
	>>> map += (IntervalMap.Segment(Interval(3, 8), "Y"))
	>>> print map
	{([1,3)->X)([3,5)->XY)([5,8)->Y)}
	

The insert method only inserts into the map where there is no collision.

    >>> map = IntervalMap(IntervalMap.Segment(Interval(1, 5), "X"))
    >>> print map.insert(IntervalMap.Segment(Interval(3, 8), "Y"))
    {([1,5)->X)([5,8)->Y)}


The set method will override values.

    >>> print IntervalMap(IntervalMap.Segment(Interval(1, 5), "X")).set(IntervalMap.Element(3, "Y"))
    {([1,3)->X)([3,3]->Y)((3,5)->X)}

	
If the codomain of a map supports subtraction, so does the map

    >>> map = IntervalMap(IntervalMap.Segment(Interval(1, 5), 2))
    >>> print map - IntervalMap.Segment(Interval(2, 4), 1)
    {([1,2)->2)([2,4)->1)([4,5)->2)}


The erase method will remove values    

    >>> map = IntervalMap(IntervalMap.Segment(Interval(1, 5), 2))
    >>> print map.erase(Interval(2, 4))
    {([1,2)->2)([4,5)->2)}


Interval maps are presented as sequences of segments
	
	>>> for segment in IntervalMap(IntervalMap.Segment(Interval(1, 5), "value1")).add(IntervalMap.Segment(Interval(11, 15), "value2")):
	...     print segment
	[1,5); value1
	[11,15); value2


The segment that contains a value in the domain can be found if it is in the map

	>>> print IntervalMap(IntervalMap.Segment(Interval(1, 5), object())).find(2).interval
	[1,5)
	>>> print IntervalMap(IntervalMap.Segment(Interval(1, 5), object())).find(12)
	None


A map can test whether it holds a particular value or interval in the domain, an element, a segment	or another map

	>>> map = IntervalMap(IntervalMap.Segment(Interval(1, 5), "X"))
	>>> 2 in map
	True
	>>> Interval(1, 3) in map
	True
	>>> IntervalMap.Element(3, "X") in map
	True
	>>> IntervalMap.Element(8, "X") in map
	False
	>>> IntervalMap.Element(3, "Y") in map
	False
	>>> IntervalMap.Segment(Interval(1, 3), "X") in map
	True
	>>> IntervalMap.Segment(Interval(1, 8), "X") in map
	False
	>>> IntervalMap.Segment(Interval(1, 3), "Y") in map
	False
	>>> map in map
	True
	>>> IntervalMap(IntervalMap.Segment(Interval(1, 5), "X")) in map
	True
	>>> IntervalMap(IntervalMap.Segment(Interval(1, 5), "Y")) in map
	False


Equality operators work as expected

	>>> segment = IntervalMap.Segment(Interval(1, 5), "X")
	>>> map == IntervalMap(segment)
	True
	>>> map != IntervalMap()
	True

	
The size of an interval map is the number of elements it holds. The iterative size or
count is how many segments it holds

	>>> from pyicl import IntIntervalMap
	>>> IntIntervalMap().size
	0
	>>> IntIntervalMap(IntIntervalMap.Segment(IntInterval(1, 5), "X")).size
	4
	>>> IntIntervalMap(IntIntervalMap.Segment(IntInterval(1, 5), "X")).cardinality
	4
	>>> len(IntIntervalMap(IntIntervalMap.Segment(IntInterval(1, 5), "X")))
	4
	>>> IntervalMap(IntervalMap.Segment(Interval(1, 5), "X")).iterative_size
	1
	>>> IntervalMap(IntervalMap.Segment(Interval(1, 5), "X")).interval_count
	1
	
	
Intersections between maps and various other types are possible

    >>> from pyicl import IntervalIntMap
    >>> map = IntervalIntMap(IntervalIntMap.Segment(Interval(1, 5), 2))
    >>> print map.intersection(Interval(2, 4))
    {([2,4)->2)}
    >>> print map.intersection(5)
    {}
    >>> print map.intersection(3)
    {([3,3]->2)}


Symmetric difference or XOR is available

    >>> from pyicl import IntervalIntMap
    >>> map = IntervalIntMap(IntervalIntMap.Segment(Interval(3, 5), 2))
    >>> print map ^ IntervalIntMap.Segment(Interval(0, 10), 4)
    {([0,3)->4)([5,10)->4)}
    >>> map ^= IntervalIntMap.Segment(Interval(0, 10), 4)
    >>> print map
    {([0,3)->4)([5,10)->4)}





IntervalBounds
--------------

Interval bounds can be open or closed on the left or right of the interval.

	>>> from pyicl import IntervalBounds
	>>> IntervalBounds.OPEN.closed_on_right
	False
	>>> IntervalBounds.OPEN.closed_on_left
	False
	>>> IntervalBounds.LEFT_OPEN.closed_on_right
	True
	>>> IntervalBounds.LEFT_OPEN.closed_on_left
	False
	>>> IntervalBounds.RIGHT_OPEN.closed_on_right
	False
	>>> IntervalBounds.RIGHT_OPEN.closed_on_left
	True
	>>> IntervalBounds.CLOSED.closed_on_right
	True
	>>> IntervalBounds.CLOSED.closed_on_left
	True
	
	
	
    