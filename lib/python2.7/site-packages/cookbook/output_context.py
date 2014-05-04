#
# Copyright John Reid 2010
#


"""
Code to implement output contexts.
"""

import os, glob, logging
from cookbook.cache_decorator import PickledMemoize



def ensure_dir_exists(dir):
    "Make sure the given directory exists."
    if not os.path.exists(dir):
        os.makedirs(dir)



class OutputContext(object):
    """
    An output context. Uses the Borg design pattern:
    http://code.activestate.com/recipes/66531-singleton-we-dont-need-no-stinkin-singleton-the-bo/
    """
    
    __shared_state = {}
    
    def __init__(self):
        "Construct."
        self.__dict__ = self.__shared_state

    
    def setUp(self, root_dir, tag=None):
        "Set up the output context, i.e. tell it where any output should go."
        self.root_dir = root_dir
        if None == tag: # if no tag supplied, work out which is next.
            existing_output_dirs = glob.glob(os.path.join(self.root_dir, '[0-9][0-9][0-9][0-9]'))
            if len(existing_output_dirs):
                existing_tags = map(os.path.basename, existing_output_dirs)
                existing_tags.sort()
                tag = '%04d' % (int(existing_tags[-1]) + 1)
            else:
                tag = '0000'
        self.tag = tag
        self.output_dir = os.path.join(self.root_dir, self.tag)
        logging.info('Setting up output context to send output to %s', self.output_dir)
        self.cache_dir = os.path.join(self.output_dir, 'cache')
        ensure_dir_exists(self.cache_dir)


    def _check_is_setUp(self):
        try:
            self.cache_dir
        except AttributeError:
            logging.warning('output_context.setUp() never called, using default settings.')
            self.setUp('output')
    
    
    def cache_filename(self, object_name):
        "@return: A callable that returns a filename suitable for caching an object."
        def filename():
            self._check_is_setUp()
            return os.path.join(self.cache_dir, '%s.pickle' % object_name)
        return filename
    
    
    def caching_decorator(self, name, dump_on_update=False):
        "@return: A decorator that caches the results of methods."
        def decorator(fn):
            return PickledMemoize(fn, self.cache_filename(name), dump_on_update=dump_on_update)
        return decorator


output_context = OutputContext()
"An object we can use to access the output context."


if '__main__' == __name__:
    logging.basicConfig(level=logging.DEBUG)
    
    logging.debug('Defining cached function.')
    @output_context.caching_decorator('square', dump_on_update=True)   
    def square(x):
        return x**2
    
    logging.debug('Setting up output context.')
    output_context.setUp('output')
        
    logging.debug('Calling cached function.')
    print square(9)
    print square(9)
    
