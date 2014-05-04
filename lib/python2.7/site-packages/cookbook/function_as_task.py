#
# Copyright John Reid 2010
#

"""
Code to run a function as a task. Useful to make sequential code parallel.

Uses pickling to pass arguments and get result back.
"""


import sys


class CalledProcessError(Exception):
    """This exception is raised when a process run by check_call() or
    check_output() returns a non-zero exit status.
    The exit status will be stored in the returncode attribute;
    check_output() will also store the output in the output attribute.
    """
    def __init__(self, returncode, cmd, output=None):
        self.returncode = returncode
        self.cmd = cmd
        self.output = output
    def __str__(self):
        return "Command '%s' returned non-zero exit status %d. Output was:\n%s" % (self.cmd, self.returncode, self.output)


def check_output(*popenargs, **kwargs):
    r"""Run command with arguments and return its output as a byte string.

    If the exit code was non-zero it raises a CalledProcessError.  The
    CalledProcessError object will have the return code in the returncode
    attribute and output in the output attribute.

    The arguments are the same as for the Popen constructor.  Example:

    >>> check_output(["ls", "-l", "/dev/null"])
    'crw-rw-rw- 1 root root 1, 3 Oct 18  2007 /dev/null\n'

    The stdout argument is not allowed as it is used internally.
    To capture standard error in the result, use stderr=STDOUT.

    >>> check_output(["/bin/sh", "-c",
    ...               "ls -l non_existent_file ; exit 0"],
    ...              stderr=STDOUT)
    'ls: non_existent_file: No such file or directory\n'
    """
    from subprocess import Popen, PIPE
    if 'stdout' in kwargs:
        raise ValueError('stdout argument not allowed, it will be overridden.')
    process = Popen(stdout=PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        raise CalledProcessError(retcode, cmd, output=output)
    return output







def run_as_subprocess(module_name, function_name, *args, **kwargs):
    """
    Run the named function as a subprocess.
    """
    import tempfile, subprocess, cPickle, os, logging
    _args_handle, args_filename = tempfile.mkstemp()
    _result_handle, result_filename = tempfile.mkstemp()
    try:
        to_pickle = args, kwargs
        cPickle.dump(to_pickle, open(args_filename, 'w'))
        python_code = "from %s import %s as fn; from cookbook.function_as_task import do_task; do_task(fn, '%s', '%s')" % (
            module_name, function_name, args_filename, result_filename
        )
        args = ('python%d.%d' % sys.version_info[:2], '-c', python_code)
        logging.debug('Running: %s', ' '.join(args))
        check_output(args=args, stderr=subprocess.STDOUT)
        #subprocess.check_call(args=args)
        result = cPickle.load(open(result_filename))
    finally:
        os.remove(args_filename) # no longer needed
        os.remove(result_filename) # no longer needed
    return result



def do_task(fn, args_filename, result_filename):
    "Actually do the task."
    import cPickle
    args, kw_args = cPickle.load(open(args_filename))
    result = fn(*args, **kw_args)
    cPickle.dump(result, open(result_filename, 'w'))





def sleep(time_to_sleep):
    "Function to test run function as task functionality."
    import time, logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logging.info('Sleeping for %d seconds', time_to_sleep)
    time.sleep(time_to_sleep)
    logging.info('Finished sleeping for %d seconds', time_to_sleep)
    return "Slept for %d seconds" % time_to_sleep




def log_exception(exc_type, exc_obj, exc_tb):
    "Log an exception. Can be used as replacement for sys.excepthook."
    import traceback, logging
    exc_info = traceback.format_exception(exc_type, exc_obj, exc_tb)
    for l in exc_info:
        logging.error(l.strip())





def create_worker_on_queue(q, do_work):
    "Create a worker function that takes tasks off a queue."
    import sys, logging
    def worker():
        while True:
            item = q.get()
            try:
                result = do_work(item)
                logging.debug('Got result: %s', result)
            except:
                logging.error('Caught exception in queue worker')
                log_exception(*sys.exc_info())
            q.task_done()
    return worker




def create_queue(num_worker_threads, do_work):
    "Create a queue and a number of worker threads on it."
    from Queue import Queue
    from threading import Thread
    q = Queue()
    for _ in range(num_worker_threads):
        t = Thread(target=create_worker_on_queue(q, do_work))
        t.setDaemon(True)
        t.start()
    return q



if '__main__' == __name__:
    import logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    # the function that does our work
    def do_work(time_to_sleep):
        return run_as_subprocess("cookbook.function_as_task", "sleep", time_to_sleep)

    # create a queue
    num_worker_threads = 2
    q = create_queue(num_worker_threads, do_work)

    # put some work on it
    for item in range(5):
        q.put(item)

    # block until all tasks are done
    q.join()
