"""Command-line skeleton application for Calendar API.
Usage:
    $ python sample.py

You can also get help on all the command-line flags the program understands
by running:

    $ python sample.py --help

"""

import argparse
import functools
import httplib2
import os
import pprint
import pytz
import sys
import time

from apiclient import discovery
from dateutil.relativedelta import relativedelta
from datetime import datetime
from oauth2client import client, file, tools
from pyicl import Interval, IntervalMap, IntervalSet, Set
from pyrfc3339 import generate, parse


# text list separator
SEPARATOR = ';'

# for appending to usernames
EMAIL_POSTFIX = '@onid.oregonstate.edu'

# Parser for command-line arguments.
parser = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 parents=[tools.argparser])


# CLIENT_SECRETS is name of a file containing the OAuth 2.0 information for
# this application, including client_id and client_secret. You can see the
# Client ID and Client secret on the APIs page in the Cloud Console:
# <https://cloud.google.com/console#/project/377626221408/apiui>
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__),
                              'data/client_secrets.json')


# Set up a Flow object to be used for authentication.
# Add one or more of the following scopes. PLEASE ONLY ADD THE SCOPES YOU
# NEED. For more information on using scopes please see
# <https://developers.google.com/+/best-practices>.
FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS,
    scope=[
        # Calendar API authorization
        #'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.readonly',
        # Directory API authorization
        'https://www.googleapis.com/auth/admin.directory.device.chromeos',
        'https://www.googleapis.com/auth/admin.directory.device.chromeos.readonly',
        'https://www.googleapis.com/auth/admin.directory.device.mobile',
        'https://www.googleapis.com/auth/admin.directory.device.mobile.action',
        'https://www.googleapis.com/auth/admin.directory.device.mobile.readonly',
        'https://www.googleapis.com/auth/admin.directory.group',
        'https://www.googleapis.com/auth/admin.directory.group.member',
        'https://www.googleapis.com/auth/admin.directory.group.member.readonly',
        'https://www.googleapis.com/auth/admin.directory.group.readonly',
        'https://www.googleapis.com/auth/admin.directory.notifications',
        'https://www.googleapis.com/auth/admin.directory.orgunit',
        'https://www.googleapis.com/auth/admin.directory.orgunit.readonly',
        'https://www.googleapis.com/auth/admin.directory.user',
        'https://www.googleapis.com/auth/admin.directory.user.alias',
        'https://www.googleapis.com/auth/admin.directory.user.alias.readonly',
        'https://www.googleapis.com/auth/admin.directory.user.readonly',
        'https://www.googleapis.com/auth/admin.directory.user.security',
    ],
    message=tools.message_if_missing(CLIENT_SECRETS))


def convert_ranges_dict(convert_func, ranges_list):
    """
    Pre:
        - convert_func is a function that takes datetime strings of the sort
          returned by a freebusy query and returns some value (usually a
          transformation of the string into some other representation of
          datetime).
        - ranges_list is a list of dictionaries of the sort that is returned as the
          'busy' member of a freebusy query dictionary.  At minimum, it must
          have values for 'start' and 'end'.
    Post:
        - Returns a list of dictionaries, each of which has keys 'start' and
          'end'.
    """
    ranges_list = [(convert_func(t.get('start')), convert_func(t.get('end')))
                   for t in ranges_list]
    return map(lambda e: {'start': e[0], 'end': e[1]}, ranges_list)


get_ranges_datetime_obj = functools.partial(convert_ranges_dict, parse)
""" Wrapper for convert_ranges_dict() for use in map(), filter(), or another
such function that requires a function of one argument """


def get_calendars(freebusy):
    return freebusy.get('calendars')


# TODO: work on exception handling
def build_freebusy_query(timeMin, timeMax, onids, timeZone=None,
                         groupExpansionMax=None, calendarExpansionMax=None,
                         suffix=EMAIL_POSTFIX):
    """
    (Adapted in part from Google's Freebusy docs at
    https://developers.google.com/google-apps/calendar/v3/reference/freebusy/query)

    Pre :
        - timeMin and timeMax are datetime strings of the form '%Y-%m-%dT%X',
          which is the format required by freebusy queries.
        - onids is a list of ONID usernames.
        - timeZone is a string representing a time zone.  Defaults to UTC.
        - groupExpansionMax is the maximal number of calendar identifiers to be
          provided for a single group.  Optional.  An error will be returned
          for a group with more members than this value.
        - calendarExpansionMax is the maximal number of calendars for which FreeBusy information is to be
          provided. Optional.
    Post:
        - Success: returns a freebusy query object
        - Failure: raises an exception if timeMin and timeMax are not specified

    """
    query = {}
    try:
        query['timeMin'] = timeMin
        query['timeMax'] = timeMax
        query['items'] = [{'id': onid + suffix} for onid in onids]

        if timeZone is not None:
            query['timeZone'] = timeZone
        if groupExpansionMax is not None:
            query['groupExpansionMax'] = groupExpansionMax
        if calendarExpansionMax is not None:
            query['calendarExpansionMax'] = calendarExpansionMax

        return query

    except:
        print("Must specify timeMin and timeMax")


def disc_interval_set(pairs):
    """
    Pre:
        - pairs is a list of two-tuples.
    Post:
        Returns an IntervalSet containing each of the value sets in 'pairs'.
    """
    disc_interval = IntervalSet()
    for l, r in pairs:
        disc_interval.add(Interval(l, r))
    return disc_interval


def interval_set_to_list(interval_set):
    """
    Pre:
        - interval_set is an IntervalSet.
    Post:
        - returns a list of two-tuples for each interval in interval_set.
    """
    return map(lambda elem: (elem.lower, elem.upper), interval_set)


def convert_calendars(calendars, statuses, convert_func):
    """ Pre:
        -   'calendars' is a list of calendars of the same structure as those
            extracted from the dictionary returned by
            apiclient.discovery.build().freebusy.query().execute()
        -   'statuses' is either 'free' or 'busy'
        -   'convert_func' is a function that takes a list of dictionaries of
            the form {'start': <RFC3339 string>, 'busy': <RFC3339 string>} and
            returns a list of dictionaries of the same form.
    """
    if not statuses:
        raise ValueError(
            "'statuses' list must contain either 'free', 'busy', or both")

    # Copy the calendar so that we don't accidentally modify something we
    # shouldn't
    calendars_local = calendars.copy()

    for status in statuses:
        if status not in ['free', 'busy']:
            raise KeyError("'status' argument must be either 'free' or 'busy'")

        for account, range_dict in calendars_local.iteritems():
            # Access the list of busy times
            times = range_dict.get(status)

            # If the set of busy times is empty, then the account holder is
            # free for the entire interval
            if times == []:
                continue

            # Build a list of busy ranges expressed as a dictionary with
            # 'start' and 'end' keys and values expressed as seconds since
            # the epoch
            try:
                converted_ranges = convert_func(times)
            except:
                print("Invalid conversion function")

            # Replace original range_dictionary with new range_dictionary
            range_dict[status] = converted_ranges

    return calendars_local


def ranges_overlaps(calendars, status):
    """
    Pre:
        - calendars :
    """
    if status not in ['free', 'busy']:
        raise KeyError("'status' argument must be either 'free' or 'busy'")

    calendars_local = calendars.copy()

    overlaps = IntervalMap()

    for account, ranges_dict in calendars_local.iteritems():
        # Access the list of free times
        free_ranges = ranges_dict.get(status)

        # Create a pyicl set containing the name of the account
        # N.B. The second set of parentheses around 'account', and the comma
        # afterward, are mandatory!
        account_set = Set((account,))

        # Create a map segment for each free interval the account holder has,
        # and add it to the map
        for free_range in free_ranges:
            segment = overlaps.Segment(Interval(free_range.get('start'),
                                                free_range.get('end')),
                                       account_set)
            overlaps.add(segment)

    # 'overlaps' now contains a mapping of free times to sets of accounts.
    # 'overlaps', when iterated, will yield each segment.  These segments
    # have the members 'interval' (which holds the time interval) and value
    # (which holds the names of the accounts free at that time).  The start
    # time for each interval can be accessed by <segment name>.interval.lower,
    # and the end time by <segment name>.interval.upper.
    return overlaps


def calendars_free(timeMin, timeMax, calendars):
    calendars_local = calendars.copy()

    # Create an IntervalSet with these times as endpoints
    whole_range = IntervalSet(Interval(timeMin, timeMax))

    # For each account in the calendar, transform the list of busy times into a
    # list of free times
    for account, ranges_dict in calendars_local.iteritems():
        # Access the list of busy times
        busy_ranges = ranges_dict.get('busy')

        # If the set of busy times is empty, then the account holder is free
        # for the entire interval
        if busy_ranges == []:
            busy_ranges_intervals = IntervalSet()
        else:
            # Build a list of busy ranges expressed as a dictionary with
            # 'start' and 'end' keys
            busy_ranges_tuples = map(lambda e: (e.get('start'), e.get('end')),
                                     busy_ranges)

            # Turn this list into an IntervalSet
            busy_ranges_intervals = disc_interval_set(busy_ranges_tuples)

        # Take the difference of the whole range with the set of busy times -
        # this is an IntervalSet containing the account holder's free intervals
        # with units in seconds since the Epoch
        free_ranges_intervals = whole_range - busy_ranges_intervals
        free_ranges = interval_set_to_list(free_ranges_intervals)

        # Map list of tuples to dictionary in the form of the 'busy' dictionary
        # 'busy_ranges_dict'
        free_ranges_dict = map(lambda e: {'start': e[0], 'end': e[1]},
                               free_ranges)

        # Store the dictionary of free times in the same dictionary as the
        # dictionary of busy times
        ranges_dict['free'] = free_ranges_dict

    # calendar_local now contains lists of both free and busy ranges for each
    # account holder
    return calendars_local


def execute_freebusy_query(service, start_time, end_time, users):
    try:
        start_time_str = generate(start_time)
        end_time_str = generate(end_time)

        freebusy_api = service.freebusy()
        query = build_freebusy_query(
            start_time_str, end_time_str, users)
        request = freebusy_api.query(body=query)
        freebusy = request.execute()

    except client.AccessTokenRefreshError:
        print ("The credentials have been revoked or expired, please re-run"
               "the application to re-authorize")

    calendars = get_calendars(freebusy)

    # Convert busy intervals from strings to datetime objects
    new_calendars = convert_calendars(calendars, ['busy'],
                                      get_ranges_datetime_obj)

    # Add list of free times to calendars
    return calendars_free(start_time, end_time, new_calendars)


def init_google_api(
    api_name,
    api_version,
    auth_host_name=None,
    noauth_local_webserver=None,
    auth_host_port=None,
    logging_level=None,
    storage_path=os.path.join(os.path.dirname(__file__), 'data/sample.dat')
):
    """
    For the calendar API, api_name is 'calendar' and api_version is 'v3'.
    For the directory API, api_name is 'admin' and api_version is 'directory_v1'
    """
    # Parse the command-line flags.
    # What to do about this?  It's unlikely that this module is going to be
    # invoked as a script.  Can we build the parser object without passing
    # sys.argv?  Maybe just an empty list?  Or does tools.run_flow accept other
    # structures for the 'flags' argument?
    flags = parser.parse_args(sys.argv[1:])

    if auth_host_name is not None:
        pass

    # Check that user has a graphical display available.
    # If not, set the flag that causes a link to the
    # auth page to be displayed on the command line
    if not os.environ.get('DISPLAY'):
        flags.noauth_local_webserver = True

    # If the credentials don't exist or are invalid run through the native
    # client flow. The Storage object will ensure that if successful the good
    # credentials will get written back to the file.
    storage = file.Storage(storage_path)
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(FLOW, storage, flags)

    # Create an httplib2.Http object to handle our HTTP requests and authorize
    # it with our good Credentials.
    http = httplib2.Http()
    http = credentials.authorize(http)

    # Construct the service object for the interacting with the Calendar API.
    return discovery.build(api_name, api_version, http=http)


def main(argv):
    # Parse the command-line flags.
    flags = parser.parse_args(argv[1:])

    # Check that user has a graphical display available.
    # If not, set the flag that causes a link to the
    # auth page to be displayed on the command line
    if not os.environ.get('DISPLAY'):
        flags.noauth_local_webserver = True

    # If the credentials don't exist or are invalid run through the native
    # client flow. The Storage object will ensure that if successful the good
    # credentials will get written back to the file.
    storage = file.Storage(os.path.join(os.path.dirname(__file__),
                                        'data/sample.dat'))
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(FLOW, storage, flags)

    # Create an httplib2.Http object to handle our HTTP requests and authorize
    # it with our good Credentials.
    http = httplib2.Http()
    http = credentials.authorize(http)

    # Construct the service object for the interacting with the Calendar API.
    service = discovery.build('calendar', 'v3', http=http)

    try:
        start_time = datetime.utcnow().replace(tzinfo=pytz.utc)
        end_time = start_time + relativedelta(hours=+1)
        end_time.replace(tzinfo=pytz.utc)
        start_time_str = generate(start_time)
        end_time_str = generate(end_time)

        freebusy_api = service.freebusy()
        query = build_freebusy_query(
            start_time_str, end_time_str, ['schreibm', 'looneyka', 'clampitc'])
        request = freebusy_api.query(body=query)
        freebusy = request.execute()

        calendars = get_calendars(freebusy)

        # Convert busy intervals from strings to datetime objects
        new_calendars = convert_calendars(calendars, ['busy'],
                                          get_ranges_datetime_obj)

        # Add list of free times to calendars
        new_calendars = calendars_free(start_time, end_time, calendars)

        # Create a PyICL map of free intervals and users free during those
        # intervals
        free_ranges_interval_map = ranges_overlaps(new_calendars, 'free')

        for segment in free_ranges_interval_map:
            when = segment.interval
            who = segment.value
            print('Users free during listed periods: %s, %s'
                  % (when, ', '.join(who)))

    except client.AccessTokenRefreshError:
        print ("The credentials have been revoked or expired, please re-run"
               "the application to re-authorize")


if __name__ == '__main__':
    main(sys.argv)
