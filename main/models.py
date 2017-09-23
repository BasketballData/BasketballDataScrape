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


class Location(models.Model):
    city = models.CharField(max_length=300)
    code = models.CharField(max_length=100, primary_key=True)
    title = models.CharField(max_length=300)

    def __str__(self):
        return self.city


class Game(models.Model):
    code = models.CharField(max_length=300, unique=True)
    status = models.CharField(default="future", max_length=300, blank=True)
    team_a = models.ForeignKey(Team, related_name='%(class)s_team_a', 
                                blank=True, null=True, on_delete=models.CASCADE)
    team_b = models.ForeignKey(Team, related_name='%(class)s_team_b',
                                blank=True, null=True, on_delete=models.CASCADE)
    team_a_score = models.IntegerField(blank=True, null=True)
    team_b_score = models.IntegerField(blank=True, null=True)
    team_a_foul = models.IntegerField(default=0, blank=True)
    team_b_foul = models.IntegerField(default=0, blank=True)
    team_a_period_scores = models.CharField(max_length=300, blank=True)
    team_b_period_scores = models.CharField(max_length=300, blank=True)
    current_period = models.CharField(max_length=10, blank=True)
    start_time = models.BigIntegerField(default=0, blank=True, null=True)
    location = models.ForeignKey(Location, blank=True, null=True)
    time = models.CharField(max_length=30, blank=True)
    init_scrape = models.BooleanField(default=True)

    def save(self, force_insert=False, force_update=False):
        if not self.team_a or not self.team_b:
            game = Fiba_Game(self.code)
            data_available = game.data_available()
            if data_available['game_comp_details']:
                team_a_temp, team_b_temp = game.get_teams()
                team_a, _ = Team.objects.get_or_create(code=team_a_temp['code'],
                                                    defaults=team_a_temp)
                team_a.save()
                team_b, _ = Team.objects.get_or_create(code=team_b_temp['code'],
                                        defaults=team_b_temp)
                team_b.save()
                self.team_a = team_a
                self.team_b = team_b
        # if self.team_a_score == "" or self.team_b_score == "":
        #     game = Fiba_Game(self.code)
        #     info = game.get_info()
        #     if self.team_a.code == info['team_a']['team_a_uid']:
        #         self.team_a_score = info['team_a']['team_a_score']
        #         self.team_b_score = info['team_b']['team_b_score']
        #     else:
        #         self.team_b_score = info['team_a']['team_a_score']
        #         self.team_a_score = info['team_b']['team_b_score']
        super(Game, self).save(force_insert, force_update)

    def __str__(self):
        return self.code

    def get_actions(self):
        actions = Actions.objects.filter(game=self.id)
        return actions
    
    def get_score(self):
        return "%s-%s" % (self.team_a_score, self.team_b_score)

    def get_periods_score(self):
        full_xml = ""
        team_a_scores = self.team_a_period_scores.split()
        team_b_scores = self.team_b_period_scores.split()
        q = 1
        for a, b in zip(team_a_scores, team_b_scores):
            full_xml += "<q%s>%s-%s</q%s>" % (q, a, b, q)
            q += 1
        return full_xml
    
    def utc_start(self):
        if self.start_time:
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.start_time / 1000))
        else:
            return "Unknown"



class Player(models.Model):
    code = models.CharField(max_length=300, unique=True)
    first_name = models.CharField(max_length=300)
    last_name = models.CharField(max_length=300)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    headshot = models.CharField(max_length=500)
    shirt_number = models.IntegerField()

    def get_full_name(self):
        return self.first_name + ' ' + self.last_name


class Actions(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    action_code = models.CharField(max_length=30) # AC
    action_text = models.CharField(max_length=100, blank=True, null=True) # Action
    action_uid = models.IntegerField(default=0, blank=True, null=True) # Id
    action_local_uid = models.CharField(max_length=30, unique=True, blank=True, null=True)
    time = models.CharField(max_length=30, blank=True, null=True) # Time
    epoch_time = models.BigIntegerField(blank=True, null=True)
    player = models.ForeignKey(Player, blank=True, null=True,
                                related_name='%(class)s_player') # C1
    shot_x = models.IntegerField(blank=True, null=True) # SX
    shot_y = models.IntegerField(blank=True, null=True) # SY
    team_a_score = models.IntegerField(blank=True, null=True)
    team_b_score = models.IntegerField(blank=True, null=True)
    score = models.CharField(max_length=30,blank=True, null=True) # Score
    subs_in = models.ForeignKey(Player, blank=True, null=True,
                                related_name='%(class)s_subs_in') # C2 | On SUBS Player field -OUT subs_in +IN
    plus_minus = models.CharField(max_length=30,blank=True, null=True)
    team = models.ForeignKey(Team, blank=True, null=True)
    period = models.CharField(max_length=30,blank=True, null=True)

    class Meta:
        ordering = ['-period', '-action_uid']
        verbose_name = "Action"

    def get_utc_time(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(self.epoch_time))

    def get_shot_x(self):
        if self.shot_x:
            return self.shot_x
        else:
            return ""

    def get_shot_y(self):
        if self.shot_y:
            return self.shot_y
        else:
            return ""

@receiver(pre_save, sender=Game)
def check_status(sender, instance, **kwargs):
    if instance._state.adding:
        game = Fiba_Game(instance.code)
        available = game.data_available()
        if available['game_info'] and available['game_actions']:
            #info = game.get_info()
            #instance.status = info['status']
            # instance.start_time = info['start_time']
            # instance.team_a_score = info['team_a']['team_a_score']
            # instance.team_a_foul = info['team_a']['team_a_foul']
            # instance.team_b_score = info['team_b']['team_b_score']
            # instance.team_b_foul = info['team_b']['team_b_foul']
            # instance.current_period = info['current_period']
            # instance.time = info['time']
            # instance.team_a_period_scores = info['team_a']['team_a_scores']
            # instance.team_b_period_scores = info['team_b']['team_b_scores']

            tasks.init_locations(instance.code)
            try:
                location = Location.objects.get(code=info['location'])
                instance.location = location
            except:
                pass
        else:
            instance.start_time = game.get_start_time()
            instance.status = "future"

# @receiver(post_save, sender=Game)
# def add_teams(sender, instance, created, **kwargs):
#     if created:
#         game = Fiba_Game(instance.code)
#         available = game.data_available()
#         if available['game_info'] and available['game_actions']:
#             players = game.get_players()
#             for player in players:
#                 tasks.add_player.apply_async(args=([player]), countdown=10)
#             # time.sleep(0.5) # In case not all players created
#             #tasks.get_game_actions.apply_async(args=([instance.code]), countdown=15) # Add actions, 
