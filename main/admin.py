from django.contrib import admin
from main.models import Game, Player, Team, Actions, Location
from django import forms

from main.utils.fiba_api import Fiba_Game

# Register your models here.

class MyForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = "__all__"
    def clean_code(self):
        code = self.cleaned_data['code']
        if '#' in code:
            code = code.replace('#', '')
        if ' ' in code:
            code = code.replace(' ', '')
        if not '&' in code:
            raise forms.ValidationError('We did not find & sign in code. Example of proper game code: 12105&BKM400101')
        game = Fiba_Game(code)
        game_exists = game.check_exists()
        if not game_exists['league']:
            raise forms.ValidationError('League not found. Please check the code')
        if not game_exists['game']:
            raise forms.ValidationError('League found but no information about this game. Please check the code')
        
        return code
        #raise forms.ValidationError("You have no points!")

class GameAdmin(admin.ModelAdmin):
    form = MyForm
    list_display = ['code', 'team_a', 'team_b', 'status', 'team_a_score', 'team_b_score', 'utc_start']
    ordering = ('code',)
admin.site.register(Game, GameAdmin)

class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    ordering = ('name',)
admin.site.register(Team, TeamAdmin)

class PlayerAdmin(admin.ModelAdmin):
    list_display = [ 'last_name', 'first_name', 'team']
    search_fields = ('first_name', 'last_name', 'team__name', 'code')
    ordering = ('last_name',)
admin.site.register(Player, PlayerAdmin)

class ActionsAdmin(admin.ModelAdmin):
    list_display = ['game', 'action_uid', 'action_local_uid', 'action_code', 'period', 'time']
    ordering = ('game','period' ,'-time')
    search_fields = ('game__code',)
admin.site.register(Actions, ActionsAdmin)

class LocationAdmin(admin.ModelAdmin):
    list_display = ['city', 'code', 'title']
    ordering = ('city',)
admin.site.register(Location, LocationAdmin)