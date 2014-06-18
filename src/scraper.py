#!/usr/bin/env python2

import re
import sys
import os.path
import os
import pprint
import sqlite3
import itertools
import urllib
import urllib2
import urlparse

from blessings import terminal
from bs4 import BeautifulSoup
from database import db_session, db_init
from datetime import datetime
from dateutil import parser
from dateutil.relativedelta import *
from models import Event, User


# Adapted from user Wilfred Hughes' answer at:
# http://stackoverflow.com/questions/4293460/how-to-add-custom-parameters-to-an-url-query-string-with-python
def set_query_params(url, query_dict=None, *args, **kwargs):
    scheme, netloc, path, query_string, fragment = urlparse.urlsplit(url)

    query_params = urlparse.parse_qsl(query_string)

    old_query_dict = dict(query_params)

    args_dict = {}
    if query_dict is not None:
        if isinstance(query_dict, dict):
            old_query_dict.update(query_dict)
        elif isinstance(query_dict, tuple):
            if len(args) > 0:
                args.insert(query_dict, 0)
                args_dict = dict(args)
            else:
                args = query_dict
                args_dict = {args[0]:args[1]}
            pass
        else:
            raise ValueError()

    old_query_dict.update(args_dict)
    old_query_dict.update(kwargs)

    new_query_string = urllib.urlencode(old_query_dict.items(), doseq=True)

    return urlparse.urlunsplit((scheme, netloc, path, new_query_string, fragment))


CATALOG_URL = 'http://catalog.oregonstate.edu'
SEARCHER_URL = CATALOG_URL + '/SOCSearcher.aspx'

DIRECTORY_URL = 'http://directory.oregonstate.edu/'
DIRECTORY_QUERY = {
    'type': 'search',
    'cn': '',
    'osudepartment': '',
    'affiliation': 'employee',
    'join': 'and',
}

DIRECTORY_URL_QS = set_query_params(DIRECTORY_URL, DIRECTORY_QUERY)

# Not sure what the difference is bewteen 'abcder' and 'abcdeg', but the first
# returns more results.
CATALOG_QUERY = {
    'chr': 'abcder',
    #'chr': 'abcdeg',
}

COURSE_LINK_REGEX = "ctl00_ContentPlaceHolder1_gvResults"

COURSE_QUERY = {
    # Term, StartDate, EndDate, Weeks, CRN, Sec, Instructor, Day/Time/Date
    'Columns': 'abcdfgjk',
}

COURSE_OFFERING_TABLE_ID = "ctl00_ContentPlaceHolder1_SOCListUC1_gvOfferings"


DAY_MAP = {
    'M': MO,
    'T': TU,
    'W': WE,
    'R': TH,
    'F': FR,
    'S': SA,
    'U': SU, # Is this the right letter for Sunday?
}


TERM = Terminal()


# Helper to open urls
class MyOpener(urllib.FancyURLopener):
    version = 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15'


#OPENER = MyOpener()


def get_all(url, name=None, attrs={}, recursive=True, text=None, limit=None, **kwargs):
    #page = OPENER.open(url)
    page = urllib2.urlopen(url)

    page_text = page.read()
    page.close()

    soup = BeautifulSoup(page_text)

    return soup.find_all(name, attrs, recursive, text, limit, **kwargs)


def get_category_links():
    tags = get_all(set_query_params(SEARCHER_URL, CATALOG_QUERY), 'a',
                   id=re.compile(COURSE_LINK_REGEX))

    for tag in tags:
        yield tag['href']


def get_course_mappings(path):
    url = set_query_params(CATALOG_URL + path, COURSE_QUERY)

    #page = OPENER.open(url)
    page = urllib2.urlopen(url)

    page_text = page.read()
    page.close()

    soup = BeautifulSoup(page_text)

    table = soup.find('table', id=COURSE_OFFERING_TABLE_ID)
    table_headers = map(lambda th: th.text, table.find_all('th'))

    dept = soup.find('a', href=re.compile('CollegeOverview')).text.strip()
    course = soup.find('img', alt='Course').parent.text
    strip_ws = re.compile(r'\s+')
    course = strip_ws.sub(' ', course).strip()

    for row in table.find_all('tr'):
        data = map(lambda td: td.text.strip(), row.find_all('td'))
        #dept = soup.find('a', href=re.compile('CollegeOverview')).text
        if data:
            course_dict = (dict(zip(table_headers, data)))
            course_dict['dept'] = dept
            course_dict['course'] = course
            yield course_dict


def parse_courseinfo(course):
    StartDate = course.get('StartDate')
    EndDate = course.get('EndDate')
    DayTimeDate = course.get('Day/Time/Date')
    Weeks = course.get('Weeks')
    Instructor = course.get('Instructor')
    dept = course.get('dept')

    # Convert to datetime
    #start_date = parser.parse(StartDate).date()
    #end_date = parser.parse(EndDate).date()

    # Figure out what days of the week the class occurs
    day_re = re.match('^(\w+)\s+(\d{4})-(\d{4}).*$', DayTimeDate)
    if day_re:
        days = list(day_re.group(1))
        days = map(lambda day: DAY_MAP.get(day), days)
        start_time = day_re.group(2)
        end_time = day_re.group(3)
    else:
        days = None
        start_time = None
        end_time = None

    names = re.match('^(\w+),\s+(\w+).*$', Instructor)
    if names:
        instructor = {
            'fname': names.group(2),
            'lname': names.group(1),
        }
    else:
        instructor = None

    return {
        'instructor' : instructor,
        'start_date': StartDate,
        'end_date': EndDate,
        'start_time': start_time,
        'end_time': end_time,
        'days': days,
        'weeks': Weeks,
        'dept': dept,
        'crn': course.get('CRN'),
        'sec': course.get('Sec'),
        'term': course.get('Term'),
        'course': course.get('course'),
    }


def courseinfo_to_model(info):
    course_start_date = parser.parse(info.get('start_date')).date()
    course_end_date = parser.parse(info.get('end_date')).date()

    start_time = info.get('start_time')
    end_time = info.get('end_time')

    weekdays = info.get('days')

    start_date = None
    end_date = None
    duration = None

    if weekdays is not None and start_time is not None and end_time is not None:
        start_weekday = weekdays[0]
        end_weekday = weekdays[len(weekdays) - 1]

        start_date = course_start_date + relativedelta(weekday=start_weekday(+1))
        end_date = course_end_date + relativedelta(weekday=end_weekday(-1))

        # We don't worry about extracting JUST the start time, since
        start_time_dt = datetime.strptime(start_time, '%H%M')
        end_time_dt = datetime.strptime(end_time, '%H%M')
        duration = end_time_dt - start_time_dt
        start_time = start_time_dt.time()
        end_time = end_time_dt.time()

    return Event(
        start_date=start_date,
        end_date=end_date,
        start_time=start_time,
        end_time=end_time,
        weekdays=weekdays,
        duration=duration,
        description=info.get('course'),
        crn=info.get('crn'),
        sec=info.get('sec'),
        term=info.get('term'),
    )


def build_directory_query(info, by_surname=False):
    iname = info.get('instructor')
    if by_surname:
        ret = set_query_params(
            DIRECTORY_URL_QS,
            surname=iname.get('lname')
        )
    else:
        dept = dept_raw = info.get('dept').lower()
        print("DEPARTMENT RAW: {0}".format(dept_raw))
        dept_match = re.match(r'^(?:college|school)\s+of\s+(\w+).*$', dept_raw)
        if dept_match:
            dept = dept_match.group(1)[:3]
        print("DEPARTMENT: {0}".format(dept))
        ret = set_query_params(
            DIRECTORY_URL_QS,
            cn="{0} {1}".format(iname.get('fname'), iname.get('lname')),
            osudepartment=dept
        )
    return ret


def strip_strings(elem, delim):
    text = ''
    for string in elem.stripped_strings:
        text += string + delim
    return text


def instructor_dict_to_model(idict):
    full_name = idict.get('Full Name')
    names = None
    if full_name is not None:
        names = re.match('^(\w+),\s+(\w+)\s*(\w*).*$', idict.get('Full Name'))

    if names:
        fname = names.group(2)
        mname = names.group(3)
        lname = names.group(1)
    else:
        fname = None
        mname = None
        lname = None

    phone_raw = idict.get('Office Phone Number')
    phone = None
    if phone_raw is not None:
        phone = int(filter(lambda c: c >= '0' and c <= '9', phone_raw))

    return User(
        onid=idict.get('ONID Username'),
        fname=fname,
        mname=mname,
        lname=lname,
        dept=idict.get('Department'),
        email=idict.get('Email Address'),
        phone=phone
    )


def get_instructor_info(courseinfo):
    url = build_directory_query(courseinfo)
    #page = OPENER.open(url)
    page = urllib2.urlopen(url)
    page_text = page.read()
    page.close()

    soup = BeautifulSoup(page_text)
    record = soup.find('div', {'class': 'record'})

    if record is None:
        iname = courseinfo.get('instructor')
        fname = iname.get('fname')
        lname = iname.get('lname')

        url = build_directory_query(courseinfo, by_surname=True)

        page = urllib2.urlopen(url)
        page_text = page.read()
        page.close()

        soup = BeautifulSoup(page_text)
        record = soup.find('div', {'class': 'record'})

        if record is None:
            records = soup.find('div', {'id': 'records'})

            if records is None:
                print("NO INSTRUCTOR BY THE NAME {0} {1}".format(fname, lname))
                return None

            iname_re = re.compile("^{0},\s+{1}.*$".format(lname, fname[0]))

            ilinks = records.find_all('a', dept=True, text=iname_re)
            for ilink in ilinks:
                print("POSSIBLE MATCH: {0}".format(ilink.text))
            if len(ilinks) != 1:
                print("AMBIGUOUS RESULTS; SKIPPING")
                return None

            url = DIRECTORY_URL + ilinks[0]['href']
            page = urllib2.urlopen(url)
            page_text = page.read()
            page.close()
            soup = BeautifulSoup(page_text)
            record = soup.find('div', {'class': 'record'})

    # DEBUGGING
    if record is None:
        print("NO RECORD/MULTIPLE RECORDS FOR URL {0}".format(url))
        sys.exit(1)

    idict = {}
    titles = record.find_all('dt')
    for title in titles:
        value = title.find_next_sibling('dd')
        text = strip_strings(value, '\n')

        idict[title.text.strip()] = text.strip()

    if not idict:
        print(record)

    return idict


def main():
    db_init()

    link_counter = 0
    course_counter = 0
    links = get_category_links()
    for link in links:
        link_counter += 1
        print("########## PROCESSING COURSE CATALOG ENTRY {0} ##########".format(link_counter))

        courses = get_course_mappings(link)

        for course in courses:
            course_counter += 1
            print("########## PROCESSING COURSE {0} ##########".format(course_counter))

            courseinfo = parse_courseinfo(course)
            #print("COURSE INFO: {0}".format(courseinfo))

            # Skip courses without instructors
            if(courseinfo.get('instructor')) is None:
                continue

            inames = courseinfo.get('instructor')
            #print("INSTRUCTOR: {0}".format(inames))
            #print("DEPARTMENT: {0}".format(courseinfo.get('dept')))
            instructor_query = User.query.filter(
                User.lname == inames.get('lname')).filter(
                User.fname.startswith(inames.get('fname')[0]))

            if len(instructor_query.all()) == 1:
                instructor = instructor_query.first()
            else:
                instructor = instructor_query.filter(User.dept.like(courseinfo.get('dept'))).first()

            #print("INSTRUCTOR QUERY BY NAME/DEPT: {0}".format(instructor))

            if instructor is None:
                idict = get_instructor_info(courseinfo)
                print("COURSE INFO: {0}".format(courseinfo))
                print("INSTRUCTOR INFO: {0}".format(idict))
                if not idict:
                    continue
                #print("ONID: {0}".format(idict.get('ONID Username')))
                instructor = User.query.filter(User.onid == idict.get('ONID Username')).first()

                #print("INSTRUCTOR QUERY BY ONID: {0}".format(instructor))

                if instructor is None:
                    instructor = instructor_dict_to_model(idict)
                    db_session.add(instructor)

            event = Event.query.filter(
                Event.user.any(onid=instructor.onid)) .filter(
                    Event.crn == courseinfo.get('crn')).filter(
                        Event.term == courseinfo.get('term')).filter(
                            Event.sec == courseinfo.get('sec')).first()

            if event is None:
                #print("COURSEINFO: {0}".format(courseinfo))
                event = courseinfo_to_model(courseinfo)
                instructor.events.append(event)

            db_session.commit()



    db_session.commit()
    db_session.remove()


if __name__ == '__main__':
    main()
