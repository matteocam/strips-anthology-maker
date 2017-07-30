from bs4 import BeautifulSoup
import urllib
import calendar
import os.path
from glob import glob
from subprocess import call
from reportlab.pdfgen import canvas
from reportlab.platypus import Image
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import utils


MINVMARGIN = inch/2
FONTSIZE = 14

URLBASE = 'http://doonesbury.slate.com/strip/archive' # Fmt: YYYY/M(M)/D(D)

def urlFromDate(y, m, d):
    return "%s/%d/%d/%d" % (URLBASE, y, m, d)

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
        makePdf(y)

def getImageSize(fn):
    img = utils.ImageReader(fn)
    return img.getSize()

def captionFromFileName(fn):
    base = os.path.basename(fn)
    return os.path.splitext(base)[0]

def drawCenteredImage(c,
                      fn,
                      curY,
                      pgSize = letter,
                      minHMargin = 2*inch/3,
                      minVMargin = MINVMARGIN):
    # Compute required space to
    # have space below the image.
    # Tells to turn page if necessary (by returning -1)

    maxImgW = pgSize[0]-minHMargin*2

    captionH = FONTSIZE*1.1

    # TODO: Add text before image

    # Do computation
    origW, origH = getImageSize(fn)
    imgW = min(origW, maxImgW)
    imgH = int(float(imgW)/origW*origH)
    x = minHMargin + (maxImgW-imgW)/2

    newY = curY-captionH-imgH-minVMargin 
        
    # check everything fits
    if newY < 0:
        # new page needed
        return -1
    else:
        caption = captionFromFileName(fn)
        c.drawString(x, curY, caption)
        c.drawImage(fn, x, curY-captionH-imgH, imgW, imgH)         
        return newY


def grabWholeYear(y):
    return glob("pics/%d-*.jpg" % y) 
 
def setupCanvas(c):
    c.setStrokeColorRGB(0,0,0)
    c.setFillColorRGB(0,0,0)
    c.setFont("Helvetica", FONTSIZE)

def makePdf(y):
    files = grabWholeYear(y)

    
    title = 'Doonesboory-%d.pdf' % y
    output_filename = title
    c = canvas.Canvas(output_filename, pagesize=letter)
    setupCanvas(c)

    pgStart = letter[1]-MINVMARGIN
    curY = pgStart
    for fn in files:
        res = drawCenteredImage(c, fn, curY) 
        if res < 0:
            c.showPage()
            setupCanvas(c)
            curY = pgStart
            curY = drawCenteredImage(c, fn, curY)
            if curY < 0:
                print "What the hell!?"
                return
        else:
            curY = res
    c.save()

# Example Usage: grabStripsForRange(1987, 1988)
