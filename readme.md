FIBA WEBSITE LIVE SCORE SCRAPER


URLS:
https://livecache.sportresult.com/node/db/FIBASTATS_PROD/TRANSLATION_JSON.json?s=unknown&t=0
http://www.fiba.basketball/svc/EventStatus?eventID=13229
https://livecache.sportresult.com/node/db/FIBASTATS_PROD/12105_SCHEDULE_JSON.json?s=unknown&t=0
https://livecache.sportresult.com/node/db/FIBASTATS_PROD/13229_STANDINGDATA_JSON.json?s=unknown&t=0
https://livecache.sportresult.com/node/db/FIBASTATS_PROD/13229_GAME_13554-A-2_JSON.json?s=534&t=0
https://livecache.sportresult.com/node/db/FIBASTATS_PROD/13229_COMPDETAILS_13554-A-2_JSON.json?s=1&t=0
https://livecache.sportresult.com/node/db/FIBASTATS_PROD/13229_GAMEACTIONS_13554-A-2_OT1_JSON.json?s=75&t=0


https://livecache.sportresult.com/node/db/FIBASTATS_PROD/12105_STANDINGDATA_JSON.json?s=unknown&t=0
https://livecache.sportresult.com/node/db/FIBASTATS_PROD/12105_COMPDETAILS_BKM400407_JSON.json?s=1&t=0
https://livecache.sportresult.com/node/db/FIBASTATS_PROD/12105_GAME_BKM400407_JSON.json?s=534&t=0
https://livecache.sportresult.com/node/db/FIBASTATS_PROD/12105_SCHEDULE_JSON.json?s=unknown&t=0

12105&BKM400405
https://livecache.sportresult.com/node/db/FIBASTATS_PROD/12105_GAMEACTIONS_BKM400405_Q1_JSON.json?s=75&t=0


WORKFLOW:
1. Add new Game
2. Check if game is LIVE or OVER
3. Add TEAMS to database
4. Add PLAYERS to database


GAME STATE:
1. Future - Do nothing
2. Playing - Scrape every X seconds
3. Finished - If not scraped do the scraping. Respond XML



PROBLEMS:
1. If player anounced later on not on instantinating the Game/Team we won't get him in database.


START DJANGO CELERY BEAT: celery -A proj beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler