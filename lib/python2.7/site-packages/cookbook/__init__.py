#
# Copyright John Reid 2006, 2007, 2008, 2012
#


import pkg_resources

__doc__ = pkg_resources.resource_string(__name__, "README")
__license__ = pkg_resources.resource_string(__name__, "LICENSE")
__release__, __svn_revision__ = pkg_resources.resource_string(__name__, "VERSION").strip().split('-')
__major_version__, __minor_version__, __release_version__ = map(int, __release__.split('.'))
__version__ = '%d.%d' % (__major_version__, __minor_version__)

def version_string():
    """Return the release and svn revision as a string."""
    return '%s %s' % (__release__, __svn_revision__)



from bunch import *
from bidirectional_map import *
from const import *
from dicts import *
from enum import *
from equivalence import *
from groupby import *
from lru_cache import *
from named_tuple import *
from pre_post_conditions import *
from process_priority import *
from reverse_dict import *


