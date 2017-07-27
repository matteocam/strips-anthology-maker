from bs4 import BeautifulSoup
import urllib
import calendar
import os.path
from subprocess import call

urlbase = 'http://doonesbury.slate.com/strip/archive' # Fmt: YYYY/M(M)/D(D)

def urlFromDate(y, m, d):
    return "%s/%d/%d/%d" % (urlbase, y, m, d)

def grabStripForDate(y, m, d):
    picName = 'pics/%d-%d-%d.jpg' % (y, m, d)

    # Check if pic already exists
    if os.path.isfile(picName):
        print 'Skipping %d-%d-%d.jpg - It already exists' % (y, m, d)
        return
    
    print 'Downloading %d-%d-%d' % (y, m, d)
    # Parse html
    r = urllib.urlopen(urlFromDate(y,m,d)).read()
    soup = BeautifulSoup(r, 'html.parser')
    strip = soup.find("img", {"class":"strip"})
    imgSrcUrl = strip['src']

    # Check strip is good
    if 'strip_error' in imgSrcUrl:
        print "Bad date: %d-%d-%d" % (y, m, d)
        return

    # Download strip
    urllib.urlretrieve(imgSrcUrl, picName)

    # Reduce size of image
    # Command (using ImageMagick) is "mogrify -strip -quality 70%  img.jpg"
    call("/opt/local/bin/mogrify -strip -quality 70% " + picName, shell=True)
    

def grabStripsForRange(yStart = 1986, yEnd = 2017):
    for y in range(yStart, yEnd+1):
        for m in range(1,12+1):
            daysInMonth = calendar.monthrange(y, m)[1]
            for d in range(1,daysInMonth+1):
                grabStripForDate(y, m, d)
            


# Example Usage: grabStripsForRange(1987, 1988)
