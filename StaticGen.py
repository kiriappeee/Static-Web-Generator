from BeautifulSoup import BeautifulSoup, Tag
from collections import namedtuple
from datetime import datetime
import calendar
import re
import os

"""Create a named tuple to hold the information about the blog post since the post itself is only information without any methods or need to change the variables within it."""

BlogInfo = namedtuple('BlogInfo', 'postTitle, postContent')
INDEX_FILE_PATH = r"D:\Programming\Python\mystatic\Static Test Site\index.html"
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

def getFileAsSoup(fileName):
    """Function to get the html code and return a beautifulsoup object for the other functions to work on"""
    htmlFile = open(fileName, 'rb')
    htmlCode = BeautifulSoup(htmlFile.read())
    htmlFile.close()
    return htmlCode

def checkIndexPostsLength():
    """Checks how many posts there are on the index page and returns the number as an integer"""
    indexFile = open(INDEX_FILE_PATH, 'rb')
    indexCode = BeautifulSoup(indexFile.read())
    indexFile.close()
    return len(indexCode.findAll('div', 'post'))

def insertPost(blogInfo, indexPostLength, fileName):
    """function to check how many posts are there in the index file and if there are 15 then it removes the oldest post and inserts a new one.
    if there are less than 15 posts then it simply adds one to the zeroth index"""
    indexFile = open(INDEX_FILE_PATH, 'rb')
    indexCode = BeautifulSoup(indexFile.read())
    indexFile.close()    
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

def removeOldestPost(indexCode):
    """function to remove the oldest post from the index file"""
    indexCode.findAll('div','post')[14].extract()
    return indexCode

def doPost(fileName):
    htmlCode = getFileAsSoup(fileName)
    htmlCode = alterPostTime(htmlCode)
    htmlFile = open(fileName, 'wb')
    htmlFile.write(str(htmlCode))
    htmlFile.close()
    blogInfo = getFileInfo(htmlCode)
    insertPost(blogInfo, checkIndexPostsLength(), fileName)
