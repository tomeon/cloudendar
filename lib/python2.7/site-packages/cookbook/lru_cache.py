"""
One-line decorator call adds caching to functions with hashable arguments and no
keyword arguments. When the maximum size is reached, the least recently used
entry is discarded -- appropriate for long-running processes which cannot allow
caches to grow without bound. Includes built-in performance instrumentation.

Adapted from http://code.activestate.com/recipes/498245-lru-and-lfu-cache-decorators/
(released under PSF license).
"""


from collections import deque
import pickle

def lru_cache(maxsize=0, cache_storage_file=None):
    '''
    Decorator applying a least-recently-used cache with the given maximum size.

    Arguments to the cached function must be hashable.
    Cache performance statistics stored in f.hits and f.misses.
    '''
    def decorating_function(f):
        cache = {}        # mapping of args to results
        if maxsize:
            queue = deque()   # order that keys have been accessed
            refcount = {}     # number of times each key is in the access queue
        else:
            queue = refcount = None # no maxsize

        # load from file if possible
        if cache_storage_file:
            try:
                cache, queue, refcount = pickle.load(open(cache_storage_file))
            except:
                print 'Could not load cache from "%s"' % cache_storage_file

        def dump():
            if None == cache_storage_file:
                raise RuntimeError('No cache storage file specified')
            pickle.dump((cache, queue, refcount), open(cache_storage_file, 'w'))

        def wrapper(*args):
            # localize variable access (ugly but fast)
            _cache=cache; _len=len; _refcount=refcount; _maxsize=maxsize
            if _maxsize:
                queue_append=queue.append; queue_popleft = queue.popleft

            # get cache entry or compute if not found
            try:
                result = _cache[args]
                wrapper.hits += 1
            except KeyError:
                result = _cache[args] = f(*args)
                wrapper.misses += 1

            # do we have a maxsize for this cache?
            if None != queue:
                # record that this key was recently accessed
                queue_append(args)
                _refcount[args] = _refcount.get(args, 0) + 1

                # Purge least recently accessed cache contents
                while _len(_cache) > _maxsize:
                    k = queue_popleft()
                    _refcount[k] -= 1
                    if not _refcount[k]:
                        del _cache[k]
                        del _refcount[k]

                # Periodically compact the queue by duplicate keys
                if _len(queue) > _maxsize * 4:
                    for i in [None] * _len(queue):
                        k = queue_popleft()
                        if _refcount[k] == 1:
                            queue_append(k)
                        else:
                            _refcount[k] -= 1
                    assert len(queue) == len(cache) == len(refcount) == sum(refcount.itervalues()), (queue, cache, refcount)

            return result
        wrapper.__doc__ = f.__doc__
        wrapper.__name__ = f.__name__
        wrapper.hits = wrapper.misses = 0
        wrapper.cache = cache
        wrapper.persist_cache = dump
        return wrapper
    return decorating_function


if __name__ == '__main__':

    @lru_cache(cache_storage_file='lru_cache_test.cache')
    def f(x, y):
        return 3*x+y

    domain = range(5)
    from random import choice
    for i in xrange(1000):
        r = f(choice(domain), choice(domain))

    print f.hits, f.misses
