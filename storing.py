'''

NS-API: Storingen
    Geeft een lijst met storingen weer

    Gebruik:
    ./storing.py -a Amsterdam
        -> geeft alle actuele storingen weer waar 'Amsterdam' in voor komt
           (dus ook Amsterdam Zuid, Amsterdam Amstel, etc.)
     ./storing.py -u Amsterdam
        -> geeft alle actuele en geplande storingen weer waar 'Amsterdam' in voor komt
           (dus ook Amsterdam Zuid, Amsterdam Amstel, etc.)

    Dependencies:
        De files 'credentials.py' en 'pb_token.txt' moeten in dezelfde map staan.

'''
# Settings
pb_send = 1

import os.path
import sys
import requests

if len(sys.argv) != 3:
    print('Gebruik: storing.py -a Amsterdam (actueel) of storing.py -u Amsterdam (Actueel en gepland)')
    sys.exit()

if pb_send == 0:
    print 'No pushbullet notes will be sent!'

# Importeer credentials van credentials.py
from credentials import *
from xml.etree import ElementTree

#Creeer algehad file als die niet bestaat
if os.path.isfile('storing_algehad.py') == False:
    with open('storing_algehad.py','w') as file:
        file.write('notified = []')

# Read token for pushbullet
if pb_send == 1:
    global TOKEN
    with open('pb_token.txt', 'r') as file:
        TOKEN = file.read().replace('\n','')

def note(ttl,msg):
    url = "https://api.pushbullet.com/v2/pushes"
    data = dict(type="note", title=ttl, body=msg)
    nreq = requests.post(url, json=data, auth=(TOKEN, '')).json()

url = 'http://webservices.ns.nl/ns-api-storingen'

if sys.argv[1] == '-a':
    url = url + '?station=' + sys.argv[2] + '&actual=true&unplanned=false'

if sys.argv[1] == '-u':
    url = url + '?station=' + sys.argv[2] + '&actual=true&unplanned=true'

data = requests.get(url, auth=(username, password))
tree = ElementTree.fromstring(data.content)

from storing_algehad import *

# Ongepland
for i in range(0,(len(tree[0]))):
    # Allocate as empty strings --> needed for concatenating later on
    sto_Traj = ''
    sto_Reden = ''
    sto_Msg = ''
    sto_Advies = ''
    sto_Date = ''
    sto_Per = ''

    sto_ID = tree[0][i][0].text
    if sto_ID in notified:
        print 'Storing gevonden: ' + sto_ID + '. Is al gemeld.'
    else:
        print 'Storing gevonden: ' + sto_ID + '. Nieuw, dus melding versturen.'
        # Get all information
        for j in range(0,len(tree[0][i])):
            if tree[0][i][j].tag == 'Traject':
                sto_Traj = tree[0][i][j].text
            elif tree[0][i][j].tag == 'Reden':
                sto_Reden = tree[0][i][j].text
            elif tree[0][i][j].tag == 'Bericht':
                sto_Msg = tree[0][i][j].text
                sto_Msg = sto_Msg.replace('<![CDATA[','').replace(']','').replace('\r','').replace('\n','')
            elif tree[0][i][j].tag == 'Advies':
                sto_Advies = tree[0][i][j].text
            elif tree[0][i][j].tag == 'Datum':
                sto_Date = tree[0][i][j].text
            elif tree[0][i][j].tag == 'Periode':
                sto_Per = tree[0][i][j].text

        # Build message
        if sto_Reden != '':
            ttl = 'NS Ongepland: ' + sto_Traj
        else:
            ttl = 'NS Ongepland: ' + sto_Traj + ' omdat: ' + sto_Reden
        msg = 'Storing: ' + sto_ID + '\nMelddatum: ' + sto_Date + '\nBericht: ' + sto_Msg

        if pb_send == 1:
            note(ttl,msg)
            notified.append(sto_ID)

# Gepland
for i in range(0,(len(tree[1]))):
    # Allocate as empty strings --> needed for concatenating later on
    sto_Traj = ''
    sto_Reden = ''
    sto_Msg = ''
    sto_Advies = ''
    sto_Date = ''
    sto_Per = ''

    sto_ID = tree[1][i][0].text
    if sto_ID in notified:
        print 'Storing gevonden: ' + sto_ID + '. Is al gemeld.'
    else:
        print 'Storing gevonden: ' + sto_ID + '. Nieuw, dus melding versturen.'
        # Get all information
        for j in range(0,len(tree[1][i])):
            if tree[1][i][j].tag == 'Traject':
                sto_Traj = tree[1][i][j].text
            elif tree[1][i][j].tag == 'Reden':
                sto_Reden = tree[1][i][j].text
            elif tree[1][i][j].tag == 'Bericht':
                 sto_Msg = tree[1][i][j].text
            elif tree[1][i][j].tag == 'Advies':
                sto_Advies = tree[1][i][j].text
            elif tree[1][i][j].tag == 'Datum':
                sto_Date = tree[1][i][j].text
            elif tree[1][i][j].tag == 'Periode':
                sto_Per = tree[1][i][j].text

        # Build message
        if sto_Reden != '':
            ttl = 'NS Gepland: ' + sto_Traj
        else:
            ttl = 'NS Gepland: ' + sto_Traj + ' omdat: ' + sto_Reden
        msg = 'Storing: ' + sto_ID + '\nPeriode: ' + sto_Per + '\nAdvies: ' + sto_Advies

        if pb_send == 1:
            note(ttl,msg)
            notified.append(sto_ID)

with open('storing_algehad.py', 'w') as file:
    file.write('notified = ' + repr(notified))
