from BeautifulSoup import BeautifulSoup, Tag
from collections import namedtuple
from datetime import datetime
import calendar
import re
import os

"""Create a named tuple to hold the information about the blog post since the post itself is only information without any methods or need to change the variables within it."""

BlogInfo = namedtuple('BlogInfo', 'postTitle, postContent')
INDEX_FILE_PATH = r"D:\Programming\Python\mystatic\Static Test Site\index.html"
ARCHIVE_FILE_PATH = r"D:\Programming\Python\mystatic\Static Test Site\archive-copy.html"
MAX_INDEX_POSTS = 15

def getFileInfo(htmlCode):
    """Function takes an appropriately formatted HTML file in and returns a BlogInfo Object"""    
    #blogInfo = BlogInfo(htmlSoup.find('div','content').find('h1')), htmlSoup.find('div','content').find(
    blogPost = htmlCode.find('div','content')
    header =  blogPost.find('h1').text
    iterPoint = blogPost.h1
    content = ''
    #iterate through each sibling of the html until we come to the end of the post which is signalled by the post time p
    while True:
        iterPoint = iterPoint.nextSibling
        if iterPoint and hasattr(iterPoint, 'attrs') and iterPoint.attrs == [('class','post-time')]:
            break
        elif iterPoint:
            content += str(iterPoint)    
    blogInfo = BlogInfo(header, BeautifulSoup(content))    
    return blogInfo

def alterPostTime(htmlCode):
    """function to alter the date of posting in the blog post and returns it as a PostDate Object"""
    d = datetime.now()
    suffix = '' 
    if 4 <= d.day <= 20 or 24 <= d.day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][d.day % 10 - 1]
    postMonth = calendar.month_name[d.month]
    postDay = str(d.day) + suffix
    postYear = str(d.year)
    #search for the post information and alter it
    postTimeInfo = htmlCode.find('div','content').find('p','post-time')
    postTimeInfo.find(text=re.compile('Posted on')).replaceWith('Posted on %s %s %s by '%(postMonth, postDay, postYear))
    return htmlCode

#code to insert the post

def checkIndexPostsLength():
    """Checks how many posts there are on the index page and returns the number as an integer"""
    indexFile = open(INDEX_FILE_PATH, 'rb')
    indexCode = BeautifulSoup(indexFile.read())
    indexFile.close()
    return len(indexCode.findAll('div', 'post'))

def insertPost(blogInfo, indexPostLength, fileName):
    """function to check how many posts are there in the index file and if there are 15 then it removes the oldest post and inserts a new one.
    if there are less than 15 posts then it simply adds one to the zeroth index. The function then returns the new post title that was created."""
    indexCode = getFileAsSoup(INDEX_FILE_PATH)
    if indexPostLength == MAX_INDEX_POSTS:
        indexCode = removeOldestPost(indexCode)    
    newPost = Tag(BeautifulSoup(), 'div', attrs={'class':'post'})
    postTitle = Tag(BeautifulSoup(), 'h1')
    postLink = Tag(BeautifulSoup(), 'a', attrs={'href':'/posts/%s'%os.path.basename(fileName)})
    postLink.insert(0, blogInfo.postTitle)
    postTitle.insert(0, postLink)    
    newPost.insert(0, postTitle)
    newPost.insert(1, blogInfo.postContent)
    indexCode.find('div','content').insert(0, newPost)
    indexFile = open(INDEX_FILE_PATH, 'wb')
    indexFile.write(indexCode.prettify())
    indexFile.close()
    return postTitle

def removeOldestPost(indexCode):
    """function to remove the oldest post from the index file"""
    indexCode.findAll('div','post')[14].extract()
    return indexCode

#code to archive the post
def insertArchive(blogInfo, fileName):
    #check if the archive period exists within the archive file
    archivePeriodExists = checkArchivePeriod()
    if (not archivePeriodExists[0] or not archivePeriodExists[1]):
        archiveCode = insertArchivePeriod(archivePeriodExists)
    else:
        archiveCode = getFileAsSoup(ARCHIVE_FILE_PATH)
    soupParser = BeautifulSoup()
    #since we organise our posts in reverse chronological order we don't need to use the posttime to find the necessary tag
    archivePeriod = archiveCode.find('ul','articles')
    newPostLI = Tag(soupParser, 'li')
    newPostLink = Tag(soupParser, 'a', attrs = {'href':'posts/%s'%os.path.basename(fileName)})
    newPostLink.insert(0, blogInfo.postTitle)
    newPostLI.insert(0, newPostLink)

    archivePeriod.insert(0,newPostLI)
    archiveFile = open(ARCHIVE_FILE_PATH, 'wb')
    archiveFile.write(archiveCode.prettify())
    archiveFile.close()



def checkArchivePeriod():
    """function to go through the archive.html file to check if the relevant month and year exist under the archive.html file
    function returns a tuple of boolean values which represents whether the year and the month exist respectively"""
    archiveCode = getFileAsSoup(ARCHIVE_FILE_PATH)
    #search for the year
    postTime = datetime.now()
    yearExists = archiveCode.find('h4', text = re.compile(r"%s"%postTime.year)) is not None   
    monthExists = yearExists and (archiveCode.find('h4', text= re.compile(r"%s"%postTime.year)).parent.nextSibling.nextSibling.li.text == calendar.month_name[postTime.month])

    return (yearExists, monthExists)

def insertArchivePeriod(archivePeriodExists):
    postTime = datetime.now()
    soupParser = BeautifulSoup()
    archiveCode = getFileAsSoup(ARCHIVE_FILE_PATH)
    archiveTag = archiveCode.find('div', 'content archive-content')
    if not archivePeriodExists[0]:
        """Build a tag that follows the format of <li><h4>YEAR</h4></li><ul></ul>
        This tag goes under the div content archive-content section as the first element so that the years will be displayed in chronological order of newest to oldest"""
        yearListLI = Tag(soupParser, 'li')
        yearH4 = Tag(soupParser, 'h4')
        yearH4.insert(0, str(postTime.year))
        yearListMonthUL =Tag(soupParser, 'ul')
        yearListLI.insert(0, yearH4)
        yearListLI.insert(1, yearListMonthUL)
        yearListLI = BeautifulSoup(yearListLI)
        archiveTag.ul.insert(0, yearListLI)
    else:
        #locate the tag that we would have built if the year did not exist
        yearListMonthUL = archiveTag.find('h4', text=re.compile(str(postTime.year))).parent.nextSibling.nextSibling
        
    #construct the month list tag which is where we need to inser the new articles into
    monthLI = Tag(soupParser, 'li', attrs={'class':'month'})
    archiveFileLink = Tag(soupParser,'a', attrs={'href':'archives/%s%s.html'%(calendar.month_name[postTime.month],postTime.year)})
    archiveFileLink.insert(0, '%s'%calendar.month_name[postTime.month])
    #monthLI.insert(0, archiveFileLink)
    monthLI.insert(0, calendar.month_name[postTime.month])
    #inser the month tag we just created into the year area. Note that the months will be arranged from newest to oldest.
    yearListMonthUL.insert(0, monthLI)    
    yearListMonthUL.insert(1, Tag(soupParser, 'ul', attrs={'class':'articles'}))
    archiveCode = BeautifulSoup(archiveCode.prettify())
    return archiveCode
        
def doPost(fileName):
    htmlCode = getFileAsSoup(fileName)
    htmlCode = alterPostTime(htmlCode)
    htmlFile = open(fileName, 'wb')
    htmlFile.write(str(htmlCode))
    htmlFile.close()
    blogInfo = getFileInfo(htmlCode)
    postTitle = insertPost(blogInfo, checkIndexPostsLength(), fileName)
    
    insertArchive(blogInfo, fileName)



def getFileAsSoup(fileName):
    """Function to get the html code and return a beautifulsoup object for the other functions to work on"""
    htmlFile = open(fileName, 'rb')
    htmlCode = BeautifulSoup(htmlFile.read())
    htmlFile.close()
    return htmlCode
