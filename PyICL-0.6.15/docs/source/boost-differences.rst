..
.. Copyright John Reid 2012
..
.. This is a reStructuredText document. If you are reading this in text format, it can be 
.. converted into a more readable format by using Docutils_ tools such as rst2html.
..

.. _Docutils: http://docutils.sourceforge.net/docs/user/tools.html




Differences to boost.icl
========================

The pyicl package is based on the `boost.icl`__ C++ library. Anyone conversant with this library
will notice some differences between the two. We discuss the major differences here to clarify
pyicl's behaviour. The discussion will probably not be so helpful to those not familiar with C++
or boost.icl in particular.

.. __: http://www.boost.org/libs/icl/doc/html




Domain and codomain types
-------------------------

The pyicl package exports several different variants of intervals, interval sets and interval
maps. These are primarily distinguished by the domains and codomains in which they operate.
For example a pyicl.Interval will take any python object as a lower or upper bound, however
a pyicl.IntInterval will only accept integers.

    >>> from pyicl import Interval, IntInterval
    >>> "bar" in Interval("a", "c")
    True
    >>> 0 in IntInterval(0, 1)
    True


In general the name of the pyicl container class will reflect its domain type. If the name
starts with "Interval", the interval bounds can be any python object. Otherwise the beginning of the
name defines the domain the container works on, for example "Int" or "Float".  For example,
pyicl.FloatInterval is an interval in the floating point domain. In general, intervals over
python objects work well. One reason to use specific interval domains might
be performance. Another is stricter type checking, although this is hardly "pythonic".
For example nonsensical bounds do not work although they do not fail on construction, only
on use.

    >>> Interval(0, "a")
    <pyicl...Interval object at 0x...>
    >>> len(Interval(0, "a"))
    Traceback (most recent call last):
      ...
    TypeError: unsupported operand type(s) for -: 'str' and 'int'


The codomain type of maps is placed before the word "Map" in their names. For example,
pyicl.IntIntervalStringMap is a map from intervals over integers to string values.
pyicl.FloatIntervalMap is a map from intervals over floating point numbers to general python
objects. The codomain type of a map can affect its behaviour because Boost.icl uses an identity_element
value as part of its map aggregation on overlap functionality. For python objects, pyicl defines
this as None. This value of None is shared amongst all maps that have codomains of python objects.
If the codomain of your map is naturally an integer, 0 is a much better choice for the identity 
element. For string values, "" is more natural. This is the primary reason for exposing maps with
different codomains. The pyicl package uses a custom combine functor when the codomain type is a
python object to avoid problems. This is necessary to allow intersections of maps with object 
codomains for example:

	>>> from pyicl import IntervalMap
	>>> map = IntervalMap()
	>>> map += map.Segment(Interval(1, 5), 2)
	>>> print map.intersection(Interval(2, 4))
	{([2,4)->2)}

	>>> from pyicl import Set
	>>> map = IntervalMap()
	>>> map += IntervalMap.Segment(Interval(1, 5), Set([2]))
	>>> print map.intersection(Interval(2, 4))
	{([2,4)->Set([2]))}


Despite this work around, *it is better to use maps which have the correct codomain
defined*. For example you should prefer to use pyicl.IntervalIntMap over pyicl.IntervalMap
if your codomain type is integral. For example:

	>>> from pyicl import IntervalIntMap
	>>> map = IntervalIntMap()
	>>> map += map.Segment(Interval(1, 5), 2)
	>>> print map.intersection(Interval(2, 4))
	{([2,4)->2)}

