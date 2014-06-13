#!/usr/bin/env python2
from __future__ import print_function   # For handy log_diaging to stderr

import inspect
import itertools
import linecache
import os
import pwd
import requests
import simplejson as json
import sys


ONID_LNAME_MINLEN = 6
ONID_LNAME_MAXLEN = 7
ONID_DUP_MAX = 3
ONID_QUERY_URL = "http://web.engr.oregonstate.edu/~schreibm/get_onid.php"

EMAIL_POSTFIX = '@onid.oregonstate.edu'


def get_username():
    return pwd.getpwuid(os.getuid()).pw_name


def get_email(postfix=EMAIL_POSTFIX):
    return "{0}{1}".format(get_username(), postfix)


def get_onid(fname, lname):
    def _generate_onids(fname, lname):
        # Grab list consisting of first letter and first two letters of first
        # name
        ftrunc = [fname[0], fname[0:2]]

        # Figure out how long the section of last name should be
        if(len(lname) < ONID_LNAME_MAXLEN):
            maxlen = len(lname) + 1
        else:
            maxlen = ONID_LNAME_MAXLEN + 1

        # Construct a list of permutations of last name segments, from
        # 'ONID_LNAME_MINLEN' to 'maxlen' characters long.
        ltrunc = [lname[0:r] for r in range(ONID_LNAME_MINLEN, maxlen)]

        # These lists will get mixed together
        combo = [ftrunc, ltrunc]

        mutations = list(itertools.product(*combo))
        mutations = list(itertools.chain.from_iterable(
            map(lambda e: [e[0] + e[1], e[1] + e[0]], mutations)))
        mutations += list(itertools.chain.from_iterable(
            map(lambda e: [e + str(x) for x in range(2, ONID_DUP_MAX + 1)],
                mutations)))

        for onid in mutations:
            yield onid

    fname = fname.lower()
    lname = lname.lower()

    for onid in _generate_onids(fname, lname):
        try:
            passwd = pwd.getpwnam(onid)
            pw_fname, pw_lname = passwd.pw_gecos.lower().split()
            if len(pw_lname) > 2:
                pw_lname = ''.join(pw_lname)
            if pw_fname.find(fname[:3]) == -1 or pw_lname.find(lname) == -1:
                continue
            return onid
        except:
            continue


def get_onids(users):
    ret = []
    for user in users:
        fname = users[0].get('fname')
        lname = users[0].get('lname')
        user['onid'] = get_onid(fname, lname)
        ret.append(user)
    return ret


def request_onids(users):
    url = ONID_QUERY_URL
    payload = users
    headers = {'content-type': 'application/json'}

    response = requests.post(url, data=json.dumps(payload), headers=headers)
    ret = json.loads(response.content)

    for user in ret:
        if user.get('onid') == 'None':
            user['onid'] = None

    return ret


def request_onid(fname, lname):
    return request_onids([{'fname': fname, 'lname': lname}])[0]


def pretty_date(dt):
    return dt.strftime("%m/%d/%Y %I:%M:%S %p")


# Thanks to user Apogentus at
# http://stackoverflow.com/questions/14519177/python-exception-handling-line-number
# for info about prettily printing exceptions
def log_err(msg):
    exc_type, exc_obj, tb = sys.exc_info()
    frame = tb.tb_frame
    lineno = tb.tb_lineno
    filename = frame.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, frame.f_globals)
    print("{} :: {} :: {}: {}: {} ".format(filename, lineno, line.strip(), msg,
                                           exc_obj), file=sys.stderr)


# Thanks to user junjanes at
# http://stackoverflow.com/questions/6810999/how-to-determine-file-function-and-line-number
# for info re: the 'inspect' module
def log_diag(msg):
    caller_fr = inspect.stack()[1]
    frame = caller_fr[0]
    info = inspect.getframeinfo(frame)
    print("{} :: {} :: {}: {}".format(info.filename, info.function,
                                      info.lineno, msg), file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        print(get_onid(sys.argv[1], sys.argv[2]))
    else:
        print("ERROR")
