"""
From: http://code.activestate.com/recipes/52308-the-simple-but-handy-collector-of-a-bunch-of-named/
(released under PSF license).
"""

class Bunch(object):
    """
    Often we want to just collect a bunch of stuff together, naming each item of the bunch; 
    a dictionary's OK for that, but a small do-nothing class is even handier, and prettier to use.
    """
    
    def __init__(self, **kwds):
        self.__dict__.update( kwds )

    def __str__(self):
        return 'Bunch:\n\t%s' % '\n\t'.join(
                [
                        '%s:\n%s' % (k,v) for k, v in self.__dict__.iteritems()
                ]
        )
