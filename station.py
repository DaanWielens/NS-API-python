'''

NS-API: Stations
    Geeft een lijst met stations weer

    Gebruik:
    ./station.py
        -> geeft alle stations weer
    ./station.py -a Amsterdam
        -> geeft alle stations weer waar 'Amsterdam' in voor komt
           (dus ook Amsterdam Zuid, Amsterdam Amstel, etc.)
    ./station.py -s 'Amsterdam Amstel'
        -> geeft alleen stations weer die voldoen aan de stricte opdracht
           (dus enkel Amsterdam Amstel)
'''

import sys
import requests
# Importeer credentials van credentials.py
from credentials import *
from xml.etree import ElementTree

url = 'http://webservices.ns.nl/ns-api-stations-v2'
data = requests.get(url, auth=(username, password))
tree = ElementTree.fromstring(data.content)

if sys.argv[1] == '-a':
    for i in range(0,len(tree)):
        if sys.argv[2] in tree[i][2][2].text:
            print '------------------------------------'
            print 'Station: ' + tree[i][2][2].text
            print 'Type:    ' + tree[i][1].text
            print 'Land:    ' + tree[i][3].text
            print 'Lat.:    ' + tree[i][5].text
            print 'Lon.:    ' + tree[i][6].text
if sys.argv[1] == '-s':
    for i in range(0,len(tree)):
        if sys.argv[2] == tree[i][2][2].text:
            print 'Station: ' + tree[i][2][2].text
            print 'Type:    ' + tree[i][1].text
            print 'Land:    ' + tree[i][3].text
            print 'Lat.:    ' + tree[i][5].text
            print 'Lon.:    ' + tree[i][6].text
