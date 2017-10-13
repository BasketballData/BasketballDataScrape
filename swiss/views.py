from django.shortcuts import render
from django.http import HttpResponse
from main.models import Game

import requests

# Create your views here.
def get_game(request, game):
    BASE_URL = "http://www.fibalivestats.com/data/%s/data.json"
    url = BASE_URL % game
    retries = 0
    success = False
    while not success:
        if retries < 3:
            response = requests.get(url)
            if response.status_code == 200 or response.status_code == 304:
                success = True
                return render(request, 
                        'swiss_game.xml',
                        {'info': response.json()},
                        content_type="application/xhtml+xml")
            else:
                retries += 1
        else:
            return HttpResponse('Failed to get response from FibaStats server')