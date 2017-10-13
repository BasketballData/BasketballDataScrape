from django.db import models


class SwissGame(models.Model):
    league_id = models.IntegerField()
    competition_id = models.IntegerField()
    match_id = models.IntegerField()
    match_status = models.CharField(max_length=50)
    match_time_utc = models.DateTimeField()
    live = models.IntegerField()
    home_name = models.CharField(max_length=300)
    home_code = models.CharField(max_length=30)
    home_team_id = models.IntegerField()
    home_logo = models.CharField(max_length=300)
    away_name = models.CharField(max_length=300)
    away_code = models.CharField(max_length=30)
    away_team_id = models.IntegerField()
    away_logo = models.CharField(max_length=300)