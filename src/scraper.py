#!/usr/bin/env python2

import re
import sys
import os.path
import os
import pprint
import sqlite3
import itertools
import urllib
import urlparse

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
    'affiliation': 'any',
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
    # All options
    #'Columns' : 'abcdefghijklmnopqrstuvwxyz',
    # StartDate, EndDate, Weeks, CRN, Sec, Instructor, Day/Time/Date
    'Columns': 'bcdjk',
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


# Helper to open urls
class MyOpener(urllib.FancyURLopener):
    version = 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15'


OPENER = MyOpener()


def get_all(url, name=None, attrs={}, recursive=True, text=None, limit=None, **kwargs):
    page = OPENER.open(url)

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

    page = OPENER.open(url)

    page_text = page.read()
    page.close()

    soup = BeautifulSoup(page_text)

    table = soup.find('table', id=COURSE_OFFERING_TABLE_ID)
    table_headers = map(lambda th: th.text, table.find_all('th'))

    dept = soup.find('a', href=re.compile('CollegeOverview')).text
    course_img = soup.find('img', alt='Course')
    course = course_img.text
    print("course: {0}".format(course_img))

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
        'course': course.get('course')
    }


def courseinfo_to_model(info):
    course_start_date = parser.parse(info.get('start_date')).date()
    course_end_date = parser.parse(info.get('end_date')).date()

    start_time = info.get('start_time')
    end_time = info.get('end_time')

    weekdays = info.get('days')
    start_weekday = weekdays[0]
    end_weekday = weekdays[len(weekdays) - 1]

    start_date = course_start_date + relativedelta(weekday=start_weekday(+1))
    end_date = course_end_date + relativedelta(weekday=end_weekday(-1))

    # We don't worry about extracting JUST the start time, since
    start_time_dt = datetime.strptime(start_time, '%H%M')
    end_time_dt = datetime.strptime(end_time, '%H%M')
    duration = end_time_dt - start_time_dt

    return Event(
        start_date=start_date,
        end_date=end_date,
        start_time=start_time_dt.time(),
        end_time=end_time_dt.time(),
        weekdays=weekdays,
        duration=duration,
        description=info.get('course'),
    )


def build_directory_query(info):
    instructor = info.get('instructor')
    return set_query_params(
        DIRECTORY_URL_QS,
        cn="{0} {1}".format(instructor.get('fname'), instructor.get('lname')),
        osudepartment=info.get('dept')
    )


def remove_br_tags(elem, delim):
    text = ''


def strip_strings(elem, delim):
    text = ''
    for string in elem.stripped_strings:
        text += string + delim
    return text


def instructor_dict_to_model(idict):
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


def get_instructor_info(url):
    page = OPENER.open(url)

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

    return idict


def main():
    db_init()

    links = get_category_links()
    for link in links:
        courses = get_course_mappings(link)

        for course in courses:
            courseinfo = parse_courseinfo(course)

            dir_url = build_directory_query(courseinfo)
            idict = get_instructor_info(dir_url)

            instructor = User.query.filter(User.onid == idict.get('onid')).first()
            print(instructor)
            if instructor is None:
                instructor = instructor_dict_to_model(idict)
                db_session.add(instructor)

            print(courseinfo)
            event = courseinfo_to_model(courseinfo)
            instructor.events.append(event)
            db_session.commit()
            break

        #db_session.commit()
        break

    db_session.commit()
    db_session.remove()


if __name__ == '__main__':
    main()
