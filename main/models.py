import time

from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from main.utils.fiba_api import Fiba_Game

from main import tasks


class Team(models.Model):
    code = models.CharField(max_length=300, unique=True)
    name = models.CharField(max_length=300)
    flag = models.CharField(max_length=500)
    nationality = models.CharField(max_length=50)

    def __str__(self):
        return self.name    


class Game(models.Model):
    code = models.CharField(max_length=300, unique=True)
    status = models.CharField(max_length=300, blank=True)
    team_a = models.ForeignKey(Team, related_name='%(class)s_team_a', 
                                blank=True, null=True, on_delete=models.CASCADE)
    team_b = models.ForeignKey(Team, related_name='%(class)s_team_b',
                                blank=True, null=True, on_delete=models.CASCADE)
    team_a_score = models.IntegerField(default=0, blank=True)
    team_b_score = models.IntegerField(default=0, blank=True)
    current_period = models.CharField(max_length=10, blank=True)
    start_time = models.BigIntegerField(default=0, blank=True)

    def save(self, force_insert=False, force_update=False):
        if not self.team_a or not self.team_b:
            game = Fiba_Game(self.code)
            team_a_temp, team_b_temp = game.get_teams()
            team_a, _ = Team.objects.get_or_create(code=team_a_temp['code'],
                                                defaults=team_a_temp)
            team_a.save()
            team_b, _ = Team.objects.get_or_create(code=team_b_temp['code'],
                                    defaults=team_b_temp)
            team_b.save()
            self.team_a = team_a
            self.team_b = team_b
            info = game.get_info()
            if self.team_a.code == info['team_a']['team_a_uid']:
                self.team_a_score = info['team_a']['team_a_score']
                self.team_b_score = info['team_b']['team_b_score']
            else:
                self.team_b_score = info['team_a']['team_a_score']
                self.team_a_score = info['team_b']['team_b_score']
        super(Game, self).save(force_insert, force_update)


class Player(models.Model):
    code = models.CharField(max_length=300, unique=True)
    first_name = models.CharField(max_length=300)
    last_name = models.CharField(max_length=300)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    headshot = models.CharField(max_length=500)


class Actions(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    action_code = models.CharField(max_length=30) # AC
    action_text = models.CharField(max_length=100, blank=True, null=True) # Action
    action_uid = models.IntegerField(default=0, blank=True, null=True) # Id
    time = models.CharField(max_length=30, blank=True, null=True) # Time
    epoch_time = models.BigIntegerField(blank=True, null=True)
    player = models.ForeignKey(Player, blank=True, null=True,
                                related_name='%(class)s_player') # C1
    shot_x = models.IntegerField(blank=True, null=True) # SX
    shot_y = models.IntegerField(blank=True, null=True) # SY
    score = models.CharField(max_length=30,blank=True, null=True) # Score
    subs_in = models.ForeignKey(Player, blank=True, null=True,
                                related_name='%(class)s_subs_in') # C2 | On SUBS Player field -OUT subs_in +IN


@receiver(pre_save, sender=Game)
def check_status(sender, instance, **kwargs):
    game = Fiba_Game(instance.code)
    info = game.get_info()
    instance.status = info['status']
    instance.start_time = info['start_time']
    # instance.team_b_score = info['team_b_score']
    instance.current_period = info['current_period']

@receiver(post_save, sender=Game)
def add_teams(sender, instance, **kwargs):
    game = Fiba_Game(instance.code)
    players = game.get_players()
    for player in players:
        tasks.add_player.apply_async(player_info=player) # SITA VIETA KNISAS
    time.sleep(0.5) # In case not all players created
    tasks.get_game_actions(instance.code) # Add actions