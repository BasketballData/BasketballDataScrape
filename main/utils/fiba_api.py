import logging
import requests

logger = logging.getLogger(__name__)


BASE_URL = "https://livecache.sportresult.com/node/db/FIBASTATS_PROD/%s%s%s%sJSON.json?s=534&t=0"
BASE_GAME_INFO = "GAME_"
BASE_ACTIONS_INFO = "GAMEACTIONS_"
BASE_COMP_DETAILS = "COMPDETAILS_"
BASE_STANDINGDATA = "STANDINGDATA_"
STATUSES = {
    'Event-1-': 'future',
    'Event-2-': 'future',
    'Event-4-': 'playing',
    'Event-6-': 'future',
    'Event-7-': 'finished',
    'Event-9-': 'future',
    'Event-11-': 'future',
    'Event-12-': 'finished',
    'Event-13-': 'future',
    'Event-14-': 'future',
    'Event-15-': 'finished',
    'Event-50-': 'playing',
    'Event-99-': 'finished',    
    'Event-999-': 'finished',
}
BASE_fLAG = "http://www.fiba.basketball/img/flags/90x/%s.jpg"

class Fiba_Game:
    def __init__(self, code):
        self.code = code
        self.league, self.game = code.split('&')
        self.league += '_'
        self.game += '_'
        
    
    def get_info(self):
        """ Returns information of the game """
        response = self._make_request(BASE_GAME_INFO, self.league, self.game)
        try:
            team_a_score = int(response['content']['full']['Competitors'][0]['Score'])
            team_b_score = int(response['content']['full']['Competitors'][1]['Score'])
        except Exception as e:
            print('ERROR: %s' % e)
            team_a_score = 0
            team_b_score = 0
        
        tmp_a_scores = response['content']['full']['Competitors'][0]['Periods']
        team_a_scores = ''
        for q in tmp_a_scores:
            team_a_scores +=  q['Score'] + ' '
        
        tmp_b_scores = response['content']['full']['Competitors'][1]['Periods']
        team_b_scores = ''
        for q in tmp_b_scores:
            team_b_scores +=  q['Score'] + ' '
        
        information = {
            'status': STATUSES[response['content']['full']['Status']],
            'team_a': {
                'team_a_uid': response['content']['full']['Competitors'][0]['Id'],
                'team_a_score': team_a_score,
                'team_a_foul': response['content']['full']['Competitors'][0]['Stats']['A_FOUL'],
                'team_a_scores': team_a_scores,
            }, 
            'team_b': {
                'team_b_uid': response['content']['full']['Competitors'][1]['Id'],
                'team_b_score': team_b_score,
                'team_b_foul':  response['content']['full']['Competitors'][1]['Stats']['A_FOUL'],
                'team_b_scores': team_b_scores,
            },
            'current_period': response['content']['full']['CurrentPeriod'],
            'start_time': response['content']['full']['StartTime'],
            'location': response['content']['full']['Location'],
            'time': response['content']['full']['RC'],
        }
        return information
    
    def get_locations(self):
        """ Returns a list of locations """
        response = self._make_request(BASE_STANDINGDATA, self.league)
        return response['content']['full']['Locations']


    def get_teams(self):
        """ Returns information about competitors of the game """
        response = self._make_request(BASE_COMP_DETAILS, self.league, self.game)
        team_a = None
        team_b = None
        for key, value in response['content']['full']['Competitors'].items():
            if value['IsTeam']:
                if not team_a:
                    team_a = {
                        'code': value['Id'],
                        'name': value['Name'],
                        'nationality': value['Nationality'],
                        'flag': BASE_fLAG % value['Nationality']
                    }
                elif not team_b:
                    team_b = {
                        'code': value['Id'],
                        'name': value['Name'],
                        'nationality': value['Nationality'],
                        'flag': BASE_fLAG % value['Nationality']
                    }
                else:
                    break
        return team_a, team_b

    def get_players(self):
        """ Returns information about players of the game """
        response = self._make_request(BASE_COMP_DETAILS, self.league, self.game)
        players = []

        for key, value in response['content']['full']['Competitors'].items():
            if not value['IsTeam']:
                player = {
                    'code': value['Id'],
                    'first_name': value['FirstName'],
                    'last_name': value['Name'],
                    'headshot': value['HeadShot'],
                    'team_unique_id': value['ParentId']
                }
                players.append(player)
        return players

    def get_actions(self, period=None):
        """ Returns single or all periods actions
            period varaible must have trailing underscore _
            example: Q1_, Q2_, etc..
         """

        def _next_period(period):
            """ Get next period """
            periods = {
                'Q1_': 'Q2_',
                'Q2_': 'Q3_',
                'Q3_': 'Q4_',
                'Q4_': 'OT1_',
                'OT1_': 'OT2_',
                'OT2_': 'OT3_',
                'OT3_': 'OT4_'
            }
            return periods[period]
        actions = []
        start_period = 'Q1_'
        if not period:
            finished = False
            while not finished:
                response = self._make_request(BASE_ACTIONS_INFO, self.league, self.game, start_period)
                if not response:
                    print('BAD RESPONSE')
                    break
                actions = actions + response['content']['full']['Items']
                for item in response['content']['full']['Items']:
                    if item['AC'] == 'ENDG':
                        # Game Ended
                        finished = True
                        break
                    elif item['AC'] == 'ENDP':
                        # Period Ended
                        start_period = _next_period(start_period)
                        break
                    else:
                        if item == response['content']['full']['Items'][-1]:
                            start_period = _next_period(start_period)
                        else:
                            pass
            return actions
        else:
            # Get particular period
            response = self._make_request(BASE_ACTIONS_INFO, self.league, self.game, period)
            actions = response['content']['full']['Items']
            return actions


    def _make_request(self, endpoint, league, game='', period=''):
        """ Base function for making requests to FIBA """
        good_status = [200, 304]
        url = BASE_URL % (league, endpoint, game, period)
        print('MAKING NEW REQUEST: %s' % url)
        response = requests.get(url)
        if response.status_code in good_status:
            return response.json()
        else: 
            return None