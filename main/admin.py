from django.contrib import admin
from main.models import Game, Player, Team, Actions

# Register your models here.
class GameAdmin(admin.ModelAdmin):
    list_display = ['code', 'team_a', 'team_b', 'status', 'team_a_score', 'team_b_score']
admin.site.register(Game, GameAdmin)

class TeamAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']
admin.site.register(Team, TeamAdmin)

class PlayerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'team']
admin.site.register(Player, PlayerAdmin)

class ActionsAdmin(admin.ModelAdmin):
    list_display = ['action_uid', 'action_code', 'time']
admin.site.register(Actions, ActionsAdmin)