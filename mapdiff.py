from PIL import Image
from PIL import ImageChops
import urllib2
import os
import types
import requests
import sys

def pfile(fname,fpath,msg):
    # First request authorization to upload a file
    url = "https://api.pushbullet.com/v2/upload-request"
    ext = fpath.split('.')[-1]
    if ext == 'jpg':
        f_type = 'image/jpeg'
    elif ext == 'png':
        f_type = 'image/png'
    elif ext == 'pdf':
        f_type = 'application/pdf'
    else:
        print('Supported file types:\njpg, png, pdf')
        sys.exit()

    f_name = fpath.split('/')[-1]
    data = dict(file_name=f_name, file_type=f_type)
    nreq = requests.post(url, json=data, auth=(TOKEN, '')).json()
    rf_name = nreq['file_name']
    rf_type = nreq['file_type']
    rf_durl = nreq['file_url']
    rf_uurl = nreq['upload_url']

    # Upload the file_url
    f = {'file': open(fpath,'rb')}
    ureq = requests.post(rf_uurl, files=f)

    # Push the file
    url = "https://api.pushbullet.com/v2/pushes"
    data = dict(type="file", body=msg, file_name=fname, file_type = rf_type, file_url = rf_durl)
    freq = requests.post(url, json=data, auth=(TOKEN, '')).json()

# Get pushbullet token. This is necessary for the 'Send image' part
global TOKEN
with open('pb_token.txt', 'r') as file:
    TOKEN = file.read().replace('\n','')

#Creeer 'storing al gemeld' file als die niet bestaat
if os.path.isfile('storing_algehad.py') == False:
    with open('storing_algehad.py','w') as file:
        file.write('notified = []')


# Get the NS files (download the first two only if non-existing; they're static)
try:
    if os.path.isfile('kaart.png') == False:
        with open('kaart.png','wt') as im:
            data = urllib2.urlopen('http://www.ns.nl/static/generic/2.4.0/images/storingenkaart/kaart.png')
            im.write(data.read())

    if os.path.isfile('labels.png') == False:
        with open('labels.png','wt') as im:
            data = urllib2.urlopen('http://www.ns.nl/static/generic/2.4.0/images/storingenkaart/labels.png')
            im.write(data.read())

    with open('landdisr.gif','wt') as im:
        data = urllib2.urlopen('http://www.ns.nl/spoorkaart/maps/landdisr.gif')
        im.write(data.read())
except Exception:
    print('Het downloaden van de storingskaart is mislukt. Dit script zal nu afsluiten.')
    sys.exit()

# Load images
im_map = Image.open('kaart.png').convert("RGBA")
im_lab = Image.open('labels.png').convert("RGBA")
im_dis = Image.open('landdisr.gif').convert("RGBA")

# Merge maps
im_merged_empty = Image.alpha_composite(im_map, im_lab).save('map_empty.png')
im_merged_empty = Image.open('map_empty.png').convert("RGBA")
im_merged_current = Image.alpha_composite(im_merged_empty, im_dis).save('map_current.png')
im_merged_current = Image.open('map_current.png').convert("RGBA")

# Define the croprange (the range of interest) and then crop both images
croprange = (387, 257, 490, 304)
im_c_em = im_merged_empty.crop(croprange)
im_c_cu = im_merged_current.crop(croprange)

# Get difference between images and get the smallest size of a box that would
# contain all changes. If this box is non-existing, there are no changes
diff = ImageChops.difference(im_c_em,im_c_cu)
if isinstance(diff.getbbox(), types.NoneType) == True:
    print('No disruptions or defects within the cropped area!')
else:
    im_c_cu.save('cropdisr.png')
    import storing_algehad
    lenBefore = len(storing_algehad.notified)
    os.system('python storing.py -a Deventer')
    os.system('python storing.py -a Almelo')
    os.system('python storing.py -a Borne')
    reload(storing_algehad)
    lenAfter = len(storing_algehad.notified)
    if lenAfter > lenBefore:
        print('Nieuwe storingen gevonden, dus de kaart wordt meegezonden.')
        pfile('Storingskaart','cropdisr.png','Storingen gevonden in het bijgesneden gedeelte!')
