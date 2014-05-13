import datetime
import simplejson as json

import npyscreen
from npyscreen import wgtextbox
import curses

# google calendar datetime format
GCAL_DATETIME_FORMAT = '%Y-%m-%dT%X-07:00'  # offset to PST

# user-friendly datetime format
USER_DATETIME_FORMAT = '%x at %X'

# text list separator
SEPARATOR = ';'

# for appending to usernames
EMAIL_POSTFIX = '@onid.oregonstate.edu'

# test data
test_users = ['kayla', 'looney']


def get_free_busy(user, start_time, end_time):
    """Retrieves free/busy information from Google's v3 Calendar API for the
    specified user.
    :type start_time: datetime
    :type end_time: datetime
    :type user: str
    :return: A dictionary of usernames -> list of busy start/end time pairs
    :rtype: dict
    """
    if False: # TODO: get this up and running with the OSU g-cal, worked with normal g-cal
        from oauth2client.client import flow_from_clientsecrets
        from oauth2client.file import Storage
        from oauth2client.tools import run
        from apiclient.discovery import build
        import httplib2

        # format the date strings

        start_time = start_time.strftime(GCAL_DATETIME_FORMAT)
        end_time = end_time.strftime(GCAL_DATETIME_FORMAT)

        # connection building/credentials
        flow = flow_from_clientsecrets('client_secret.json',
                                       scope='https://www.googleapis.com/auth/calendar',
                                       redirect_uri='http://example.com/auth_return')
        storage = Storage('calendarsettings.dat')
        credentials = run(flow, storage)
        http = httplib2.Http()
        http = credentials.authorize(http)
        service = build('calendar', 'v3', http=http)
        freebusy_api = service.freebusy()
        request = freebusy_api.query(body={'items': [{'id': 'kaylalooney@gmail.com'}], 'timeMin': start_time, 'timeMax': end_time, 'timeZone': 'America/Los_Angeles'})
        freebusy = request.execute()
    else:
        # use test data for now
        with open('calendar_freebusy_example.json') as f:
            freebusy = json.loads(f.read())

    # convert the start/end times to datetimes
    calendars = freebusy['calendars']
    busy = calendars[list(calendars.keys())[0]]['busy']

    for interval in busy:
        interval['start'] = datetime.datetime.strptime(interval['start'], GCAL_DATETIME_FORMAT)
        interval['end'] = datetime.datetime.strptime(interval['end'], GCAL_DATETIME_FORMAT)

    return busy


def get_user_busy_intervals(users, start_time, end_time):
    """Retrieve the free and busy time information for users.
    :type start_time: datetime
    :type end_time: datetime
    :param users: The users to get free/busy information for.
    :type users: list
    :return: Dictionary of users and free/busy lists.
    :rtype: dict
    """
    busy = dict()

    for user in users:
        busy[user] = get_free_busy(user, start_time, end_time)

    return busy


def busy_to_free(user_interval_dictionary, start_time, end_time):
    # TODO: NOT YET IMPLEMENTED! is there an optimal way to do it?
    for user in user_interval_dictionary:
        intervals = user_interval_dictionary[user]
        new_intervals = []

        """idx = 0
        while idx < len(intervals):
            interval = intervals[idx]
            new_interval = dict()
            if idx > 0:
                last_interval = intervals[idx - 1]
            if idx == 0:
                # first interal
                if start_time == interval['start']:
                    #idx += 1 # no free time for the first interval
                    continue
                else:
                    #new_interval['start'] = start_time
                    #new_interval['end'] = interval['start']
                    pass
            elif idx == len(intervals) - 1:
                # last interval
                pass
            else:
                # somewhere in the middle
                pass

            new_intervals.append(new_interval)"""

    return user_interval_dictionary


def get_user_free_intervals(users, start_time, end_time):
    busy = get_user_busy_intervals(users, start_time, end_time)
    free = busy_to_free(busy, start_time, end_time)
    return free


def time_between_times(time, start_time, end_time):
    if (time - start_time).total_seconds() > 0:
        if (end_time - time).total_seconds() > 0:
            return True
    return False


def is_available(busy_intervals, start_time, end_time):
    """For every interval, check if the start or end time lands in a busy
    interval or if the busy interval lands in the start or end time.
    """
    for interval in busy_intervals:
        busy_start = interval['start']
        busy_end = interval['end']

        if time_between_times(start_time, busy_start, busy_end):
            # if the start of the meeting is in a busy period
            return False
        if time_between_times(end_time, busy_start, busy_end):
            # if the end of the meeting is in a busy period
            return False
        if time_between_times(busy_start, start_time, end_time):
            # if the start of the busy period is in the meeting period
            return False
        if time_between_times(busy_end, start_time, end_time):
            # if the end of the busy period is in the meeting period
            return False

    return True


def find_possible_attendees(users, start_time, end_time):
    user_interval_dictionary = get_user_busy_intervals(users, start_time, end_time)
    attendees = list(user_interval_dictionary.keys())

    for user in user_interval_dictionary:
        if not is_available(user_interval_dictionary[user], start_time, end_time):
            attendees.remove(user)

    return attendees


def get_pretty_intervals(user_interval_dictionary):
    for user in user_interval_dictionary:
        intervals = user_interval_dictionary[user]
        for interval in intervals:
            interval['start'] = interval['start'].strftime(USER_DATETIME_FORMAT)
            interval['end'] = interval['end'].strftime(USER_DATETIME_FORMAT)

    return user_interval_dictionary


class Validator(object):
    @staticmethod
    def validate_number(widget, min, max):
        """Validates a widget's value according to a min and max, and sets it to
        the closest value if the current value is invalid.
        """
        number = min
        current_value = widget.value
        if current_value.isdigit():
            number = int(current_value)
            if number < min:
                number = min
            elif number > max:
                number = max

        widget.value = str(number)


class UserAutocomplete(npyscreen.Autocomplete):
    def auto_complete(self, input):
        current_users = self.value.split(';')
        current_user = current_users[-1]

        choices = []
        for user in test_users:
            if current_user and current_user in user:
                choices.append(user)

        if choices:
            new_users = current_users[:-1]
            choice = self.get_choice(choices)
            new_users.append(choices[choice])
            self.value = ';'.join(new_users)
        else:
            curses.beep()


class TitleUserAutocomplete(npyscreen.TitleText):
    _entry_type = UserAutocomplete


class AvailabilityList(npyscreen.MultiLine):
    def __init__(self, *args, **kwargs):
        super(AvailabilityList, self).__init__(*args, **kwargs)

    def display_value(self, vl):
        return '{}'.format(vl)


class ActionControllerUserAvailability(npyscreen.ActionControllerSimple):
    """There are two general modes for querying attendance and availability.
    Attendance mode provides the user with a list of the users who are available
    for the entire specified window of time.
    Availability mode provides the user with a list of the free times that the
    specified users would all be available.
    """
    def create(self):
        self.parent.mode = 'attendance'
        self.add_remove_user_command = ':user '
        self.add_action('^' + self.add_remove_user_command + '.*',
                        self.set_users,
                        live=False)
        self.add_action('^:start', self.set_start_time, live=False)
        self.add_action('^:end', self.set_end_time, live=False)

        self.add_action('^:attendance', self.set_mode, live=False)
        self.add_action('^:availability', self.set_mode, live=False)

    def set_mode(self, command_line, widget_proxy, live):
        self.parent.mode = command_line[1:]
        self.update_values()
        self.parent.update_status()

    def set_users(self, command_line, widget_proxy, live):
        command = command_line[len(self.add_remove_user_command):]

        if command in self.parent.users:
            # remove the username if it's already present
            self.parent.users.remove(command)
        else:
            # add the username to the list
            self.parent.users.append(command)

        # redraw the status
        self.update_values()
        self.parent.update_status()

    def update_values(self):
        if len(self.parent.users) == 1:
            user_intervals_dict = get_user_free_intervals(
                self.parent.users,
                self.parent.start_time,
                self.parent.end_time
            )
            pretty_user_intervals = get_pretty_intervals(user_intervals_dict)
            values = pretty_user_intervals[self.parent.users[0]]

        elif self.parent.mode == 'attendance':
            values = self.display_attendance_mode()
        elif self.parent.mode == 'availability':
            values = self.display_availability_mode()

        self.parent.wMain.values = values
        self.parent.wMain.display()

    def display_attendance_mode(self):
        values = find_possible_attendees(self.parent.users,
                                         self.parent.start_time,
                                         self.parent.end_time)
        if not values:
            message = 'No users are available during the specified window.'
            values.append(message)

        values.insert(0, 'Currently in attendance mode, showing who can attend at a specified time. (:availability to switch)')
        return values

    def display_availability_mode(self):
        values = []

        if not values:
            message = 'No open windows of time shared by all users during the specified window.'
            values.append(message)

        values.insert(0, 'Currently in availability mode, showing windows of time all users are available. (:attendance to switch)')
        return values

    def set_start_time(self, command_line, widget_proxy, live):
        def set_parent_start_time(user_time):
            """Callback for the datetime form to call."""
            self.parent.start_time = user_time

            # check if the times are incoherent
            if (self.parent.end_time - self.parent.start_time).total_seconds() < 0:
                # start time is after end time, shift end time
                self.parent.end_time = self.parent.start_time + datetime.timedelta(hours=1)

            # update the interface
            self.parent.update_status()

        # update the date/time form with the callback
        date_time_form = self.parent.parentApp.getForm('DATETIME')
        date_time_form.set_callback(set_parent_start_time)

        # let the user select the time
        self.parent.parentApp.switchForm('DATETIME')

    def set_end_time(self, command_line, widget_proxy, live):
        def set_parent_end_time(user_time):
            """Callback for the datetime form to call."""
            self.parent.end_time = user_time

            # check of times are incoherent
            if (self.parent.end_time - self.parent.start_time).total_seconds() < 0:
                # end time is before start time, shift start time
                self.parent.start_time = self.parent.end_time - datetime.timedelta(hours=1)

            self.parent.update_status()

        # update the date/time form with the callback
        date_time_form = self.parent.parentApp.getForm('DATETIME')
        date_time_form.set_callback(set_parent_end_time)

        # let the user select the time
        self.parent.parentApp.switchForm('DATETIME')


class UserAvailabilityForm(npyscreen.FormMuttActiveTraditional):
    MAIN_WIDGET_CLASS = AvailabilityList
    ACTION_CONTROLLER = ActionControllerUserAvailability

    def __init__(self, *args, **kwargs):
        super(UserAvailabilityForm, self).__init__(*args, **kwargs)

        # initial user list is empty
        self.users = []

        # initial start time
        self.start_time = datetime.datetime.now()
        self.start_time = self.start_time.replace(
            hour=(self.start_time.hour + 1) % 24,
            minute=0,
            second=0
        )

        # initial end time
        self.end_time = datetime.datetime.now() + datetime.timedelta(hours=6)
        self.end_time = self.end_time.replace(
            hour=self.end_time.hour,
            minute=0,
            second=0
        )

        # update the initial status
        self.update_status()

    def update_status(self):
        if self.users:
            if len(self.users) == 1:
                # if there is only one user, the application defaults to just
                # showing their open windows of time during the specified window
                self.wStatus1.value = 'Open times'
            else:
                # there is more than one user, so tailor the text to the current
                # mode
                self.wStatus1.value = 'User {}'.format(self.mode)
            self.wStatus1.value += ' of ' + ','.join(self.users)
        else:
            self.wStatus1.value = 'Enter :user <user> to get started.'

        self.wStatus1.value += '    (:user <user> to add/remove a user)'
        self.wStatus1.value += '  mode: {}'.format(self.mode)

        status = 'Time Window - '
        status += 'Start: ' + self.start_time.strftime(USER_DATETIME_FORMAT)
        status += '    '
        status += 'End: ' + self.end_time.strftime(USER_DATETIME_FORMAT)
        status += '    (:start/:end to set)'
        self.wStatus2.value = status

        self.wStatus1.display()
        self.wStatus2.display()


class DateTimeForm(npyscreen.Form):
    """Display a date and time entry form. Call a callback passing the datetime
    when the user presses OK.
    """

    def create(self):
        self.date = self.add(npyscreen.TitleDateCombo, name='What day are you interested in?', allowPastDate=False)
        self.hour = self.add(npyscreen.TitleText, name='What hour?', value='0')
        self.minute = self.add(npyscreen.TitleText, name='What minute?', value='0')
        self.callback = None

    def afterEditing(self):
        Validator.validate_number(self.hour, 0, 23)
        Validator.validate_number(self.minute, 0, 60)

        if self.callback:
            # get the datetime and call the callback with it
            user_time = datetime.datetime(
                year=self.date.value.year,
                month=self.date.value.month,
                day=self.date.value.day,
                hour=int(self.hour.value),
                minute=int(self.minute.value)
            )
            self.callback(user_time)

        self.parentApp.switchFormPrevious()

    def set_callback(self, callback):
        """Sets the callback that passes the user's datetime as the argument."""
        self.callback = callback


class MainForm(npyscreen.Form):
    def create(self):
        self.name = 'OSU Scheduling System'
        self.add(npyscreen.TitleFixedText, name='Welcome to the OSU Scheduling System.', value='')
        self.single_user_availability_button = self.add(npyscreen.ButtonPress, name='User Availability')
        self.single_user_availability_button.whenPressed = lambda: self.parentApp.switchForm('USERAVAILABILITY')


class SchedulerApplication(npyscreen.NPSAppManaged):
    def onStart(self):
        self.registerForm('MAIN', MainForm())
        self.registerForm('USERAVAILABILITY', UserAvailabilityForm())
        self.registerForm('DATETIME', DateTimeForm())


if __name__ == '__main__':
    app = SchedulerApplication()
    app.run()
