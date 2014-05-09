from urllib import urlopen

from bs4 import BeautifulSoup

import re

# Copy all of the content from the provided web page
webpage = urlopen('http://feeds.huffingtonpost.com/huffingtonpost/LatestNews').read()

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
