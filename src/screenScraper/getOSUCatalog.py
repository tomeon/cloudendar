#########################################################################
#  Author: Charles C. Clampitt 
#  Created: 5/20/2014 for CS419 Senior Project
#
#  Purpose: This python script is indended to open the OSU course catalog 
#  at http://catalog.oregonstate.edu/CourseSearcher.aspx?chr=abcdeg
#  and will parse all links on the page that are relevent to a OSU course
#  Offering. Once the main catalog is parsed a secondard parse will occur 
#  for each URL extracted and these URL's will be followed to the actaul  
#  course offering page and then the contents will be parsed and added
#  to the SqlLite3 database.
#
#########################################################################

import re
import sys
import urllib
import urlparse
from bs4 import BeautifulSoup

# Array to hold stage one scraping of the OSU catalog (Holds URL's to follow to secondary pages.)
s = [] 


# Helper to open urls  
class MyOpener(urllib.FancyURLopener):
    version = 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15'
 
# Helper function to print tab delimited 
def printTab(text):
    print '\t', text


# Helper function to print new line 
def printNewLine(text):
    print '\t', text

def get_category_links(url):
    myopener = MyOpener()
    page = myopener.open(url)
 
    text = page.read()
    page.close()
 
    soup = BeautifulSoup(text)

    mytable = soup.find_all("table", "ctl00_ContentPlaceHolder1_gvResults")
    print mytable
    m = soup.find(id="ctl00_ContentPlaceHolder1_gvResults")
   
    for tag in m.find_all('a', href=True):
        tag['href'] = urlparse.urljoin(url, tag['href'])
        #print tag['href']
        s.append(tag['href'])
  

# get_category_links(url)

def process(url):
    myopener = MyOpener()
    #page = urllib.urlopen(url)
    page = myopener.open(url)
 
    text = page.read()
    page.close()
 
    soup = BeautifulSoup(text)
 
    for tag in soup.findAll('a', href=True):
        tag['href'] = urlparse.urljoin(url, tag['href'])
        #print tag['href']
        s.append(tag['href'])

# process(url)
 
def main():

# Define the URL to the OSU Catalog
    url = 'http://catalog.oregonstate.edu/CourseSearcher.aspx?chr=abcdeg'

# First stage processing, return set 
    #process(url)
    get_category_links(url)

# Print statement to check the results of the first stage scrape
    for newurl in s:
        print newurl

    

# main()
 
if __name__ == "__main__":
    main()
