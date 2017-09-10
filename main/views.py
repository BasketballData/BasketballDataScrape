from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from main.models import Game

# Create your views here.
def get_game(request, game):
    game = get_object_or_404(Game, code=game)
    return HttpResponse(game.code)