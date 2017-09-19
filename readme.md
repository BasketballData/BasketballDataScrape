## ABOUT
Live fiba game data scraper and XML exporter

## CREDENTIALS

SERVER IP ADDRESS: 138.68.68.33

ROOT: root

ROOT PASSWORD: fiba#2017

ADMIN PANEL: http://138.68.68.33/admin
ADMIN USERNAME: fiba
ADMIN PASSWORD: fiba#2017

## TECHNOLOGY USED
1. Django
2. Celery
3. Redis
4. PostgreSQL
5. Flower
6. Supervisor

## HOW TO

### ADD NEW GAME
To add new game login to administrator panel and click on **GAMES** menu item and click on **ADD NEW GAME** button.
You need to add only game **code** which can be obtained from FIBA website. 
EXAMPLE FIBA GAME URL: http://www.fiba.basketball/ls/#12105&BKM400405
EXAMPLE CODE TO BE ADDED: **105&BKM400405** *(note: do not include hasgtag #)*

### GET XML FEED
To get XML feed you need to visit 138.68.68.33/game_code_here 
EXAMPLE: 138.68.68.33/105&BKM400405

## FLOWER
Implemented FLOWER for easy tracking of celery background tasks.
URL: 138.68.68.33:5555

## SUPERVISOR
Implemented supervisor for Gunicorn/Celery/Flower service managment. You can check status, restart, stop or start these services from GUI web panel.
URL: 138.68.68.33:9001
USERNAME: fiba
PASSWORD: fiba#2017


## SOURCE URLS:
https://livecache.sportresult.com/node/db/FIBASTATS_PROD/TRANSLATION_JSON.json?s=unknown&t=0
http://www.fiba.basketball/svc/EventStatus?eventID=13229
https://livecache.sportresult.com/node/db/FIBASTATS_PROD/12105_SCHEDULE_JSON.json?s=unknown&t=0
https://livecache.sportresult.com/node/db/FIBASTATS_PROD/13229_STANDINGDATA_JSON.json?s=unknown&t=0
https://livecache.sportresult.com/node/db/FIBASTATS_PROD/13229_GAME_13554-A-2_JSON.json?s=534&t=0
https://livecache.sportresult.com/node/db/FIBASTATS_PROD/13229_COMPDETAILS_13554-A-2_JSON.json?s=1&t=0
https://livecache.sportresult.com/node/db/FIBASTATS_PROD/13229_GAMEACTIONS_13554-A-2_OT1_JSON.json?s=75&t=0
