# NS-API-python
Python scripts om informatie via de NS API te verkrijgen.

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
