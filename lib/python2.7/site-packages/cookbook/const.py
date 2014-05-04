"""
"""

class _const( object ):
    """
    In Python, any variable can be re-bound at will -- and modules don't 
    let you define special methods such as an instance's __setattr__ 
    to stop attribute re-binding. Easy solution (in Python 2.1 and up): 
    use an instance as 'module'...
    
    Adapted from http://code.activestate.com/recipes/65207-constants-in-python/
    (released under PSF license).
    """
    class ConstError( TypeError ): pass
    def __setattr__( self, name, value ):
        if name in self.__dict__:
            raise self.ConstError, "Can't rebind const(%s)" % name
        self.__dict__[name] = value
    def __delattr__( self, name ):
        if name in self.__dict__:
            raise self.ConstError, "Can't unbind const(%s)" % name
        raise NameError, name

import sys
sys.modules[__name__] = _const()
