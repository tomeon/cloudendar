# Screen scrape script that will get the OSU catalog and dump the contents in a SQLLite DB
# Author Charles Clampitt for team Project with Kayla Looney and Matt Schreiber
# Spring 2014 CS419

#Import urllib so we can fetch URL's 
from urllib import urlopen

# BeautifulSoup does not have to be installed on the system on the bs4 dir must be present in the code base
# and the following will import to BeautifulSoup modules needed to do screenscraping
from bs4 import BeautifulSoup

# Import for regular expressions
import re

# Copy all of the content from the provided web page
webpage = urlopen('http://catalog.oregonstate.edu/CourseSearcher.aspx?chr=abcdeg').read()

# Grab everything that lies between the title tags using a REGEX
patFinderTitle = re.compile('')

# Grab the link to the original article using a REGEX
patFinderLink = re.compile('')

# Grab the content for the article using a REGEX
patFinderContent = re.compile('')

# Store all of the titles and links found in 2 lists
findPatTitle = re.findall(patFinderTitle,webpage)

findPatLink = re.findall(patFinderLink,webpage)

findPatContent = re.findall(patFinderContent,webpage)

# Create an iterator that will cycle through the first 16 articles and skip the first few
listIterator = []

listIterator[:] = range(2,26)

soup2 = BeautifulSoup(webpage)

#print soup2.findAll("title")

titleSoup = soup2.findAll("title")

linkSoup = soup2.findAll("link")

contentSoup = soup2.findAll("content")

for i in listIterator:
    print titleSoup[i]
    print linkSoup[i]
    print contentSoup[i]
    print i
    print "\n"
