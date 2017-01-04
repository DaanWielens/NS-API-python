# Settings
pb_send = 1

# Importeer afhankelijkheden
import os.path
import sys
import requests
from xml.etree import ElementTree

# Importeer credentials van credentials.py
from credentials import *

via = False

# Controleer input
if len(sys.argv) == 3:
    fromStation = sys.argv[1]
    toStation = sys.argv[2]

elif len(sys.argv) == 4:
    fromStation = sys.argv[1]
    toStation = sys.argv[2]
    viaStation = sys.argv[3]
    via = True
else:
    print('Gebruik: "reisplan.py Amsterdam Zwolle" of "reisplan.py Amsterdam Zwolle Groningen" voor een via')
    sys.exit()

# Controleer of berichten worden verzonden
if pb_send == 0:
    print 'Geen notificaties via pushbullet'

# Extraheer input data and initialise
ongeregeldheden = 0
pushTitle = 'Verstoring: ' + fromStation + ' ' + toStation
pushMsg = ''
url = 'http://webservices.ns.nl/ns-api-treinplanner?fromStation='+fromStation+'&toStation='+toStation

# Voeg info toe van de via
if via:
    pushTitle = pushTitle + ' via ' + viaStation
    url = url + '&viaStation=' + viaStation

# Read token for pushbullet
if pb_send == 1:
    global TOKEN
    with open('pb_token.txt', 'r') as file:
        TOKEN = file.read().replace('\n','')

def note(ttl,msg):
    url = "https://api.pushbullet.com/v2/pushes"
    data = dict(type="note", title=ttl, body=msg)
    nreq = requests.post(url, json=data, auth=(TOKEN, '')).json()

data = requests.get(url, auth=(username, password))
tree = ElementTree.fromstring(data.content)

for itt in range(0,(len(tree[0])-1)):
    # basis attibuten van een reisadvies oppakken
    Status = tree[itt].find('Status').text
    vertrekTijd = tree[itt].find('GeplandeVertrekTijd').text[11:16]
    aankomstTijd = tree[itt].find('GeplandeAankomstTijd').text[11:16]

    if Status != 'VOLGENS-PLAN':
        # Er is iets mis uitvinden wat
        ongeregeldheden += 1

        if Status == 'VERTRAAGD':

            # Mogelijke problemen, uitzoeken hoe groot
            AankomstVertraging = tree[itt].find('AankomstVertraging')
            VertrekVertraging = tree[itt].find('VertrekVertraging')

            if (AankomstVertraging is None) and (VertrekVertraging is None):
                # Gedurende de treinreis rijd de trein met vertraging maar haalt dit in
                #print 'Vals alarm'
                ongeregeldheden -= 1
                continue

            else:
                pushMsg = pushMsg + Status + '\n'
                # Er is vertragin en we gaan er last van hebben
                if VertrekVertraging is not None:
                    pushMsg = pushMsg + 'Vertrek: ' + vertrekTijd + ' ' + VertrekVertraging.text + '\n'
                else:
                    pushMsg = pushMsg + 'Vertrek: ' + vertrekTijd + ' (op tijd)\n'

                if AankomstVertraging is not None:
                    pushMsg = pushMsg + 'Aankomst: ' + aankomstTijd + ' ' + AankomstVertraging.text + '\n'
                else:
                    pushMsg = pushMsg + 'Aankomst: ' + aankomstTijd + ' (op tijd)\n'

        elif Status == 'NIET-MOGELIJK':
            # Reisadvies is vervallen of niet haalbaar
            pushMsg = pushMsg + 'Vertrek: ' + vertrekTijd + ' VERVALT\n'
            pushMsg = pushMsg + 'Aankomst: ' + aankomstTijd + 'VERVALT\n'

        else:
            # Andere gevallen, impact moeilijk te bepalen
            pushMsg = pushMsg + Status + '\n'
            pushMsg = pushMsg + 'Vertrek: ' + vertrekTijd + '\n'
            pushMsg = pushMsg + 'Aankomst: ' + aankomstTijd + '\n'

        pushMsg = pushMsg + '\n'

if ongeregeldheden > 0 and pb_send == 1:
    note(pushTitle, pushMsg)
