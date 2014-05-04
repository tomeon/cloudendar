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
parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[tools.argparser])


# CLIENT_SECRETS is name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret. You can see the Client ID
# and Client secret on the APIs page in the Cloud Console:
# <https://cloud.google.com/console#/project/377626221408/apiui>
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'data/client_secrets.json')


# Set up a Flow object to be used for authentication.
# Add one or more of the following scopes. PLEASE ONLY ADD THE SCOPES YOU
# NEED. For more information on using scopes please see
# <https://developers.google.com/+/best-practices>.
FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS,
    scope=[
            #'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/calendar.readonly',
        ],
        message=tools.message_if_missing(CLIENT_SECRETS))


def seconds_since_epoch(datetime_obj):
    return time.mktime(datetime_obj.timetuple())


def seconds_since_epoch_str(datetime):
    return seconds_since_epoch(parse(datetime))


def convert_ranges_dict(convert_func, ranges_dict):
    ranges_list = [(convert_func(t.get('start')), convert_func(t.get('end'))) for t in ranges_dict]
    return map(lambda e: {'start': e[0], 'end': e[0]}, ranges_list)


get_ranges_sse = functools.partial(convert_ranges_dict, seconds_since_epoch_str)


get_ranges_datetime_obj = functools.partial(convert_ranges_dict, parse)


def get_calendars(freebusy):
    return freebusy.get('calendars')


def free_times(start, end):
    return None


def freebusy_query(timeMin, timeMax, items, timeZone=None, groupExpansionMax=None,
                   calendarExpansionMax=None):
    query = {}
    suffix = "@onid.oregonstate.edu"
    try:
        query['timeMin'] = timeMin
        query['timeMax'] = timeMax
        query['items'] = [{'id': onid + suffix} for onid in items]

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
    disc_interval = IntervalSet()
    for l, r in pairs:
        disc_interval.add(Interval(l, r))
    return disc_interval


def interval_set_to_list(interval_set):
    return map(lambda elem: (elem.lower, elem.upper), interval_set)


"""
Pre:
    -   'calendars' is a list of calendars of the same structure as those
        extracted from the dictionary returned by
        apiclient.discovery.build().freebusy.query().execute()
    -   'statuses' is either 'free' or 'busy'
    -   'convert_func' is a function that takes a list of dictionaries of the
        form {'start': <RFC3339 string>, 'busy': <RFC3339 string>} and returns
        a list of dictionaries of the same form.
"""
def convert_calendars(calendars, statuses, convert_func):
    if not statuses:
        raise ValueError("'statuses' list must contain either 'free', 'busy', or both")

    for status in statuses:
        if status not in ['free', 'busy']:
            raise KeyError("'status' argument must be either 'free' or 'busy'")

        # Copy the calendar so that we don't accidentally modify something we
        # shouldn't
        calendars_local = calendars.copy()

        for account, range_dict in calendars_local.iteritems():
            # Access the list of busy times
            times = range_dict.get(status)

            # If the set of busy times is empty, then the account holder is free
            # for the entire interval
            if times == []:
                continue

            # Build a list of busy ranges expressed as a dictionary with 'start'
            # and 'end' keys and values expressed as seconds since the epoch
            try:
                converted_ranges = convert_func(times)
            except:
                print("Invalid conversion function")

            # Replace original range_dictionary with new range_dictionary
            #range_dict[status] = new_range_dict
            range_dict[status] = converted_ranges

    return calendars_local


def free_ranges_overlaps(calendars):
    calendars_local = calendars.copy()

    overlaps = IntervalMap()

    for account, ranges_dict in calendars_local.iteritems():
        # Access the list of free times
        free_ranges = ranges_dict.get('free')

        # Create a pyicl set containing the name of the account
        # N.B. The second set of parentheses around 'account', and the comma
        # afterward, are mandatory!
        print(account)
        account_set = Set((account,))

        # Create list of tuples containing endpoints of free ranges
        free_ranges_tuples = map(lambda e: (e.get('start'), e.get('end')), free_ranges)


        for free_range_tuple in free_ranges_tuples:
            print(free_range_tuple)
            segment = overlaps.Segment(Interval(free_range_tuple), account_set)
            #print(segment)
            overlaps.add(segment)
        #    overlaps.add(overlaps.Segment(Interval(free_range_tuple), account_set))

    #for segment in overlaps:
    #    when = segment.interval
    #    who = segment.value
    #    print '%s: %s\n' % (when, ', '.join(who))



def calendars_free(timeMin, timeMax, calendars):
    calendars_local = calendars.copy()

    # Get start and end points expressed as seconds since the Epoch
    timeMin_sse = seconds_since_epoch_str(timeMin)
    timeMax_sse = seconds_since_epoch_str(timeMax)

    # Create an IntervalSet with these times as endpoints
    whole_range = IntervalSet(Interval(timeMin_sse, timeMax_sse))

    # For each account in the calendar, transform the list of busy times into a
    # list of free times
    for account, ranges_dict in calendars_local.iteritems():
        # Access the list of busy times
        busy_ranges_dict = ranges_dict.get('busy')

        # If the set of busy times is empty, then the account holder is free
        # for the entire interval
        if busy_ranges_dict == []:
            busy_ranges_intervals = IntervalSet()
        else:
            # Build a list of busy ranges expressed as a dictionary with 'start'
            # and 'end' keys and values expressed as seconds since the epoch
            busy_ranges_sse = get_ranges_sse(busy_ranges_dict)
            busy_ranges_sse_tuples = map(lambda e: (e.get('start'), e.get('end')),
                                        busy_ranges_sse)

            # Turn this list into an IntervalSet
            busy_ranges_intervals = disc_interval_set(busy_ranges_sse_tuples)

        # Take the difference of the whole range with the set of busy times -
        # this is an IntervalSet containing the account holder's free intervals
        # with units in seconds since the Epoch
        free_ranges_intervals = whole_range - busy_ranges_intervals
        free_ranges_sse_tuples = interval_set_to_list(free_ranges_intervals)

        # Get list of tuples of datetimes in UTC
        free_ranges = map(lambda e: (datetime.utcfromtimestamp(e[0]),
                                     datetime.utcfromtimestamp(e[1])),
                          free_ranges_sse_tuples)

        # Map list of tuples to dictionary in the form of the 'busy' dictionary
        # 'busy_ranges_dict'
        free_ranges_dict = map(
            lambda e: {'start': generate(e[0].replace(tzinfo=pytz.utc)),
                       'end': generate(e[1].replace(tzinfo=pytz.utc)),},
            free_ranges)

        # Store the dictionary of free times in the same dictionary as the
        # dictionary of busy times
        ranges_dict['free'] = free_ranges_dict

    # calendar_local now contains lists of both free and busy ranges for each
    # account holder
    return calendars_local


def main(argv):
    # Parse the command-line flags.
    flags = parser.parse_args(argv[1:])

    # Check that user has a graphical display available.
    # If not, set the flag that causes a link to the
    # auth page to be displayed on the command line
    if not os.environ.get('DISPLAY'):
        flags.noauth_local_webserver = True

    # If the credentials don't exist or are invalid run through the native client
    # flow. The Storage object will ensure that if successful the good
    # credentials will get written back to the file.
    storage = file.Storage(os.path.join(os.path.dirname(__file__), 'data/sample.dat'))
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(FLOW, storage, flags)

    # Create an httplib2.Http object to handle our HTTP requests and authorize it
    # with our good Credentials.
    http = httplib2.Http()
    http = credentials.authorize(http)

    # Construct the service object for the interacting with the Calendar API.
    service = discovery.build('calendar', 'v3', http=http)

    try:
        start_time = datetime.utcnow()
        end_time = start_time + relativedelta(hours=+1)
        start_time_str = generate(start_time.replace(tzinfo=pytz.utc))
        end_time_str = generate(end_time.replace(tzinfo=pytz.utc))

        freebusy_api = service.freebusy()
        query = freebusy_query(
            start_time_str, end_time_str, ['schreibm', 'looneyka', 'clampitc'])
        request = freebusy_api.query(body=query)
        freebusy = request.execute()
        calendars = get_calendars(freebusy)
        new_calendars = calendars_free(start_time_str, end_time_str, calendars)
        print(new_calendars)

        new_calendars = convert_calendars(new_calendars, ['free', 'busy'],
                                          get_ranges_datetime_obj)

        #pprint.pprint(new_calendars)

        #free_ranges_overlaps(new_calendars)

    except client.AccessTokenRefreshError:
        print ("The credentials have been revoked or expired, please re-run"
            "the application to re-authorize")


# For more information on the Calendar API you can visit:
#
#   https://developers.google.com/google-apps/calendar/firstapp
#
# For more information on the Calendar API Python library surface you
# can visit:
#
#   https://developers.google.com/resources/api-libraries/documentation/calendar/v3/python/latest/
#
# For information on the Python Client Library visit:
#
#   https://developers.google.com/api-client-library/python/start/get_started
if __name__ == '__main__':
    main(sys.argv)
