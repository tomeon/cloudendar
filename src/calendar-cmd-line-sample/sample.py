# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Command-line skeleton application for Calendar API.
Usage:
  $ python sample.py

You can also get help on all the command-line flags the program understands
by running:

  $ python sample.py --help

"""

import argparse
import datetime
import functools
import httplib2
import os
import pprint
import pytz
import sys

from apiclient import discovery
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from oauth2client import file
from oauth2client import client
from oauth2client import tools
from pyrfc3339 import generate, parse
from pytz import timezone

# google calendar datetime format
GCAL_DATETIME_FORMAT = '%Y-%m-%dT%X'  # offset to PST

# user-friendly datetime format
USER_DATETIME_FORMAT = '%x at %X'


def format_datetime(fmt, dt):
    return dt.strftime(fmt)

gcal_datetime = functools.partial(format_datetime, GCAL_DATETIME_FORMAT)

# Parser for command-line arguments.
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[tools.argparser])


# CLIENT_SECRETS is name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret. You can see the Client ID
# and Client secret on the APIs page in the Cloud Console:
# <https://cloud.google.com/console#/project/377626221408/apiui>
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

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


def main(argv):
  # Parse the command-line flags.
  flags = parser.parse_args(argv[1:])

  # Check that user has graphical display available.
  # If not, set the flag that causes a link to the
  # auth page to be displayed on the command line
  if not os.environ.get('DISPLAY'):
    flags.noauth_local_webserver = True

  # If the credentials don't exist or are invalid run through the native client
  # flow. The Storage object will ensure that if successful the good
  # credentials will get written back to the file.
  storage = file.Storage('sample.dat')
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
    # text list separator
    SEPARATOR = ';'

    # for appending to usernames
    EMAIL_POSTFIX = '@onid.oregonstate.edu'

    # test data
    test_users = ['kayla', 'looney']

    start_time = datetime.utcnow()
    end_time = start_time + relativedelta(hours=+1)
    start_time_str = generate(start_time.replace(tzinfo=pytz.utc))
    end_time_str = generate(end_time.replace(tzinfo=pytz.utc))
    print(start_time_str)
    print(end_time_str)
    # sys.exit(0)

    freebusy_api = service.freebusy()
    request = freebusy_api.query(body=
                                 {'items': [{'id': 'schreibm@onid.oregonstate.edu'},
                                            {'id': 'looneyka@onid.oregonstate.edu'},
                                            {'id': 'clampitc@onid.oregonstate.edu'}],
                                  'timeMin': start_time_str,
                                  'timeMax': end_time_str,},
                                 )
    freebusy = request.execute()
    pprint.pprint(freebusy)

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
