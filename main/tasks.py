import logging
import time
import json

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
def get_game_actions(code, period=None):
    """ Gets all actions and stores to database """
    action_text_json = None
    with open('main/utils/actions.json') as f:
        action_text_json = json.load(f)

    current_game = models.Game.objects.get(code=code)
    game = Fiba_Game(code)
    actions = game.get_actions(period)
    #logger.info('THIS IS ACTION: %s' % actions)
    #teams = models.Team.objects.filter(code=code)
    teams = []
    teams.append(current_game.team_a)
    teams.append(current_game.team_b)
    players = models.Player.objects.filter(team__in=teams)

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
    
    def _get_action_uid(action):
        action_uid = None
        try:
            return int(action['ListIndex'])
        except Exception as e:
            #logger.info("ERROR IN ACTION UID. %s" % e)
            return int(action['Id'])
    
    def _get_action_text(action):
        action_text = action.get('Action', '')
        if not action_text:
            action_name = '%s|%s|%s|%s|%s'
            action_code = action.get('AC', '')
            action_z1 = action.get('Z1', '')
            action_z2 = action.get('Z2', '')
            action_z3 = action.get('Z3', '')
            action_su = action.get('SU', '')
            action_name = action_name % (
                                        action_code,
                                        action_z1,
                                        action_z2,
                                        action_z3,
                                        action_su)
            try:
                action_text = action_text_json['content']['full']['actions'][action_name]
                return action_text
            except:
                return action_text
        return action_text


    current_score = {'team_a': 0, 'team_b': 0}

    all_actions = models.Actions.objects.filter(game=current_game).values_list('action_local_uid', flat=True)
    for action in actions:
        #logger.info('MMM THIS IS ACTION: %s' % action)
        score = action.get('Score', None)
        if score:
            splited_score = score.split('-')
            current_score['team_a'] = splited_score[0]
            current_score['team_b'] = splited_score[1]
        
        action_uid = _get_action_uid(action)
        action_period = action.get('action_period', '')
        # Constructing unique id from game code, period, action id/index
        action_local_uid = current_game.code + action_period + str(action_uid)

        if not action_local_uid in all_actions:
            #logger.info('ACTION ID: %s ALL ACTIONS: %s' % (action_uid, all_actions))
            # Maybe add this to separate Celery tasks (?)
            models.Actions.objects.create(
                game=current_game,
                action_code=action.get('AC', ''),
                action_text=_get_action_text(action),
                action_uid=action_uid,
                action_local_uid=action_local_uid,
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
                period=action.get('action_period', '')
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


@shared_task
def check_future():
    games = models.Game.objects.filter(status="future")
    for current_game in games:
        time_now = int(time.time())
        time_game = current_game.start_time / 1000
        time_difference = time_game - time_now

        if time_difference < 600:
            if not current_game.team_a or not current_game.team_b:
                game = Fiba_Game(current_game.code)
                data_available = game.data_available()
                if data_available['game_comp_details']:
                    team_a_temp, team_b_temp = game.get_teams()
                    team_a, _ = models.Team.objects.get_or_create(code=team_a_temp['code'],
                                                        defaults=team_a_temp)
                    team_a.save()
                    team_b, _ = models.Team.objects.get_or_create(code=team_b_temp['code'],
                                            defaults=team_b_temp)
                    team_b.save()
                    current_game.team_a = team_a
                    current_game.team_b = team_b
                    current_game.save()

        if time_difference < 60:
            game = Fiba_Game(current_game.code)
            available = game.data_available()
            if available['game_info']:
                info = game.get_info()
                current_game.start_time = info['start_time']
                current_game.team_a_score = info['team_a']['team_a_score']
                current_game.team_a_foul = info['team_a']['team_a_foul']
                current_game.team_b_score = info['team_b']['team_b_score']
                current_game.team_b_foul = info['team_b']['team_b_foul']
                current_game.current_period = info['current_period']
                current_game.time = info['time']
                current_game.team_a_period_scores = info['team_a']['team_a_scores']
                current_game.team_b_period_scores = info['team_b']['team_b_scores']
                init_locations(current_game.code)
                try:
                    location = Location.objects.get(code=info['location'])
                    current_game.location = location
                except:
                    pass
            players = game.get_players()
            if len(players) > 5:
                for player in players:
                    add_player.apply([player])
                current_game.status = "playing"

            current_game.save()


@shared_task
def check_playing():
    games = models.Game.objects.filter(status="playing")
    logger.info('Checking for games in PLAYING state. FOUND: %s' % len(games))
    for game in games:
        update_game_info.delay(game.pk)
        if game.init_scrape:
            get_game_actions.delay(game.code)
            game.init_scrape = False
            game.save()
        else:
            get_game_actions.delay(game.code, game.current_period)


@shared_task
def update_game_info(pk):
    game_model = models.Game.objects.get(pk=pk)
    logger.info('Updating game information. GAME: %s' % game_model.code)
    game = Fiba_Game(game_model.code)
    info = game.get_info()
    game_model.status = info['status']
    game_model.start_time = info['start_time']
    game_model.team_a_score = info['team_a']['team_a_score']
    game_model.team_a_foul = info['team_a']['team_a_foul']
    game_model.team_b_score = info['team_b']['team_b_score']
    game_model.team_b_foul = info['team_b']['team_b_foul']
    game_model.current_period = info['current_period']
    game_model.time = info['time']
    game_model.team_a_period_scores = info['team_a']['team_a_scores']
    game_model.team_b_period_scores = info['team_b']['team_b_scores']
    #tasks.init_locations(game_model.code)
    if not game_model.location:
        init_locations(game_model.code)
        try:
            location = models.Location.objects.get(code=info['location'])
            game_model.location = location
        except:
            pass
    game_model.save()