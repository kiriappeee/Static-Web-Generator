from BeautifulSoup import BeautifulSoup
from collections import namedtuple
from datetime import datetime
import calendar
import re

"""Create a named tuple to hold the information about the blog post since the post itself is only information without any methods or need to change the variables within it."""

BlogInfo = namedtuple('BlogInfo', 'postTitle, postContent')

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
    blogInfo = BlogInfo(header, content)

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

def doPost(fileName):
    htmlCode = getFileAsSoup(fileName)
    htmlCode = alterPostTime(htmlCode)
    htmlFile = open(fileName, 'wb')
    htmlFile.write(str(htmlCode))
    htmlFile.close()
    blogInfo = getFileInfo(htmlCode)
