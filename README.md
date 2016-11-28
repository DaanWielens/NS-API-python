# NS-API-python
Python scripts om informatie via de NS API te verkrijgen.

## MapDiff
Een van de problemen die ik ondervond bij `storing.py` is dat ondanks dat je kunt opgeven dat je alleen storingen voor Maastricht wil ontvangen, je toch storingen van Groningen krijgt (dit geldt voor ongeplande storingen, niet voor geplande storingen/werkzaamheden).

`MapDiff` lost dit op doordat je een gekozen stuk van de storingskaart van de NS (te vinden op http://www.ns.nl/reisinformatie/actuele-situatie-op-het-spoor) kunt selecteren. Enkel en alleen als er storingen in dat gebied zijn wordt het `storing.py` script aangeroepen. Dit neemt niet weg dat je een melding voor Groningen krijgt wanneer er iets aan de hand is, maar je krijgt alleen een melding als er ook iets in Maastricht aan de hand is (om maar even dezelfde voorbeelden te gebruiken).

**Gebruik:**
Gebruik de storingskaart (http://www.ns.nl/static/generic/2.4.0/images/storingenkaart/kaart.png) om een gebied te selecteren waarbinnen je wilt controleren op storingen. Dit gebied wordt opgeslagen door middel van 4 coördinaten: linksboven x, linksboven y, rechtsonder x, rechtsonder y.

In het script kunnen deze waarden ingevoerd worden in
`croprange(linksboven_x, linksboven_y, rechtsonder_x, rechtsonder_y)`

Vervolgens kun je de stations definiëren waarvoor je meldingen wilt ontvangen wanneer er een storing is binnen de `croprange`. Pas de regels van de stations aan naar eigen wens (laatste regels van het bestand, wijst zich vanzelf).

**Dependencies:**
Het script `mapdiff.py` heeft meerdere dependencies:
- Het script `storingen.py` moet in dezelfde map staan
- De file `pb_token.txt` is nodig (zie uitleg bij `storing.py`)
- De file `credentials.py` is nodig voor `storing.py` (wordt daar verder toegelicht)

## Storingen
Via `storing.py` kan men de actuele storingen opvragen. Deze worden via Pushbullet eenmalig verzonden naar de gebruiker.

**Gebruik:**
Toon actuele stroringen voor een bepaald station (traject):
`./storing.py -a Amsterdam`

Toon actuele en geplande (toekomstige) storingen voor een station:
`./storing.py -u Amsterdam`

**Dependencies:**
Het script `storing.py` heeft twee dependencies:
- De file `credentials.py` bevat simpelweg twee regels:
```
username = 'blabla'
password = 'blabla'
```
*Note:* Deze credentials zijn van het NS-API account. Hiervoor moet je je aanmelden (gratis) bij NS: https://www.ns.nl/ews-aanvraagformulier/
- De file `pb_token.txt` bevat enkel het pushbullet token zodat het script pushbullet notes kan versturen:
```
TOKEN_hier
```
*Note:* Je kunt je pushbullet token opvragen bij https://www.pushbullet.com/#settings/account

## Stations
Via `station.py` kan men stationsinformatie opvragen (naam, type, land, coördinaten, type).

**Gebruik:**
Geef alle stations weer:
`./station.py`

Geef stations weer waarin de zoekopdracht voorkomt:
`./station.py -a Amsterdam`
(geeft Amsterdam Zuid, Amsterdam Centraal, enz.)

Geef stations weer die exact de naam hebben zoals in de zoekopdracht:
`./station.py -s Amsterdam`

**Dependencies:**
Het script heeft, net als `storing.py` de `credentials.py` file nodig. Zie voor de contents van de file en het aanvragen van deze credentials de informatie bij het storingscript.
