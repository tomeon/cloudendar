#
# Copyright John Reid 2010, 2013
#

"""
Code to time things.
"""

import logging, time


class SimpleTimer(object):
    "Times things."
    
    def __init__(self):
        "Initialises and starts timer."
        self.restart()
    
    def restart(self):
        "Restarts the timer."
        self.start = time.time()
    
    def duration(self):
        "@return: The duration since start."
        return time.time() - self.start

    
class Timer(object):
    """Times things and implements the context management protocol (see PEP 343).
    A typical use case would be:
    
        from cookbook.timer import Timer
        
        with Timer(msg='description of task', level=logging.INFO, logger=getLogger(__name__)) as timer:
            <do some stuff>
    """
    
    def __init__(self, msg=None, level=logging.INFO, logger=None):
        self._msg = msg
        self._level = level
        self._logger = logger and logger or logging.getLogger()
    
    def __enter__(self):
        self.timer = SimpleTimer()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.duration = self.timer.duration()
        self._report_duration_(self.duration)
        return False
    
    def _report_duration_(self, duration):
        if self._msg:
            self._logger.log(self._level, 'Timer: Took %f seconds to %s', duration, self._msg)
        else:
            self._logger.log(self._level, 'Timer: Took %f seconds', duration)
            
