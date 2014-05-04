#
# Copyright John Reid 2007
#

"""
Code for lazy cached initialisation.
"""
import cPickle

class Cache(object):
    """
    Caches the result of calling a function. The function is evaluated once on the
    first invocation of self() and the cached result is returned for every
    invocation thereafter.
    """

    def __init__(self, initialiser):
        self.initialiser = initialiser
        self.instance = None

    def __call__(self):
        if None == self.instance:
            self.instance = self.initialiser()
        return self.instance



class PersistedCache(Cache):
    """
    Caches the result of calling a function. The function is evaluated once on the
    first invocation of self() and the cached result is returned for every
    invocation thereafter. The persist method stores the cached result in the
    given file. This pickled object is reused in preference to function
    invocation the next time the object is loaded.
    """
    def __init__(self, initialiser, pickle_file):
        Cache.__init__(self, initialiser)
        self.pickle_file = pickle_file

    def __call__(self):
        if None == self.instance:
            try:
                print 'Unpickling: %s' % self.pickle_file
                self.instance = cPickle.load(open(self.pickle_file))
            except:
                print 'Unpickling failed: %s' % self.pickle_file
                self.instance =  Cache.__call__(self)
        return self.instance

    def persist(self):
        "Pickle object to disk"
        print 'Pickling: %s' % self.pickle_file
        cPickle.dump(self(), open(self.pickle_file, 'w'))

def persist_all_in(variables):
    'Persist all the PersistedCaches in the given set of variables. E.g. persist_all_in(vars().values())'
    for var in variables:
        if isinstance(var, PersistedCache):
            var.persist()
