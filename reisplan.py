# Settings
pb_send = 1

# Importeer afhankelijkheden
import sys       # Nodig voor input arguments
import requests  # Nodig voor request aan API server
import datetime  # Nodig voor tijd vergelijken
from xml.etree import ElementTree # Nodig om data van server mee te verwerken

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
tijdNu = datetime.datetime.now()

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

for itt in range(0,(len(tree))):
    # basis attibuten van een reisadvies oppakken
    Status = tree[itt].find('Status').text

    vertrekTijdString = tree[itt].find('GeplandeVertrekTijd').text
    aankomstTijdString = tree[itt].find('GeplandeAankomstTijd').text
    vertrekTijdTijd = datetime.datetime.strptime(vertrekTijdString, "%Y-%m-%dT%H:%M:%S+0100")
    aankomstTijdTijd = datetime.datetime.strptime(aankomstTijdString, "%Y-%m-%dT%H:%M:%S+0100")
    vertrekTijd = vertrekTijdString[11:16]
    aankomstTijd = aankomstTijdString[11:16]

    if vertrekTijdTijd < tijdNu:
        # Rit is al vertrokken geen last meer van die ongeregeldheden
        continue

    if Status != 'VOLGENS-PLAN':
        # Er is iets mis uitvinden wat
        meldplicht = False
        stoMsg = ''

        if Status == 'VERTRAAGD':
            # Mogelijke problemen, uitzoeken hoe groot/relevant
            AankomstVertraging = tree[itt].find('AankomstVertraging')
            VertrekVertraging = tree[itt].find('VertrekVertraging')

            if (AankomstVertraging is None) and (VertrekVertraging is None):
                # Gedurende de treinreis rijd de trein met vertraging maar haalt dit in
                continue

            else:
                stoMsg = stoMsg + Status + '\n'
                # Er is vertraging en we gaan er last van hebben
                if VertrekVertraging is not None:
                    if len(VertrekVertraging.text) > 6 or int(VertrekVertraging.text[1]) > 5:
                        # de vertrekvertraging is groot genoeg om te melden
                        meldplicht = True

                    stoMsg = stoMsg + 'Vertrek: ' + vertrekTijd + ' ' + VertrekVertraging.text + '\n'
                else:
                    stoMsg = stoMsg + 'Vertrek: ' + vertrekTijd + ' (op tijd)\n'

                if AankomstVertraging is not None:
                    if len(AankomstVertraging.text) > 6 or int(AankomstVertraging.text[1]) > 5:
                        # de aankomstvertraging is groot genoeg om te melden
                        meldplicht = True

                    stoMsg = stoMsg + 'Aankomst: ' + aankomstTijd + ' ' + AankomstVertraging.text + '\n'
                else:
                    stoMsg = stoMsg + 'Aankomst: ' + aankomstTijd + ' (op tijd)\n'

        elif Status == 'NIET-MOGELIJK':
            # Reisadvies is vervallen of niet haalbaar
            meldplicht = True
            stoMsg = 'NIET MOGELIJK\n'
            stoMsg = stoMsg + 'Vertrek: ' + vertrekTijd + ' vervalt\n'
            stoMsg = stoMsg + 'Aankomst: ' + aankomstTijd + ' vervalt\n'

        elif Status == 'NIET-OPTIMAAL':
            # Dit is vaak niet relevant dus extra check of een bericht nodig is
            stoMsg = 'NIET-OPTIMAAL \n'
            actVertrektijdString = tree[itt].find('ActueleVertrekTijd').text
            actAankomsttijdString = tree[itt].find('ActueleAankomstTijd').text
            actVertrekTijdTijd = datetime.datetime.strptime(actVertrektijdString, "%Y-%m-%dT%H:%M:%S+0100")
            actAankomstTijdTijd = datetime.datetime.strptime(actAankomsttijdString, "%Y-%m-%dT%H:%M:%S+0100")

            deltaVertrekTijd = actVertrekTijdTijd - vertrekTijdTijd
            deltaAankomstTijd = actAankomstTijdTijd - aankomstTijdTijd

            # Controleren of de trein later dan gepland vertrekt
            if deltaVertrekTijd.seconds/60 > 5:
                meldplicht = True
                stoMsg = stoMsg + 'Vertrek: ' + vertrekTijd + ' + ' + deltaVertrekTijd/60 + ' min\n'
            else:
                stoMsg = stoMsg + 'Vertrek: ' + vertrekTijd + ' (op tijd)\n'

            if  deltaAankomstTijd.seconds/60 > 5:
                meldplicht = True
                stoMsg = stoMsg + 'Aankomst: ' + vertrekTijd + ' +' + deltaAankomstTijd/60 + ' min\n'
            else:
                stoMsg = stoMsg + 'Aankomst: ' + aankomstTijd + ' (op tijd)\n'

        else:
            # Andere gevallen, impact moeilijk te bepalen
            meldplicht = True
            stoMsg = stoMsg + Status + '\n'
            stoMsg = stoMsg + 'Vertrek: ' + vertrekTijd + '\n'
            stoMsg = stoMsg + 'Aankomst: ' + aankomstTijd + '\n'

        if meldplicht:
            ongeregeldheden += 1
            pushMsg = pushMsg + stoMsg + '\n'

if ongeregeldheden > 0 and pb_send == 1:
    note(pushTitle, pushMsg)
