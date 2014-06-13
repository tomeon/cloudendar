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
import os.path
import os
import sqlite3
import itertools
import urllib
import urlparse
from bs4 import BeautifulSoup

# Define the SQLLite3 DB to use
masterDatabase = 'data/data.db'

# Array to hold stage one scraping of the OSU catalog (Holds URL's to follow to secondary pages.)
s = [] 

# list to hold the results of secondary parse
d = []

# Array to hold URL's that had issues so that we can identify the issue later and fix
s_err = []

# Last phase of processing we hold the final constructed URL's and get data to send to oniduser table
t = []

target_name = 'error_File.txt'

# Helper to open urls  
class MyOpener(urllib.FancyURLopener):
    version = 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15'
# class MyOpener(urllib.FancyURLopener)

 
# Helper function to print tab delimited 
def printTab(text):
    print '\t', text
# def printTab(text)


# Helper function to print new line 
def printNewLine(text):
    print '\t', text
# def printNewLine(text)


# function that will write files and append inspection and diagnostics
def saveFiles(results):
   
    with open(target_name, "a") as myfile:
        myfile.write(results + "\n")

# def saveFiles(results)


# Function that will take arrays and send results to file
def saveArray(arr, b):

    if b == 0:
        filename = "onid_results_file.txt"
    else:
        filename = "results_file.txt"

    # Differnt arrays will have differnt number of columns
    numcols = len(arr[0])

    with open(filename, "w") as f:
        for x in xrange(len(arr)):
            for y in range(numcols):
                if y < numcols-1	:
                    f.write(arr[x][y] + ",")
                elif y == numcols-1:
                    f.write(arr[x][y])
            f.write("\n")
    print "\nThe " + filename + " file was saved to disk so that you may inspect for results and can be used for diagnostics.\n"
   
 # def saveArray(arr)


# Keep history of past files for inspection and diagnostics so 
# for every file we find create a new backup or the last run
# Citation: http://stackoverflow.com/questions/10107604/renaming-files-that-exist-with-python
def alternative_names(filename):
    yield filename
    base, ext = os.path.splitext(filename)
    yield base + "(Rev)" + ext
    for i in itertools.count(1):
        yield base + "(Rev %i)" % i + ext

# def alternative_names(filename)



# This function will check that we have not have any duplicates sneak past us and more than one onid id was added
# to the oniduser table
def cleanupFinal():

    print "\nFinal Cleanup in process please wait!\n"

    try:
        # Open our database
        conn = sqlite3.connect(masterDatabase)
        print "Opened database successfully";

        # We will get all records that may be duplicate and delete them keeping only the max 1       
        cmd = "delete from oniduser where rowid not in (select max(rowid) from oniduser group by onid_id);"
       
        # Exucute the drop command for teh table requested
        conn.execute(cmd);

        conn.commit()
        print "Cleanup completed successfully!"
        conn.close()
    except:
        print "An error occured while tring delete any duplicates form the oniduser table"
        exit()



# def cleanupFinal():



# Function that will drop the OSOCatalog table from our sqllite3 DB
def dropCattables(table):

    try:
        # Open our database
        conn = sqlite3.connect(masterDatabase)
        print "Opened database successfully -- Attempting to drop table";

        # Determin which table we will drop and assign sql syntax
        if table == 'cat':
            cmd = "DROP TABLE IF EXISTS OSUCatalog;"
            tt = 'OSUCatalog'
        elif table == 'user':
            cmd = "DROP TABLE IF EXISTS oniduser;"
            tt = 'oniduser'
        else:
            print "\nYou must specify a table name to be dropped. No tables were dropped and the program will now halt\n"
            exit()

        # Exucute the drop command for teh table requested
        conn.execute(cmd);

        conn.commit()
        print tt + " dropped successfully";
        conn.close()
    except:
        print "An error occured while tring to drop one or more tables from the database. System will now halt"
        exit()

# def dropCattables(table)



# This function will create a table in the database depending on the value sent in
# cat = OSUCatalog table, user = oniduser table
def createcattables(table):


    try:
        # Open our database
        conn = sqlite3.connect(masterDatabase)
        print "Opened database successfully -- Attempting to create table";

        # Determin which table we will create and assign sql syntax
        if table == 'cat':
            cmd = "CREATE TABLE OSUcatalog (id INTEGER PRIMARY KEY AUTOINCREMENT, coursecode VARCHAR(10) NOT NULL, coursenum VARCHAR(10), instructor VARCHAR(60), college VARCHAR(60), scheduleddays VARCHAR(10), starttime VARCHAR(10), endtime VARCHAR(10), startdate VARCHAR(15), enddate VARCHAR(15), term VARCHAR(10), location VARCHAR(75), type VARCHAR(100), url varchar(255));"
            tt = 'OSUCatalog'
        elif table == 'user':
            cmd = "create table oniduser(onid_id varchar(10),instructor varchar(60), college varchar(60), url varchar(255));"
            tt = 'oniduser'
        else:
            print "\nYou must specify a table name to be created. No tables were created and the program will now halt\n"
            exit()

        # Exucute the create command for the table requested
        conn.execute(cmd);

        conn.commit()
        print tt + " created successfully";
        conn.close()
    except:
        print "An error occured while tring one or more tables. System will now halt"
        exit()

   

# def createcattables(table)



# This function accepts the array holding catalog data in it and inserts into the OSUCatalog table
# For refernce the array struct is [courseSub, courseNum, instructor, dept, cday, cstarttime, cendtime, cstartdate, cenddate, term, location, classtype, url]
def populateOSUCatalog(arr):

    try:
        # Open our database
        conn = sqlite3.connect(masterDatabase)
        print "Opened database successfully -- Populating the OSUCatalog table please wait!";

        # iterate over all the rows in our array and insert then into the database

        for x in xrange(len(arr)):
            #print arr[x][0], arr[x][1], arr[x][2], arr[x][3], arr[x][4], arr[x][5], arr[x][6], arr[x][7], arr[x][8], arr[x][9], arr[x][10], arr[x][11], arr[x][12]
            cmd = "insert into OSUcatalog(coursecode,coursenum,instructor,college,scheduleddays,starttime,endtime,startdate,enddate,term,location,type,url) values(?,?,?,?,?,?,?,?,?,?,?,?,?);"
       
            # Exucute the create command for the table requested
            conn.execute(cmd, (arr[x][0], arr[x][1], arr[x][2], arr[x][3], arr[x][4], arr[x][5], arr[x][6], arr[x][7], arr[x][8], arr[x][9], arr[x][10], arr[x][11], arr[x][12]));
            conn.commit()
    
        print "Records were successfully interted into the OSUCatalog table";
        conn.close()
    except:
        print "An error occured inserting a row into the database but efforts to finsh all other rows will continue."
        pass

    
#def populateOSUCatalog(arr):



# This function will take all the onid id's found and matched positivly to a Professor or staff and save to the oniduser table
def populateOSUUsers(arr):

    
    try:
        # Open our database
        conn = sqlite3.connect(masterDatabase)
        print "Opened database successfully for oniduser record insertion -- Please wait!";

        print "Inserting " + str(len(arr)) + " Records into the oniduser table. Please wait!";

        # iterate over all the rows in our array and insert then into the database

        for x in xrange(len(arr)):
            cmd = "insert into oniduser(onid_id, instructor, college, url) values(?,?,?,?);"
       
            # Exucute the create command for the table requested
            conn.execute(cmd, (arr[x][0], arr[x][1], arr[x][2], arr[x][4]));
            conn.commit()
    
        print "Records were successfully interted into the oniduser table";
        conn.close()
    except:
        print "An error occured inserting a row into the database but efforts to finsh all other rows will continue."
        pass

    print "Populate OSUUsers had Completed!"

# def populateOSUUsers(arr):



# When parsing data I found that in order to use the on-line directory search I could not use 
# the college or the course most of the time so I use this function to match a course with a key
# that I was able to build based off hours of plugging in names in each dept and seeing what the 
# on-line directory was actually searching by. There must be a better way but I was not able to find it. 
# As a future enhancement this could be added to the DB with a set of accociations to each key. Them read 
# into an array, hash table, or other method so the query only need to hit the DB once but a larger set
# of associations over time wiht refinements could be made.
def findDeptKey(question):
  
    return {
        'ACTG': 'Business',
        'AEC': 'Economics',
        'AED': 'Agriculture',
        'AG': 'Agriculture',
        'AGRI': 'Agriculture',
        'AHE': 'Education',
        'ALS': '',
        'ANS': 'Animal',
        'ANTH': 'Anthropology',
        'AREC': 'Economics',
        'ART': 'Art',
        'AS': 'Aerospace',
        'ATS': 'Earth',
        'ALS': 'Foreign',
        'BA': 'Business',
        'BB': 'Biochem',
        'BEE': 'Engineering',
        'BI': 'Biology',
        'BIOE': 'Chem', 
        'BOT': 'Botany',
        'BRR': 'ag',
        'CBEE': 'Chem',   
        'CCE': 'civil',
        'CE': 'civil',
        'CEM': 'civil',
        'CH': 'chemistry',
        'CHE': 'chem',       
        'CHN': 'foreign',
        'COMM': 'comm',
        'CROP': 'crop',
        'CS': 'comp',
        'CSS': 'ag',
        'DHE': 'business',
        'ECE': 'comp',
        'ECON': 'economics',
        'EECS': 'comp',
        'ENG': 'lit',    
        'ENGR': 'engr',  
        'ENSC': 'earth',
        'ENT': 'crop',
        'ENVE': 'env',   
        'ES': 'ethnic',
        'EXSS': 'sport',
        'FE': 'forest',
        'FES': 'forest',
        'FILM': 'film',
        'FIN': 'business',
        'FOR': 'forest',
        'FR': 'foreign',
        'FS': 'forest',
        'FST': 'food',
        'FW': 'fish',
        'GD': 'business',
        'GEO': 'sci',    
        'GER': 'foreign',
        'GPH': 'sci',
        'GRAD': 'grad',  
        'GS': 'sci',
        'H': 'health',
        'HC': 'honor',   
        'HDFS': 'sci',
        'HHS': 'sci',
        'HORT': 'hort',    
        'HST': 'hist',
        'HSTS': 'hist',
        'IE': 'engr',
        'IEPA': 'OSU',
        'IEPG': 'OSU',
        'IEPH': 'OSU',
        'INTL': 'int',
        'IST': 'pol',
        'IT': 'foreign',
        'JCHS': '',
        'JPN': 'foreign',
        'LA': 'lit',
        'LING': 'foreign',
        'LS': '',
        'MATS': 'engr',
        'MB': 'Microbiology',
        'MCB': '',
        'ME': 'engr',
        'MFGE': 'engr',
        'MGMT': 'business',
        'MIME': 'engr',
        'MP': 'Nuclear',
        'MPP': 'pol',
        'MRKT': 'business',
        'MRM': 'sea',
        'MS': 'rotc',
        'MTH': 'math',
        'MUED': 'music',
        'MUP': 'music',
        'MUS': 'music',
        'NE': 'Nuclear',
        'NMC': 'comm',
        'NR': 'forest',
        'NS': 'rotc',
        'NUTR': 'sci',
        'OC': 'sci',
        'OEAS': 'sci',
        'PAC': 'sport',
        'PAX': 'philo',
        'PBG': 'hort',
        'PH': 'physics',
        'PHAR': 'pharm',
        'PHL': 'philo',
        'PPOL': 'pol',
        'PS': 'pol',
        'PSY': 'psycho',
        'QS': '',
        'RHP': 'rad',
        'RNG': 'animal',
        'RS': '',
        'RUS': 'foreign',
        'SED': 'edu',
        'SOC': 'soc',
        'SPAN': 'foreign',
        'SOIL': 'sci',
        'ST': 'stat',
        'SUS': 'crop',
        'TA': 'comm',
        'TCE': 'education',
        'TOX': 'toxic',
        'VMB': 'vet',
        'VMC': 'vet',
        'WGSS': 'women',
        'WLC': 'foreign',
        'WR': 'lit',
        'WRE': '',
        'WRP': '',
        'WRS': 'sci',
        'WSE': 'sci',
        'Z': 'zoo',
        }.get(question, '') 

# def findDeptKey(question):



# This function will clear array s, query distinct on instuctor and course section, lookup our search keys from findDeptKey function
# construct a URL with all required search terms embedded and save this list to array s for processing of final scrape and save to DB 
def getValidCourses(arr):

     
    # Get records from database
    try:
        # Open our database
        conn = sqlite3.connect(masterDatabase)
        print "Opened database successfully to find DISTINCT records -- Constructing final onid matching records please wait!";

        cmd = "SELECT DISTINCT instructor, coursecode, college FROM OSUCatalog;"
       
        cursor = conn.execute(cmd)
        for row in cursor:
            url = 'http://directory.oregonstate.edu/?type=search&cn='+row[0]+'&osudepartment='+findDeptKey(row[1])+'&affiliation=employee'
            onid_id = getonid(url)
            print onid_id
            if onid_id is None:
                continue
            else:
                arr.append([onid_id, row[0], row[2], findDeptKey(row[1]), url ])
        
        print "Retrieved DISTINCT records from OSUCatalog for further processing";
        conn.close()
    except:
        print "An error occued trying to open or read the records from the OSUCatalog. This application will now exit"
        exit()


    # Now we let the user know how many id's we cound and those will be committed to the Db
    print "Results are: " + str(len(arr)) + " Instructors and Staff were matched."
    
    return arr


# def getValidCourses():


# Function takes url from getValidCourses() and sees if we can extract an onid id from the page
# if so we will return the onid id else we return NOID and we will exclude this from our result
def getonid(url):
    onid_id = None       # holds the value of the extracted onid id

     # Call the custom opener
    myopener = MyOpener()
    page = myopener.open(url)
 
    # Read our page into variable
    text = page.read()
    page.close()
   
    # Soup our object
    soup = BeautifulSoup(text)
    
    try:
        pagelocate = soup.body.find(id='records')
        pagemove = pagelocate.div.dl
        
        for nn in pagemove.find_all("dt"):
            if nn.find("dt") == "ONID Username":
                print "Found a match"

        onid_id = nn.next_sibling.next_sibling.contents[0].strip()
        #print onid_id
    except:
        pagelocate = ""
        print "Not Found"
        pass

    return onid_id 

# def getonid(url):




# Process the course page for each URL. 
# NOTE: Code was left as small incremental steps so that changes can be made
# easily for changes in forms without complicated nesting
def get_course_info(url):
    courseSub = None     # Course Subject code obtained from URL
    courseNum = None     # Course number obtained from URL
    coursedec = None     # Course Description
    instructor = None    # Instructor Nanme
    dept = None          # Department 
    cday = None          # Course Day(s) (temporary)
    cstartday = None     # Course schedule Start Date
    cendday = None       # Course schedule End Date
    ctime = None         # Course Timez(s) (temporary)
    cstarttime = None    # Course Scheduled Start Time 
    cendtime = None      # Course Scheduled End Time
    cstartdate = None    # Course Start Date
    cenddate = None      # Course End Date
    term = None          # What term is this offering
    location = None      # campus
    classtype = None     # The type of class Lec, Studio, Lab, etc

    print "Starting parse of individual class links. Please wait!"


    # Call the custom opener
    myopener = MyOpener()
    page = myopener.open(url)
 
    # Read our page into variable
    text = page.read()
    page.close()

   
    # Soup our object
    soup = BeautifulSoup(text)

    # Strip all characters that we don't want to deal wiht or cause issues
    for e in soup.findAll('br'):
        e.replace_with("\t")

    # First let's process the URL and get the Course subject and course number from it 
    m = re.search('subjectcode=(.+?)&', url)  
    if m:
        courseSub = m.group(1)
        #print courseSub 

    m = re.search('coursenumber=(.+?)&', url)  
    if m:
        courseNum = m.group(1)
        #print courseNum 



    # Move to first place of interest on page and get department
    form = soup.find(id="aspnetForm")
    #print form

    # Move to and get the college department from the hyperlink
    dept = form("a")[0].text
    #print dept
    
    # Next move to the table that has the course information 
    tempmove = form.find(id="ctl00_ContentPlaceHolder1_SOCListUC1_gvOfferings")
    #print tempmove

    if tempmove is None:
        s_err.append(url)
        saveFiles(url)
        return

   
    # for each tr in this table get all data from td's and parse results. This is where we are actually 
    # parsing most of the data from the course pages.
    for alltr in tempmove.find_all("tr"):
        if alltr.find("td") is None:
            continue   #do nothing        
        else:
            try:
                # Get the term offered from the first td 
                term = alltr.find("td").contents[0].strip()
                #print term
    
                # Get the instructor from the next td
                instructor = alltr.find("td").next_sibling.contents[0].strip()
                
                # Eliminate entries and move to next if we find only staff or blank for instructor. We can not match with any onid_id
                if instructor == 'Staff':
                    continue
                elif instructor == '':
                    continue

                #print instructor 
   
                # Get day/time/date from next td. This will need to be split into parts below
                dt = alltr.find("td").next_sibling.next_sibling
                  
                daystemp = alltr.find("td").next_sibling.next_sibling.contents[0].strip()
                cstartdatetemp = alltr.find("td").next_sibling.next_sibling.contents[2].strip()
            
                #print daystemp
                #print daystemp1 

                # Split the daystemp into the parts: day(s) of week (cday), time frame of day (ctime), and class start and end dates (cstartdate, cenddate)
                cday,ctime = daystemp.split();
                #print cday
                #print ctime

                # Now split the scheuled start and and dates and times
                cstartdate, cenddate = cstartdatetemp.split('-') 
                cstarttime, cendtime = ctime.split('-')
            
                location = alltr.find("td").next_sibling.next_sibling.next_sibling.contents[0].strip()
                #print location 

                classtype = alltr.find("td").next_sibling.next_sibling.next_sibling.next_sibling.contents[0].strip()
                #print classtype 
                     

                # Assemble individual parts of course into a list to be inserted into out array
                d.append([courseSub, courseNum, instructor, dept, cday, cstarttime, cendtime, cstartdate, cenddate, term, location, classtype, url])
                #print d[0][4]
            except:
                pass
    #print d   

    print "Completed parse of individual class links!"

# get_course_info(url)



# Function that will parse the upper page of the catalog and return a list of links to follow.
# We add the &Columns=ajkmn param to the end of each string so that we will filter the 
# secondardary page to the columns we want to display which are: Term, Instructor, Day/Time/Date
# Campus and type 
def get_category_links(url):

    print "Parsing top OSU catalog page to get all links to course offerings...."

    myopener = MyOpener()
    page = myopener.open(url)
 
    text = page.read()
    page.close()
 
    soup = BeautifulSoup(text)

    mytable = soup.find_all("table", "ctl00_ContentPlaceHolder1_gvResults")
    #print mytable
    m = soup.find(id="ctl00_ContentPlaceHolder1_gvResults")
   
    for tag in m.find_all('a', href=True):
        tag['href'] = urlparse.urljoin(url, tag['href']) + '&Columns=ajkmn'
        #print tag['href']
        s.append(tag['href'])
  
    print "Parse of OSU top catalog page complete...."

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
    #testurl = 'http://catalog.oregonstate.edu/CourseDetail.aspx?subjectcode=WSE&coursenumber=515&campus=corvallis&Columns=ajkmn'
    #testurl = 'http://catalog.oregonstate.edu/CourseDetail.aspx?subjectcode=BA&coursenumber=370&campus=corvallis&Columns=ajkmn'

    global target_name
 
    # See if previous error_File.txt file exist and if so create new file name leaving old for history 
    if os.path.exists(target_name):
             target_name = next(alt_name
                           for alt_name in alternative_names(target_name)
                           if not os.path.exists(alt_name))

# First stage processing, return set 
    get_category_links(url)

# Print statement to check the results of the first stage scrape
   # for newurl in s:
    #    print newurl

    # test URL
    #get_course_info(testurl)


    progressIndicator = (len(s)-1)
    i=0
    for newurl in s:
        print newurl
        get_course_info(newurl)
        i = i +1
        print str(i) + ' of ' + str(progressIndicator) 

      
    # For inspection we save our array each run so we can check results
    saveArray(d, 1)

    # Save the results so far to the database after we clear the table first
    dropCattables("cat")
    createcattables("cat")
    populateOSUCatalog(d)
    
    # Now for every page we have collected that had valid instructor and course data on the page we 
    # will now match them against the OSU Online Directory and see if we can extract a onid ID for them.
    getValidCourses(t)

   
    # Save the resuults from the final scrape to disk for inspection later
    saveArray(t, 0)
   
    # Save the results of onid matching to database after we clear the table first
    dropCattables("user")
    createcattables("user")

    # Save all results to the oniduser table in the database. 
    populateOSUUsers(t)

    # Final scrub to ensure only one onid ID per instructor.
    cleanupFinal()

    print "\nAll records and processes have completed! You cam check the output files and the database tables for errors or to inspect results!\n"
    print "\nPROCESS COMPLETE -- GOODBYE!\n"

# main()
 
if __name__ == "__main__":
    main()
