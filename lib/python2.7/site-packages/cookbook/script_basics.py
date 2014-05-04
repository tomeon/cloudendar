#
# Copyright John Reid 2010, 2011, 2012, 2013
#

"""
Code to simplify logging and options in scripts.
"""

import traceback, logging, os, sys
from contextlib import contextmanager


def prepend_to_environment_variable(var_name, value):
    "Prepend a value to colon separated list in the named environment variable."
    # prepend this directory to front of LD_LIBRARY_PATH environment variable
    existing_value = os.environ.get(var_name, '')
    if existing_value:
        new_value = '%s:%s' % (value, existing_value)
    else:
        new_value = value
    os.environ[var_name] = new_value
    logging.debug(
        'Changed environment variable %s to %s', 
        var_name, os.environ[var_name])


def log_exception(exc_type, exc_obj, exc_tb):
    "Log an exception. Used as replacement for sys.excepthook."
    exc_info = traceback.format_exception(exc_type, exc_obj, exc_tb)
    for l in exc_info:
        logging.error(l.strip())


def setup_logging(filename=None, level=logging.INFO, log_command_line=True):
    "Set up logging."
    logformat = "%(asctime)s:%(levelname)s: %(message)s"
    logging.basicConfig(level=level, format=logformat)
    formatter = logging.Formatter(logformat)
    if filename:
        file_handler = logging.FileHandler(
            '%s.log' % os.path.splitext(os.path.basename(filename))[0])
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logging.getLogger('').addHandler(file_handler)
    if log_command_line:
        logging.info('Python: %s', sys.version)
        logging.info('Command line: %s', ' '.join(sys.argv))
    sys.excepthook = log_exception  # make sure we log exceptions.
    # This doesn't work if running under ipython.


def log_options(option_parser, options):
    "Log the values of the options."
    logging.info('Options:')
    _log_options(option_parser.option_list, options)
    for option_group in option_parser.option_groups:
        _log_option_group(option_group, options)


def _log_options(option_list, options):
    for option in option_list:
        if option.dest:
            logging.info(
                '%32s: %-32s * %s', 
                option.dest, str(getattr(options, option.dest)), option.help)


def _log_option_group(option_group, options):
    logging.info(option_group.title)
    logging.info(option_group.get_description())
    _log_options(option_group.option_list, options)


def _print_var(name):
    print '%s=%s' % (name, os.environ[name])
    print '%s:\n\t' % name, os.environ[name].replace(':', '\n\t')


def show_environment():
    "Print some details about the environment python is running in."
    print 'PYTHON:\n', sys.version
    print 'PROCESS:'
    os.system('ps -ef|grep %d|grep -v "grep %d"' % (os.getpid(), os.getpid()))
    print 'CWD:\n\t', os.getcwd()
    _print_var('LD_LIBRARY_PATH')
    _print_var('PYTHONPATH')
    print 'Args:\n\t', '\n\t'.join(sys.argv)
    
    
@contextmanager
def preserve_dlopenflags(flags):
    """A context manager that temporarily sets the dlopen flags and then
    returns them to previous values.
    """
    outer_flags = sys.getdlopenflags()
    try:
        sys.setdlopenflags(flags)
        yield
    finally:
        sys.setdlopenflags(outer_flags)


@contextmanager
def boost_python_dlopen_flags():
    """A context manager that temporarily sets the dlopen flags for loading
    multiple boost.python modules and then returns them to previous values.
    """
    flags = None
    try:
        import DLFCN
        flags = DLFCN.RTLD_NOW | DLFCN.RTLD_GLOBAL
    except:
        import warnings
        warnings.warn('Do not know which dlopen flags to set.')
    if None != flags:
        with preserve_dlopenflags(flags):
            yield
    else:
        yield

