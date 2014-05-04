#
# Copyright John Reid 2009, 2013
#

"""
Code to set up logging and options in a workflow
"""

import cPickle, logging, os
from .cache_decorator import cachedmethod, pickled_cached_method


cache_dir = None


def get_cache_dir():
    return cache_dir


def output_cached_method(name):
    "@return: Decorator that stores output of methods in cache directory."
    return pickled_cached_method(os.path.join(get_cache_dir(), '%s.pickle' % name))


def caching_decorator(cache_name):
    "@return: A decorator that caches the results of the function."
    #print 'Calling caching_decorator: %s' % cache_name
    def decorator(func):
        "Decorates by caching (pickling) the results of the function."
        @cachedmethod
        def wrapper():
            "Wrapper to cache results of a function."
            pickle_file = os.path.join(get_cache_dir(), '%s.pickle' % cache_name)
            try:
                results = cPickle.load(open(pickle_file, 'rb'))
                logging.info('Unpickled %s', pickle_file)
            except:
                logging.info('Could not unpickle %s; executing %s()', pickle_file, func.__name__)
                results = func()
                logging.info('Pickling %s', pickle_file)
                cPickle.dump(results, open(pickle_file, 'wb'), protocol=2)
            return results
        return wrapper
    return decorator


def logger_has_file_handler(logger):
    "@return: Does the logger have a file handler already?"
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            return True
    return False


def ensure_dir_exists(directory):
    "Makes a directory if it does not already exist."
    if not os.access(directory, os.X_OK):
        logging.info('Making directory: %s', directory)
        os.makedirs(directory)


def log_attributes(module):
    "Log the attributes in a module."
    for attr in dir(module):
        if not attr.startswith('_'):
            logging.info('%30s : %s', attr, str(getattr(module, attr)))


def output_file(options, filename):
    """A path to the given filename in the output directory.
    """
    return os.path.join(options.output_dir, filename)


def initialise_workflow(options):
    """
    Initialise the workflow:

    - initialise basic logging
    - over-ride options with any defined in options.output_dir/options.py
    - set up logging to file in options.output_dir
    - log option values
    - set up a cache directory to store cached output
    """
    #
    # Initialise basic logging (if not already done so)
    #
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)-15s:%(levelname)s: %(message)s')

    #
    # Over-ride options with any defined in the output directory
    #
    options_py_file = os.path.join(options.output_dir, 'options.py')
    if os.path.exists(options_py_file):
        logging.info('Overriding options from %s', options_py_file)
        execfile(options_py_file)
    else:
        logging.info('No options file: "%s" - using default options.', options_py_file)

    ensure_dir_exists(options.output_dir)

    #
    # Now we have an output directory set up logging to a file
    #
    log_file = os.path.join(options.output_dir, 'log.txt')
    if not logger_has_file_handler(logging.getLogger()):
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))
        logging.getLogger().addHandler(file_handler)

    logging.info('Options are:')
    log_attributes(options)

    logging.info('Initialising cache directory.')
    # the directory to put cached results into
    global cache_dir
    cache_dir = os.path.join(options.output_dir, 'cache')
    ensure_dir_exists(cache_dir)
    logging.info('cache_dir: %s', get_cache_dir())
