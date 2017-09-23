from django.contrib import admin
from main.models import Game, Player, Team, Actions, Location

# Register your models here.
class GameAdmin(admin.ModelAdmin):
    list_display = ['code', 'team_a', 'team_b', 'status', 'team_a_score', 'team_b_score']
    ordering = ('code',)
admin.site.register(Game, GameAdmin)

class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    ordering = ('name',)
admin.site.register(Team, TeamAdmin)

class PlayerAdmin(admin.ModelAdmin):
    list_display = [ 'last_name', 'first_name', 'team']
    search_fields = ('first_name', 'last_name', 'team', 'code')
    ordering = ('last_name',)
admin.site.register(Player, PlayerAdmin)

class ActionsAdmin(admin.ModelAdmin):
    list_display = ['game', 'action_uid', 'action_local_uid', 'action_code', 'period', 'time']
    ordering = ('game','period' ,'-time')
    search_fields = ('game',)
admin.site.register(Actions, ActionsAdmin)

class LocationAdmin(admin.ModelAdmin):
    list_display = ['city', 'code', 'title']
    ordering = ('city',)
admin.site.register(Location, LocationAdmin)