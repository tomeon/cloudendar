#
# Copyright John Reid 2011, 2012
#

from cookbook.script_basics import boost_python_dlopen_flags
import pkg_resources as _pkg_resources

__doc__ = _pkg_resources.resource_string(__name__, "README")
__license__ = _pkg_resources.resource_string(__name__, "LICENSE")
__release__, __svn_revision__ = _pkg_resources.resource_string(__name__, "VERSION").strip().split('-')
__major_version__, __minor_version__, __release_version__ = map(int, __release__.split('.'))
__version__ = '%d.%d' % (__major_version__, __minor_version__)

def version_string():
    """Return the release and svn revision as a string."""
    return '%s %s' % (__release__, __svn_revision__)


class Set(set):
    """A set class that implements += and -= as the pyicl package expects.
    """
    
    def __iadd__(self, other):
        """Set union operation. Does not update self
        """
        return self | other
    
    def __iand__(self, other):
        """Set intersection operation. Does not update self
        """
        return self & other

    def __ior__(self, other):
        """Set union operation. Does not update self
        """
        return self | other
    
    def __isub__(self, other):
        """Set subtraction operation. Does not update self
        """
        return self - other

    def __ixor__(self, other):
        """Set exclusive-or operation. Does not update self
        """
        return self ^ other


def _iteritems_two(dict1, dict2, missing_value=None):
    """
    Iterate over the keys in both dicts.
    
    Yield (key, value1, value2) where value1 and value2 are replaced
    with missing_value if the key is not in that dict.
    """
    for key, value1 in dict1.iteritems():
        yield key, value1, dict2.get(key, missing_value)
    for key, value2 in dict2.iteritems():
        if key not in dict1:
            yield key, missing_value, value2


def _add_if_not_none(v1, v2):
    if v1 is not None:
        if v2 is not None:
            return v1 + v2
        else:
            return v1
    else:
        assert v2 is not None
        return v2


class Dict(dict):
    """A dict class that implements += and -= as the pyicl package expects.

    >>> dict1 = Dict((('a', 4), ('b', 1)))
    >>> dict2 = Dict((('a', 2), ('c', 2)))
    >>> dict1 += dict2
    """
    
    def __iadd__(self, other):
        """Dict union operation. Does not update self
        """
        return self.__class__(
            (k, _add_if_not_none(v1, v2)) 
            for k, v1, v2 
            in _iteritems_two(self, other))

    def __iand__(self, other):
        """Dict intersection operation. Does not update self
        """
        raise NotImplementedError()

    def __ior__(self, other):
        """Dict union operation. Does not update self
        """
        raise NotImplementedError()

    def __isub__(self, other):
        """Dict subtraction operation. Does not update self
        """
        raise NotImplementedError()

    def __ixor__(self, other):
        """Dict exclusive-or operation. Does not update self
        """
        raise NotImplementedError()

    

class Aggregator(object):
    """A class that allows the user to supply an add function to aggregate elements
    of the codomain for an IntervalMap.
    """
    
    def __init__(self, value, add):
        """Constructor. Takes a value and an add function.
        """
        self.value = value
        self._add = add
    
    def __iadd__(self, other):
        """Implements += as pyicl package expects.
        """
        return Aggregator(self._add(self.value, other.value), self._add)
        
    def __eq__(self, other):
        return None != other and self.value == other.value and self._add == other._add
    
    def __str__(self):
        return str(self.value)



def make_aggregator(add):
    """Can be used like Aggregator but does not need add argument passed to each object.
    Drawback is that the objects are not pickle-able.
    
    Usage::
    
        >>> MyAggregator = pyicl.make_aggregator(min)
        >>> map = pyicl.IntervalMap()
        >>> map += map.Segment(pyicl.Interval(time(20,00), time(22,00)), MyAggregator(1.72))
        >>> map += map.Segment(pyicl.Interval(time(21,00), time(23,00)), MyAggregator(1.85))
        >>> for segment in map:
        ...     print segment
        [20:00:00,22:00:00); 1.72
        [22:00:00,23:00:00); 1.85
    """
    class Result(object):
        def __init__(self, value):
            """Constructor. Takes a value.
            """
            self.value = value
        
        def __iadd__(self, other):
            """Implements += as pyicl package expects.
            """
            return Result(add(self.value, other.value))
            
        def __eq__(self, other):
            return None != other and self.value == other.value
        
        def __str__(self):
            return str(self.value)

    return Result

#from functools import wraps
#def my_simple_logging_decorator(func):
#    @wraps(func)
#    def you_will_never_see_this_name(*args, **kwargs):
#        print 'calling {}'.format(func.__name__)
#        return func(*args, **kwargs)
#    return you_will_never_see_this_name
#  
#import types, inspect
#for name, fn in inspect.getmembers(Set):
#    if isinstance(fn, types.UnboundMethodType):
#        setattr(Set, name, my_simple_logging_decorator(fn))
#
#
#def __trace__(frame, event, arg):
#    print event
#    if event == "call":
#        filename = frame.f_code.co_filename
#        lineno = frame.f_lineno
#        print "%s @ %s" % (filename, lineno)
#        #print arg
#    return __trace__



#
# Load everything in extension module (using correct dlopen flags)
#
with boost_python_dlopen_flags():
    from _pyicl import *

