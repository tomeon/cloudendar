#
# Copyright John Reid 2008,2009
#


"""
Utility functions for simple logging operations.
"""


import logging, os, sys, functools
from contextlib import contextmanager


def basic_config(level=logging.INFO):
    """
    Set up simple logging to stderr.
    """
    logging.basicConfig(level=level)


def add_logging_to_file(filename, mode='w'):
    """
    Add logging to named file.
    """
    file_log = logging.FileHandler(filename, mode)
    logging.getLogger('').addHandler(file_log)


def add_file_handler(filename, logger=None, handlerType=logging.FileHandler):
    """Adds a file handler to the logger if it does not already exist. 
    If no logger is given, defaults to root logger. Returns the handler if one is
    created.
    """
    if None == logger:
        logger = logging.getLogger()
    for handler in logger.handlers:
        if hasattr(handler, 'baseFilename') and os.path.samefile(handler.baseFilename, filename):
            logger.info(
                'Already have a %s logging to %s, not adding %s.',
                type(handler).__name__,
                filename,
                handlerType.__name__
            )
            break
    else:
        handler = handlerType(filename)
        logger.addHandler(handler)
        logger.info('Added %s logging to %s.', handlerType.__name__, filename)
        return handler
        

def log_to_file_and_stderr(filename, level=logging.INFO, mode='w'):
    """
    Set up simple logging to named file.
    """
    if len(logging.getLogger().handlers) < 2:
        basic_config(level)
        add_logging_to_file(filename, mode)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        for handler in logging.getLogger().handlers:
            handler.setFormatter(formatter)


def log_exception(level=logging.ERROR, logger=None):
    """
    Log the current exception.
    """
    if None == logger:
        logger = logging.getLogger('')
    logger.log(level, '%s: %s', sys.exc_info()[0].__name__, sys.exc_info()[1])



def log_exception_traceback(level=logging.ERROR, logger=None):
    """
    Log the traceback for the current exception.
    """
    import traceback, cStringIO
    tb = cStringIO.StringIO()
    traceback.print_tb(sys.exc_info()[2], file=tb)
    if None == logger:
        logger = logging.getLogger('')
    #logger.log(level, 'Caught exception whilst in function: %s()', fn.__name__)
    logger.log(level, 'Traceback:\n%s', tb.getvalue())


def create_log_exceptions_decorator(level=logging.ERROR, log_traceback=True, logger=None):
    """
    @return: Decorator to log exceptions raised inside a function.
    """
    if None == logger:
        logger = logging.getLogger('')

    def decorator(fn):
        @functools.wraps(fn)
        def wrapped(*args, **kwds):
            try:
                return fn(*args, **kwds)
            except:
                if log_traceback:
                    log_exception_traceback(level, logger)
                log_exception(level, logger)
                raise
        return wrapped

    return decorator


@contextmanager
def use_handler(logger, handler):
    """
    A context manager that can be used to temporarily add a handler to a logger.
    
    Typical usage:
    
        from cookbook.simple_logging import use_handler
        from logging import getLogger, FileHandler, Formatter
        
        with use_handler(getLogger(), FileHandler('output.log')) as handler:
            handler.setFormatter(Formatter("%(asctime)s:%(levelname)s: %(message)s"))
            <do some stuff>
    """
    logger.addHandler(handler)
    yield handler
    logger.removeHandler(handler)
    
    
if '__main__' == __name__:
    logging.basicConfig(level=logging.INFO)
    
    class A(object):
        @create_log_exceptions_decorator()
        def method(self):
            raise RuntimeError('error')

    @create_log_exceptions_decorator()
    def exception_raiser():
        "Test exception function."
        raise RuntimeError('Error occurred')

    print 'Fn name: %s' % exception_raiser.__name__
    print 'Fn docstring: %s' % exception_raiser.__doc__
    try:
        exception_raiser()
    except:
        logging.warning('exception_raiser() raised exception')
    try:
        A().method()
    except:
        logging.warning('A().method() raised exception')
