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

    all_actions = models.Actions.objects.values_list('action_uid', flat=True)
    for action in actions:
        if not action['Id'] in all_actions:
            models.Actions.objects.create(
                game=current_game,
                action_code=action.get('AC', None),
                action_text=action.get('Action', None),
                action_uid=int(action.get('Id', "0").replace(':', "")),
                time=action.get('Time', None),
                epoch_time=action.get('GT', None),
                shot_x=action.get('SX', None),
                shot_y=action.get('SY', None),
                score=action.get('Score', None),
                subs_in=_get_player(action.get('C2', None)),
                player=_get_player(action.get('C1', None))
            ) 