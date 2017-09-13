import logging

from django.db import IntegrityError

from celery import shared_task

from main import models
from main.utils.fiba_api import Fiba_Game


logger = logging.getLogger(__name__)

@shared_task
def add_player(player_info):
    try:
        team = models.Team.objects.get(code=player_info['team_unique_id'])
    except Exception as e:
        logger.error('ERROR Creating new team. MSG: %s' % e)
        return False
    del player_info['team_unique_id']
    try:
        player = models.Player(team=team, **player_info)
        player.save()
    except IntegrityError:
        logger.info('Player %s already exists in database' % player_info['code'])
        return True
    except Exception as e:
        logger.error('ERROR Creating new player. MSG: %s' % e)
        return False
    return True


@shared_task
def get_game_actions(code):
    """ Gets all actions and stores to database """
    current_game = models.Game.objects.get(code=code)
    game = Fiba_Game(code)
    actions = game.get_actions()
    #teams = models.Team.objects.filter(code=code)
    teams = []
    teams.append(current_game.team_a)
    teams.append(current_game.team_b)
    players = models.Player.objects.filter(team__in=teams)
    logger.info('FILTERED PLAYERS: %s' % players)

    def _get_player(player_code):
        if player_code:
            for player in players:
                if player.code == player_code:
                    return player
        else:
            return None
    
    def _get_team(team_code):
        if team_code:
            for team in teams:
                if team.code == team_code:
                    return team
        else:
            return None
    
    def _clean_time(time):
        if time:
            return int(str(time)[:10])
        else:
            return ""


    all_actions = models.Actions.objects.values_list('action_uid', flat=True)
    current_score = {'team_a':0, 'team_b': 0}
    for action in actions:
        score = action.get('Score', None)
        if score:
            splited_score = score.split('-')
            current_score['team_a'] = splited_score[0]
            current_score['team_b'] = splited_score[1]
        if not action['Id'] in all_actions:
            # Maybe add this to separate Celery tasks (?)
            models.Actions.objects.create(
                game=current_game,
                action_code=action.get('AC', ''),
                action_text=action.get('Action', ''),
                action_uid=int(action.get('Id', "0").replace(':', '')),
                time=action.get('Time', ''),
                epoch_time=_clean_time(action.get('GT', '')),
                shot_x=action.get('SX', 0),
                shot_y=action.get('SY', 0),
                score=action.get('Score', ''),
                subs_in=_get_player(action.get('C2', '')),
                player=_get_player(action.get('C1', '')),
                plus_minus=action.get('SU', ''),
                team=_get_team(action.get('T1', '')),
                team_a_score=current_score['team_a'],
                team_b_score=current_score['team_b'],
            )

@shared_task
def init_locations(code):
    """ Populates database with locations """
    game = Fiba_Game(code)
    locations = game.get_locations()
    for location in locations:
        _, _ = models.Location.objects.get_or_create(
                    code=locations[location]['Code'],
                    defaults={
                        'city': locations[location]['City'],
                        'title': locations[location]['Title']                        
                    }
        )
