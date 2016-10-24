from PIL import Image
from PIL import ImageChops
import urllib2
import os
import types

# Load empty file (needed for comparison later on)
im_empty = Image.open('landdisr_empty.gif')

# Get the NS files (download the first two only if non-existing; they're static)
if os.path.isfile('kaart.png') == False:
    with open('kaart.png','wt') as im:
        data = urllib2.urlopen('http://www.ns.nl/static/generic/2.2.0/images/storingenkaart/kaart.png')
        im.write(data.read())

if os.path.isfile('labels.png') == False:
    with open('labels.png','wt') as im:
        data = urllib2.urlopen('http://www.ns.nl/static/generic/2.2.0/images/storingenkaart/kaart.png')
        im.write(data.read())

with open('landdisr.gif','wt') as im:
    data = urllib2.urlopen('http://www.ns.nl/spoorkaart/maps/landdisr.gif')
    im.write(data.read())

# Load images
im_map = Image.open('kaart.png')
im_lab = Image.open('labels.png')
im_dis = Image.open('landdisr.gif')

# Crop landdisr image for the range that must be checked on changes (disruptions, defects)
croprange = (387, 257, 490, 304)
im_cursto = im_dis.crop(croprange)

# Get difference between images and get the smallest size of a box that would
# contain all changes. If this box is non-existing, there are no changes
diff = ImageChops.difference(im_empty,im_cursto)
if isinstance(diff.getbbox(), types.NoneType) == True:
    print('No disruptions or defects within the cropped area!')
else:
    os.system('python storing.py -a Deventer')
    os.system('python storing.py -a Almelo')
    os.system('python storing.py -a Borne')
