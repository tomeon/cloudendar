#
# Copyright John Reid 2011, 2013
#

"""
Generic setup code shared between tests.
"""

import logging, os, sys

def init_test_env(file, level=logging.DEBUG):
    "Initialise test envirnoment. @return: Directory file is in."
    logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s")
    logging.getLogger('').addHandler(logging.FileHandler('%s.log' % os.path.splitext(os.path.basename(file))[0]))
    logging.info('Command line: %s', ' '.join(sys.argv))

def append_to_path(dir):
    logging.info('Appending to sys.path: %s', dir)
    sys.path.append(dir) # stempy

def update_path_for_tests():
    dir = os.path.dirname(__file__)
    #append_to_path(os.path.normpath(os.path.abspath(os.path.join(dir, '..', 'Python')))) # PyICL
    #append_to_path(os.path.normpath(os.path.abspath(os.path.join(dir, '..', '..', '..', 'Python', 'Cookbook')))) # cookbook
    #append_to_path(os.path.normpath(os.path.abspath(os.path.join(dir, '..', '..', '..', 'Infpy', 'python')))) # Infpy
    #append_to_path(os.path.normpath(os.path.abspath(os.path.join(dir, '..', '..', '..', 'PyICL', 'Python')))) # PyICL

