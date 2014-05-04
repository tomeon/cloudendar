"""

Adapted from: http://code.activestate.com/recipes/325205-cache-decorator-in-python-24/
(released under PSF license).

The latest version of Python introduced a new language feature, function and method decorators
(PEP 318, http://www.python.org/peps/pep-0318.html). This recipe show a common callable transformation
that can benefit from the new syntax, often referred to as Memoization pattern.

Memoization is a useful pattern for improving the amortized performance of a computationally expensive
function or method. The new syntax allows making explicit that a callable is memoized.

A restriction of the recipe above is that the arguments of the function (and also the method receiver
object for methods) have to be hashable.

The decorator can be generalized by allowing different caching policies (e.g. a FIFO cache or a cache
implementing an LRU policy) apart from the implied "cache-forever" policy of a dict.
"""

import logging, cPickle, os

def cachedmethod(function):
    return Memoize(function)
cached_method = cachedmethod

class Memoize(object):
    def __init__(self,function):
        self._cache = {}
        self._callable = function
        self.__name__ = function.__name__

    def __call__(self, *args, **kwds):
        cache = self._cache
        key = self._getKey(*args,**kwds)
        try: return cache[key]
        except KeyError:
            cachedValue = cache[key] = self._callable(*args,**kwds)
            return cachedValue

    def _getKey(self,*args,**kwds):
        return kwds and (args, ImmutableDict(kwds)) or args


class pickled_cached_method(object):
    def __init__(self, file, dump_on_update=True):
        self._file = file
        self.dump_on_update = dump_on_update
    def __call__(self, function):
        return PickledMemoize(function, self._file, dump_on_update=self.dump_on_update)


class PickledMemoize(object):
    """
    Like Memoize but pickles its cache/memo for use in next python session
    """

    def __init__(self, function, pickle_file, dump_on_update=True):
        "Constructor. pickle_file can either be a string naming the file or a callable that returns the name of the file."
        self._callable = function
        self._file = pickle_file
        self._cache = None
        self.__name__ = function.__name__
        self.dump_on_update = dump_on_update
        self.dirty = False
    
    def _get_file(self):
        "@return: The file we pickle to and from."
        # if the filename is a string then return it
        if isinstance(self._file, str):
            return self._file
        else: # otherwise assume it is a callable we can use to retrieve the name
            return self._file()
    
    file = property(_get_file, 'The name of the file we pickle the cache to and from.')

    def load_cache(self):
        "Load the memo from the cache."
        logging.info('Loading pickled memo from %s', self.file)
        self._cache = cPickle.load(open(self.file, 'rb'))

    def dump_cache(self):
        "Dump the memo to the cache."
        if self.dirty:
            logging.info('Dumping pickled memo to %s', self.file)
            cPickle.dump(self._get_cache(), open(self.file, 'wb'), protocol=2)
            self.dirty = False

    def _get_cache(self):
        "@return: The cache dictionary, loading it from disk if necessary and possible."
        if None == self._cache:
            if os.access(self.file, os.R_OK):
                self.load_cache()
            else:
                logging.info('No readable pickled memo cached to disk at %s, initialising empty cache', self.file)
                self._cache = {}
        return self._cache

    def __call__(self, *args, **kwds):
        "Call the function and cache result."
        cache = self._get_cache()
        key = self._getKey(*args,**kwds)
        try:
            return cache[key]
        except KeyError:
            cachedValue = cache[key] = self._callable(*args, **kwds)
            self.dirty = True
            if self.dump_on_update:
                self.dump_cache()
            return cachedValue

    def _getKey(self, *args, **kwds):
        "@return: The key for these arguments that indexes the cache dictionary."
        return kwds and (args, ImmutableDict(kwds)) or args


class ImmutableDict(dict):
    '''A hashable dict.'''

    def __init__(self,*args,**kwds):
        dict.__init__(self,*args,**kwds)
    def __setitem__(self,key,value):
        raise NotImplementedError, "dict is immutable"
    def __delitem__(self,key):
        raise NotImplementedError, "dict is immutable"
    def clear(self):
        raise NotImplementedError, "dict is immutable"
    def setdefault(self,k,default=None):
        raise NotImplementedError, "dict is immutable"
    def popitem(self):
        raise NotImplementedError, "dict is immutable"
    def update(self,other):
        raise NotImplementedError, "dict is immutable"
    def __hash__(self):
        return hash(tuple(self.iteritems()))



class pickled_method(object):
    "Pickles the result of the method (ignoring arguments) and uses this if possible on the next call."
    def __init__(self, file, name):
        self._file = file
        self._name = name

    def __call__(self, function):
        return Picklize(function, self._file, self._name)



class Picklize(object):
    def __init__(self, function, file, name):
        self._callable = function
        self._file = file
        self._name = name

    def __call__(self, *args, **kwds):
        try:
            logging.info('Trying to load %s from %s', self._name, self._file)
            return cPickle.load(open(self._file, 'rb'))
        except:
            logging.info('Could not load %s, will recalculate', self._name)
            result = self._callable(*args,**kwds)
            logging.info('Dumping %s to %s', self._name, self._file)
            cPickle.dump(result, open(self._file, 'wb'), protocol=2)
            return result




if __name__ == '__main__':
    from math import sqrt,log,sin,cos

    class Example:
        def __init__(self,x,y):
            # self._x and self._y should not be changed after initialization
            self._x = x
            self._y = y

        @cachedmethod
        def computeSomething(self, alpha, beta):
            w = log(alpha) * sqrt(self._x * alpha + self._y * beta)
            z = log(beta) * sqrt(self._x * beta + self._y * alpha)
            return sin(z) / cos(w)
