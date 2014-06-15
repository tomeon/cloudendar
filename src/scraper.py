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


CATALOG_URL = 'http://catalog.oregonstate.edu'
SEARCHER_URL = CATALOG_URL + '/SOCSearcher.aspx'

# Not sure what the difference is bewteen 'abcder' and 'abcdeg', but the first
# returns more results.
CATALOG_QUERY = {
    'chr': 'abcder',
    #'chr': 'abcdeg',
}

COURSE_LINK_REGEX = "ctl00_ContentPlaceHolder1_gvResults"

COURSE_QUERY = {
    'Columns' : 'abcdefghijklmnopqrstuvwxyz',
}


# Helper to open urls
class MyOpener(urllib.FancyURLopener):
    version = 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15'


# Adapted from user Wilfred Hughes' answer at:
# http://stackoverflow.com/questions/4293460/how-to-add-custom-parameters-to-an-url-query-string-with-python
def set_query_params(url, query_dict=None, *args, **kwargs):
    scheme, netloc, path, query_string, fragment = urlparse.urlsplit(url)

    query_params = urlparse.parse_qsl(query_string)

    old_query_dict = dict(query_params)

    args_dict = {}
    if isinstance(query_dict, dict):
        old_query_dict.update(query_dict)
    elif isinstance(query_dict, tuple):
        if len(args) > 0:
            args.insert(query_dict, 0)
            args_dict = dict(args)
        else:
            args = query_dict
            args_dict = {args[0]:args[1]}
    else:
        raise ValueError()

    old_query_dict.update(args_dict)
    old_query_dict.update(kwargs)

    new_query_string = urllib.urlencode(old_query_dict.items(), doseq=True)

    return urlparse.urlunsplit((scheme, netloc, path, new_query_string, fragment))


def get_all(url, name=None, attrs={}, recursive=True, text=None, limit=None, **kwargs):
    myopener = MyOpener()
    page = myopener.open(url)

    text = page.read()
    page.close()

    soup = BeautifulSoup(text)

    return soup.find_all(name, attrs, recursive, text, limit, **kwargs)


def get_category_links(url):
    print(url)
    print(COURSE_LINK_REGEX)
    #tags = get_all(url, 'a', id=re.compile(COURSE_LINK_REGEX))
    regex = re.compile(COURSE_LINK_REGEX)
    tags = get_all(url, 'a', id=regex)
    print(tags)

    for tag in tags:
        yield tag['href']


#def get_course_mappings():


def main():
    links = get_category_links(set_query_params(SEARCHER_URL, CATALOG_QUERY))
    for link in links:
        #parsed = urlparse.urlsplit(link)
        #queries = urlparse.parse_qsl(parsed.query)
        #print(queries)
        new_link = CATALOG_URL + set_query_params(link, COURSE_QUERY)
        print(new_link)


if __name__ == '__main__':
    main()
