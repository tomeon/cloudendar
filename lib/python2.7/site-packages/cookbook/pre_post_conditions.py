"""From http://wiki.python.org/moin/PythonDecoratorLibrary

Provide pre-/postconditions as function decorators.

Example usage:

  >>> def in_ge20(inval):
  ...    assert inval >= 20, 'Input value < 20'
  ...
  >>> def out_lt30(retval, inval):
  ...    assert retval < 30, 'Return value >= 30'
  ...
  >>> @precondition(in_ge20)
  ... @postcondition(out_lt30)
  ... def inc(value):
  ...   return value + 1
  ...
  >>> inc(5)
  Traceback (most recent call last):
    ...
  AssertionError: Input value < 20
  >>> inc(29)
  Traceback (most recent call last):
    ...
  AssertionError: Return value >= 30
  >>> inc(20)
  21

You can define as many pre-/postconditions for a function as you
like. It is also possible to specify both types of conditions at once:

  >>> @conditions(in_ge20, out_lt30)
  ... def add1(value):
  ...   return value + 1
  ...
  >>> add1(5)
  Traceback (most recent call last):
    ...
  AssertionError: Input value < 20

An interesting feature is the ability to prevent the creation of
pre-/postconditions at function definition time. This makes it
possible to use conditions for debugging and then switch them off for
distribution.

  >>> debug = False
  >>> @precondition(in_ge20, debug)
  ... def dec(value):
  ...   return value - 1
  ...
  >>> dec(5)
  4
"""

__all__ = [ 'precondition', 'postcondition', 'conditions' ]

DEFAULT_ON = True

def precondition(precondition, use_conditions=DEFAULT_ON):
    return conditions(precondition, None, use_conditions)

def postcondition(postcondition, use_conditions=DEFAULT_ON):
    return conditions(None, postcondition, use_conditions)

class conditions(object):
    __slots__ = ('__precondition', '__postcondition')

    def __init__(self, pre, post, use_conditions=DEFAULT_ON):
        if not use_conditions:
            pre, post = None, None

        self.__precondition  = pre
        self.__postcondition = post

    def __call__(self, function):
        # combine recursive wrappers (@precondition + @postcondition == @conditions)
        pres  = set( (self.__precondition,) )
        posts = set( (self.__postcondition,) )

        # unwrap function, collect distinct pre-/post conditions
        while type(function) is FunctionWrapper:
            pres.add(function._pre)
            posts.add(function._post)
            function = function._func

        # filter out None conditions and build pairs of pre- and postconditions
        conditions = map(None, filter(None, pres), filter(None, posts))

        # add a wrapper for each pair (note that 'conditions' may be empty)
        for pre, post in conditions:
            function = FunctionWrapper(pre, post, function)

        return function

class FunctionWrapper(object):
    def __init__(self, precondition, postcondition, function):
        self._pre  = precondition
        self._post = postcondition
        self._func = function

    def __call__(self, *args, **kwargs):
        precondition  = self._pre
        postcondition = self._post

        if precondition:
            precondition(*args, **kwargs)
        result = self._func(*args, **kwargs)
        if postcondition:
            postcondition(result, *args, **kwargs)
        return result

def __test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    __test()
