import xml.etree.ElementTree as ET
import argparse
import datetime
import time
from os import listdir
from os.path import isfile, join
from sets import Set
from sets import ImmutableSet
from collections import defaultdict
import math

class GameDBReader:

    def __init__(self, name):
        self.name = name
        self.tree = ET.parse(name)
        self.root = self.tree.getroot()
        self.team_to_side = {}
        self.side_to_team = {}
        self.player_to_team = {}
        self.player_to_code = {}
        self.code_to_player = {} 
        self.team_to_starters = {}
        self.team_to_starters['0'] = Set()
        self.team_to_starters['1'] = Set()
                         
        for team in self.root.findall('.//homename'):
            self.team_to_side[team.text] = '1'
            self.side_to_team['1'] = team.text
    
        for team in self.root.findall('.//awayname'):
            self.team_to_side[team.text] = '0'
            self.side_to_team['0'] = team.text

        for players in self.root.findall('.//players'):
            for player in players.findall('.//player'):
                if player.attrib['name'] != 'Team':
                    self.player_to_code[player.attrib['name']] = player.attrib['code']
                    self.code_to_player[player.attrib['code']] = player.attrib['name']
                    self.player_to_team[player.attrib['name']] = players.attrib['side']
                    if player.attrib['starter'] == '1':
                        self.team_to_starters[players.attrib['side']].add(player.attrib['name'])
            
    def GetName(self):
        return self.name
    
    def InitPlayByPlayIter(self):
        self.iter = self.root.iterfind('.//film')
        
    def GetNext(self):
        self.cur_elem = self.iter.next()

    def GetCurScore(self):
        return self.cur_elem.attrib['score']

    def GetCurrentTimeStamp(self):
        pt = datetime.datetime.strptime(self.cur_elem.attrib['min'],'%M:%S')
        return pt.second + pt.minute*60

    def GetCurrentScored(self):
        if self.cur_elem.attrib['shottype'] == '4':
            return 1
        if self.cur_elem.attrib['shottype'] == '2':
            return 2
        if self.cur_elem.attrib['shottype'] == '1':
            return 2
        if self.cur_elem.attrib['shottype'] == '5':
            return 2
        if self.cur_elem.attrib['shottype'] == '3':
            return 3
    
    def IsCurrentScored(self,team_name):
        try:
            if (self.cur_elem.attrib['fccode'] == '1000'):
                if self.cur_elem.attrib['side'] == '1':
                    side = '0'
                if self.cur_elem.attrib['side'] == '0':
                    side = '1'
                if (side == self.team_to_side[team_name]):
                    return True
            return False
        except KeyError:
            return False

    def IsCurrentFieldGoalAttempt(self):
        return_value = False
        try:
            if (self.cur_elem.attrib['fccode'] == '1000') or (self.cur_elem.attrib['fccode'] == '1001'):
                if self.cur_elem.attrib['shottype'] != '4':
                    return_value = True
        except KeyError:
            return return_value
        return return_value

    def IsCurrentFieldGoalMade(self):
        return_value = False
        try:
            if (self.cur_elem.attrib['fccode'] == '1000'):
                if self.cur_elem.attrib['shottype'] != '4':
                    return_value = True
        except KeyError:
            return return_value
        return return_value

    def GetDistanceFromBasket(self):
        x = float(self.cur_elem.attrib['x'])
        y = float(self.cur_elem.attrib['y'])
        
        
        
    def IsCurrentAllowedScore(self,team_name):
        try:
            if (self.cur_elem.attrib['fccode'] == '1000'):
                if self.cur_elem.attrib['side'] == '1':
                    side = '0'
                if self.cur_elem.attrib['side'] == '0':
                    side = '1'
                if (side != self.team_to_side[team_name]):
                    return True
            return False
        except KeyError:
            return False
        
        
    def IsCurrentSwitch(self,team_name):
        try:
            if (self.cur_elem.attrib['fccode'] == '1011'):
                if self.cur_elem.attrib['side'] == '1':
                    side = '0'
                if self.cur_elem.attrib['side'] == '0':
                    side = '1'
                if (side == self.team_to_side[team_name]):
                    return True
            return False
        except KeyError:
            return False

    def GetCurrentPlayerOut(self):
        return self.code_to_player[self.cur_elem.attrib['out']]

    def GetCurrentPlayerIn(self):
        return self.code_to_player[self.cur_elem.attrib['in']]
    
    def GetTeams(self):
        return self.team_to_side.keys()

    def GetPlayers(self):
        return self.player_to_code.keys()

    def GetPlayersByTeam(self,name):
        ret_list = []
        for player in self.GetPlayers():
            try:            
                if self.player_to_team[player] == self.team_to_side[name]:
                    ret_list.append(player)
            except KeyError:
                continue
                
        return ret_list
            
    def Get3PointersMadeByTeam(self, name):
        for team_stats in self.root.findall('.//ts'):
            if self.side_to_team[team_stats.attrib['side']]  == name:
                return int(team_stats.attrib['p3m'])
                
    def Get2PointersMadeByTeam(self, name): 
        for team_stats in self.root.findall('.//ts'):
            if self.side_to_team[team_stats.attrib['side']]  == name:
                return int(team_stats.attrib['p2m'])     

    def GetAssistsByTeam(self, name): 
        for team_stats in self.root.findall('.//ts'):
            if self.side_to_team[team_stats.attrib['side']]  == name:
                return int(team_stats.attrib['ass'])     

    def Get3PointersAttemptsByTeam(self, name): 
        for team_stats in self.root.findall('.//ts'):
            if self.side_to_team[team_stats.attrib['side']]  == name:
                return int(team_stats.attrib['p3a'])
                
    def Get2PointersAttemptsByTeam(self, name): 
        for team_stats in self.root.findall('.//ts'):
            if self.side_to_team[team_stats.attrib['side']]  == name:
                return int(team_stats.attrib['p2a'])
                
    def GetTurnoversByTeam(self, name): 
        for team_stats in self.root.findall('.//ts'):
            if self.side_to_team[team_stats.attrib['side']]  == name:
                return int(team_stats.attrib['tov'])   

    def GetOffensiveReboundsByTeam(self, name): 
        for team_stats in self.root.findall('.//ts'):
            if self.side_to_team[team_stats.attrib['side']]  == name:
                return int(team_stats.attrib['orb'])

    def GetDefensiveReboundsByTeam(self, name): 
        for team_stats in self.root.findall('.//ts'):
            if self.side_to_team[team_stats.attrib['side']]  == name:
                return int(team_stats.attrib['trb'])

    def GetPointsByPlayer(self, name):
        for player_stats in self.root.findall('.//player'):
            if player_stats.attrib['name'] == name:
                return int(player_stats.attrib['points'])

    def GetValueByPlayer(self,name):
        for player_stats in self.root.findall('.//player'):
            if player_stats.attrib['name'] == name:
                return int(player_stats.attrib['val'])
            
    def GetTimePlayedInSecondsByPlayer(self, name):
        for player_stats in self.root.findall('.//player'):
            if player_stats.attrib['name'] == name:
                pt = datetime.datetime.strptime(player_stats.attrib['min'],'%M:%S')
                return pt.second + pt.minute*60
            
    def GetStarters(self,team_name):
        return self.team_to_starters[ self.team_to_side[team_name] ]

    def GetOpponent(self,team_name):
        return_value = ""
        if self.side_to_team['1'] == team_name:
            return_value = self.side_to_team['0']
        else:
            return_value = self.side_to_team['1']
        return return_value

    def GetHomeTeam(self):
        for team in self.root.findall('.//homename'):
            return team.text

    def GetAwayTeam(self):
        for team in self.root.findall('.//awayname'):
            return team.text

    def GetHomeTeamScore(self):
        for team in self.root.findall('.//homescore'):
            return int(team.text)

    def GetAwayTeamScore(self):
        for team in self.root.findall('.//awayscore'):
            return int(team.text)


def team_scoring_percentage(made, attempted):
    if attempted == 0:
        return float(0)
    return float(made)/float(attempted)

def print_set(set):
    list_from_set = list(set)
    return ",".join(str(e) for e in sorted(list_from_set))


def offensive_efficiency(three_p_made, two_p_made, assists_made, three_p_attempts, two_p_attempts, turnovers, off_rebounds):
    return float(three_p_made + two_p_made  + assists_made) / float(three_p_attempts + two_p_attempts + assists_made + turnovers - off_rebounds)

def average(number_list):
    if len(number_list) == 0:
        return 0 
    return sum(number_list) * 1.0 / len(number_list)

def average_remove_exceptions(number_list):
    if len(number_list) > 2:
        return (sum(number_list) - max(number_list) - min(number_list)) * 1.0 / (len(number_list) - 2)
    else:
        return 0

def variance(number_list):
    avg = average(number_list)
    return average(map(lambda x: (x - avg)**2, number_list))

def std_dev(number_list):
    return math.sqrt(variance(number_list))
    

def get_team_oe(files,team_name):
    summary = {}
    summary['3pm'] = 0
    summary['2pm'] = 0
    summary['3pa'] = 0
    summary['2pa'] = 0
    summary['ass'] = 0
    summary['tov'] = 0
    summary['orb'] = 0
    
    for game_reader in files:
        for team in game_reader.GetTeams():
            if team == team_name:
                summary['3pm'] = summary['3pm'] + game_reader.Get3PointersMadeByTeam(team)
                summary['2pm'] = summary['2pm'] + game_reader.Get2PointersMadeByTeam(team)
                summary['3pa'] = summary['3pa'] + game_reader.Get3PointersAttemptsByTeam(team)
                summary['2pa'] = summary['2pa'] + game_reader.Get2PointersAttemptsByTeam(team)
                summary['ass'] = summary['ass'] + game_reader.GetAssistsByTeam(team)
                summary['tov'] = summary['tov'] + game_reader.GetTurnoversByTeam(team)
                summary['orb'] = summary['orb'] + game_reader.GetOffensiveReboundsByTeam(team)
    return offensive_efficiency(summary['3pm'], summary['2pm'], summary['ass'], summary['3pa'], summary['2pa'], summary['tov'], summary['orb'])              
    


parser = argparse.ArgumentParser(description='utility to process information from games')

parser.add_argument('--print_teams', action='store_true',dest='print_teams', default=False, help='print teams')

parser.add_argument('--print_team_oe', action='store_true',dest='print_team_oe', default=False, help='print team OE')

parser.add_argument('--print_all_teams_oe', action='store_true',dest='print_all_teams_oe', default=False, help='print all teams OE')

parser.add_argument('--team', dest='team_name', help='the team to analyze')

parser.add_argument('--dir_name', dest='dir_name', help='the directory containing the files to analyze')

parser.add_argument('--print_all_players_points_per_minute', action='store_true',dest='print_all_players_points_per_minute', default=False, help='print all players points per minute of a specified teams')

parser.add_argument('--print_all_players_all_teams_value', action='store_true',dest='print_all_players_all_teams_value', default=False, help='print all players value per minute in all teams')

parser.add_argument('--print_all_players_points_per_minute_all_teams', action='store_true',dest='print_all_players_points_per_minute_all_teams', default=False, help='print all teams points per minute in all teams')

parser.add_argument('--print_points_per_players', action='store_true',dest='print_points_per_players', default=False, help='print points per five players')

parser.add_argument('--wins_by_point_difference',action='store_true',dest='wins_by_point_difference', default=False, help='wins by point difference')

parser.add_argument('--wins_by_shooting_percentage',action='store_true',dest='wins_by_shooting_percentage', default=False, help='wins by shooting percentage')

parser.add_argument('--home_court_advantage',action='store_true',dest='home_court_advantage', default=False, help='wins by shooting percentage')

parser.add_argument('--average_rate_for_teams_by_game_result',action='store_true',dest='average_rate_for_teams_by_game_result', default=False, help='find average rate for winning team and losing team')

parser.add_argument('--average_rate_all_players',action='store_true',dest='average_rate_all_players', default=False, help='average rate')

parser.add_argument('--average_rate_against_team',action='store_true',dest='average_rate_against_team', default=False, help='average rate against a team')

parser.add_argument('--average_rate_against_team_all_teams',action='store_true',dest='average_rate_against_team_all_teams', default=False, help='average rate against a team for all teams')

parser.add_argument('--home_court_advantage_per_team',action='store_true',dest='home_court_advantage_per_team', default=False, help='How homey is each team')

parser.add_argument('--rebounds_against',action='store_true',dest='rebounds_against', default=False, help='How many defensive rebounds against a team')

parser.add_argument('--offensive_against',action='store_true',dest='offensive_against', default=False, help='How many offensive rebounds against a team')

parser.add_argument('--two_pointers_made_against',action='store_true',dest='two_pointers_made_against', default=False, help='How many 2 pointers were made against a team')

args = parser.parse_args()

files = []

for f in listdir(args.dir_name):
    if isfile(join(args.dir_name,f)):
        if f.endswith('.xml'):
            try:
                files.append(GameDBReader(f))
            except:
                print f 

teams_set = Set()
for game_reader in files:
    for team in game_reader.GetTeams():
        teams_set.add(team)

if args.print_teams:
    print teams_set
        
if args.print_team_oe:
    print str(get_team_oe(files,args.team_name)) + ',' + args.team_name

    
if args.print_all_teams_oe:
    for team in teams_set:
        print str(get_team_oe(files,team)) + ',' + team
    

if args.print_all_players_points_per_minute:
    for game_reader in files:
        print 'game:'        
        for player in game_reader.GetPlayersByTeam(args.team_name):
            if game_reader.GetTimePlayedInSecondsByPlayer(player) > 0:
                print str(float(game_reader.GetPointsByPlayer(player)*60) / float(game_reader.GetTimePlayedInSecondsByPlayer(player))) + "," + player

if args.print_all_players_all_teams_value:
    player_to_team = {}
    for team in teams_set:
        cur_players_minutes = {}
        cur_players_value = defaultdict(list)
        cur_players_value_home = defaultdict(list)
        cur_players_value_away = defaultdict(list)
        cur_players_team_against = defaultdict(list)
        for game_reader in files:
            for player in game_reader.GetPlayersByTeam(team):
                player_to_team[player] = team
                if game_reader.GetAwayTeam() == team:
                    cur_players_value_away[player].append(game_reader.GetValueByPlayer(player))
                else:
                    cur_players_value_home[player].append(game_reader.GetValueByPlayer(player))
                cur_players_minutes[player] = cur_players_minutes.get(player, 0) +  game_reader.GetTimePlayedInSecondsByPlayer(player)
                cur_players_value[player].append(game_reader.GetValueByPlayer(player))
                cur_players_team_against[player].append(game_reader.GetOpponent(team))
        for player in cur_players_value.keys():
            if cur_players_minutes[player]  == 0:
                print str(sum(cur_players_value[player])) + ',0.0,0,0,0,0,0,0,0,0,0,0,' + team + "," + player
            else:
                sorted_current = sorted(cur_players_value[player])
                print str(sum(cur_players_value[player])) + ',' +  str(float(sum(cur_players_value[player])*60)/float(cur_players_minutes[player])) + ',' + str(float(sum(cur_players_value[player]))/float(len(cur_players_value[player]))) + "," + str(average(cur_players_value_home[player])) + "," + str(average(cur_players_value_away[player])) + "," + str(max(cur_players_value[player]))  + "," + cur_players_team_against[player][cur_players_value[player].index(max(cur_players_value[player]))]  + "," + str(min(cur_players_value[player])) + "," + cur_players_team_against[player][cur_players_value[player].index(min(cur_players_value[player]))]  + "," +str(std_dev(cur_players_value[player])) + "," + str(average_remove_exceptions(cur_players_value[player])) + "," + str(sorted_current[len(sorted_current)/2])  + "," + team + "," + player


if args.print_all_players_points_per_minute_all_teams:
    for team in teams_set:
        cur_players_minutes = {}
        cur_players_points = {}
        for game_reader in files:
            for player in game_reader.GetPlayersByTeam(team):
                cur_players_minutes[player] = cur_players_minutes.get(player, 0) +  game_reader.GetTimePlayedInSecondsByPlayer(player)
                cur_players_points[player]  = cur_players_points.get(player, 0) + game_reader.GetPointsByPlayer(player)
        for player in cur_players_minutes.keys():
            if cur_players_minutes[player]  == 0:
                print '0,' + player
            else:
                print str(float(cur_players_points[player]*60)/float(cur_players_minutes[player])) + "," + player

if args.print_points_per_players:
    points_scored_by_fivers = {}
    seconds_played_by_fivers = {}
    points_allowed_by_fivers = {}
    total = 0 
    for game_reader in files:
        game_reader.InitPlayByPlayIter()
        cur_timestamp = 0
        try:
            cur_fivers = game_reader.GetStarters(args.team_name)
        except KeyError:
            continue
        key_fivers = ImmutableSet(cur_fivers)
        while True:
            try:
                game_reader.GetNext()
                current_play_timestamp = game_reader.GetCurrentTimeStamp()                    

                if game_reader.IsCurrentSwitch(args.team_name):
                    key_fivers = ImmutableSet(cur_fivers)
                    seconds_played_by_fivers[key_fivers] = seconds_played_by_fivers.get(key_fivers,0) + current_play_timestamp - cur_timestamp
                    cur_timestamp = current_play_timestamp
                    cur_fivers.remove(game_reader.GetCurrentPlayerOut())
                    cur_fivers.add(game_reader.GetCurrentPlayerIn())

                    
                if (game_reader.IsCurrentScored(args.team_name)):
                    key_fivers = ImmutableSet(cur_fivers)
                    points_scored_by_fivers[key_fivers] = points_scored_by_fivers.get(key_fivers, 0) + game_reader.GetCurrentScored()
                    
                if (game_reader.IsCurrentAllowedScore(args.team_name)):
                    key_fivers = ImmutableSet(cur_fivers)
                    points_allowed_by_fivers[key_fivers] = points_allowed_by_fivers.get(key_fivers, 0) + game_reader.GetCurrentScored()
                    total = total + game_reader.GetCurrentScored()

                    
            except StopIteration:
                key_fivers = ImmutableSet(cur_fivers)
                seconds_played_by_fivers[key_fivers] = seconds_played_by_fivers.get(key_fivers,0) + current_play_timestamp - cur_timestamp
                break

            
    for fivers in seconds_played_by_fivers.keys():
        try:
            print str(float(points_scored_by_fivers.get(fivers,0))*60/seconds_played_by_fivers[fivers]) + ',' + str(points_scored_by_fivers.get(fivers,0)) + ',' + str(seconds_played_by_fivers[fivers]) + ',' + str(points_allowed_by_fivers.get(fivers,0)) + ',' + str(float(points_scored_by_fivers.get(fivers,0) - points_allowed_by_fivers.get(fivers,0))*60/seconds_played_by_fivers[fivers]) + ',' + print_set(fivers)
        except ZeroDivisionError:
            continue
    
if args.wins_by_point_difference:
    team_to_points_margin = defaultdict(int)
    total_number_of_games_of_viable_prediction = 0
    total_number_of_correct_predictions = 0
    train_set = 0 
    for game_reader in files:
        if train_set > 50:
            if team_to_points_margin[game_reader.GetHomeTeam()] != team_to_points_margin[game_reader.GetAwayTeam()]:
                total_number_of_games_of_viable_prediction = total_number_of_games_of_viable_prediction + 1
                if team_to_points_margin[game_reader.GetHomeTeam()] > team_to_points_margin[game_reader.GetAwayTeam()]:
                    if game_reader.GetHomeTeamScore() > game_reader.GetAwayTeamScore():
                        total_number_of_correct_predictions = total_number_of_correct_predictions + 1
            
                if team_to_points_margin[game_reader.GetAwayTeam()] > team_to_points_margin[game_reader.GetHomeTeam()]:
                    if game_reader.GetAwayTeamScore() > game_reader.GetHomeTeamScore():
                        total_number_of_correct_predictions = total_number_of_correct_predictions + 1
        train_set = train_set + 1 
        team_to_points_margin[game_reader.GetHomeTeam()] = team_to_points_margin[game_reader.GetHomeTeam()] + int(game_reader.GetHomeTeamScore()) - int(game_reader.GetAwayTeamScore())
        team_to_points_margin[game_reader.GetAwayTeam()] = team_to_points_margin[game_reader.GetAwayTeam()] + int(game_reader.GetAwayTeamScore()) - int(game_reader.GetHomeTeamScore())

    print float(total_number_of_correct_predictions) / float(total_number_of_games_of_viable_prediction), total_number_of_games_of_viable_prediction
          

if args.wins_by_shooting_percentage:
    team_field_goals_attempted = defaultdict(int)
    team_field_goals_made = defaultdict(int)
    total_number_of_games_of_viable_prediction = 0
    total_number_of_correct_predictions = 0
    train_set = 0 
    for game_reader in files:
        if train_set > 50:
            if team_scoring_percentage(team_field_goals_made[game_reader.GetHomeTeam()],team_field_goals_attempted[game_reader.GetHomeTeam()]) != team_scoring_percentage(team_field_goals_made[game_reader.GetAwayTeam()],team_field_goals_attempted[game_reader.GetAwayTeam()]):
                total_number_of_games_of_viable_prediction = total_number_of_games_of_viable_prediction + 1
                if team_scoring_percentage(team_field_goals_made[game_reader.GetHomeTeam()],team_field_goals_attempted[game_reader.GetHomeTeam()]) > team_scoring_percentage(team_field_goals_made[game_reader.GetAwayTeam()],team_field_goals_attempted[game_reader.GetAwayTeam()]):
                    total_number_of_correct_predictions = total_number_of_correct_predictions + 1
                    
                if team_scoring_percentage(team_field_goals_made[game_reader.GetAwayTeam()],team_field_goals_attempted[game_reader.GetAwayTeam()]) > team_scoring_percentage(team_field_goals_made[game_reader.GetHomeTeam()],team_field_goals_attempted[game_reader.GetHomeTeam()]):
                    if game_reader.GetAwayTeamScore() > game_reader.GetHomeTeamScore():
                        total_number_of_correct_predictions = total_number_of_correct_predictions + 1

        team_field_goals_attempted[game_reader.GetHomeTeam()] = team_field_goals_attempted[game_reader.GetHomeTeam()] + game_reader.Get3PointersAttemptsByTeam(game_reader.GetHomeTeam()) + game_reader.Get2PointersAttemptsByTeam(game_reader.GetHomeTeam())
        team_field_goals_made[game_reader.GetHomeTeam()] = team_field_goals_attempted[game_reader.GetHomeTeam()] + game_reader.Get3PointersMadeByTeam(game_reader.GetHomeTeam()) + game_reader.Get2PointersMadeByTeam(game_reader.GetHomeTeam())
        

        team_field_goals_attempted[game_reader.GetAwayTeam()] = team_field_goals_attempted[game_reader.GetAwayTeam()] + game_reader.Get3PointersAttemptsByTeam(game_reader.GetAwayTeam()) + game_reader.Get2PointersAttemptsByTeam(game_reader.GetAwayTeam())
        team_field_goals_made[game_reader.GetAwayTeam()] = team_field_goals_attempted[game_reader.GetAwayTeam()] + game_reader.Get3PointersMadeByTeam(game_reader.GetAwayTeam()) + game_reader.Get2PointersMadeByTeam(game_reader.GetAwayTeam())
        train_set = train_set + 1
    print float(total_number_of_correct_predictions) / float(total_number_of_games_of_viable_prediction),total_number_of_games_of_viable_prediction 

                                                             

if args.home_court_advantage:
    total_games = 0
    total_games_won_by_home_team = 0
    for game_reader in files:
        total_games = total_games + 1 
        if game_reader.GetHomeTeamScore() > game_reader.GetAwayTeamScore():
            total_games_won_by_home_team = total_games_won_by_home_team + 1
            
    print float(total_games_won_by_home_team) / float(total_games)

if args.average_rate_for_teams_by_game_result:
    rate_for_winning_teams = []
    rate_for_losing_teams = []

    max_rate_for_winning_teams = []
    max_rate_for_losing_teams = []
    
    for game_reader in files:
        cur_team_win = []
        cur_team_lose = []
        
        if game_reader.GetHomeTeamScore() > game_reader.GetAwayTeamScore():
            for player in game_reader.GetPlayersByTeam(game_reader.GetHomeTeam()):
                if game_reader.GetTimePlayedInSecondsByPlayer(player) > 0:
                    rate_for_winning_teams.append(game_reader.GetValueByPlayer(player))
                    cur_team_win.append(game_reader.GetValueByPlayer(player))
            for player in game_reader.GetPlayersByTeam(game_reader.GetAwayTeam()):
                if game_reader.GetTimePlayedInSecondsByPlayer(player) > 0:
                    rate_for_losing_teams.append(game_reader.GetValueByPlayer(player))
                    cur_team_lose.append(game_reader.GetValueByPlayer(player))
        else:
            for player in game_reader.GetPlayersByTeam(game_reader.GetHomeTeam()):
                if game_reader.GetTimePlayedInSecondsByPlayer(player) > 0:
                    rate_for_losing_teams.append(game_reader.GetValueByPlayer(player))
                    cur_team_lose.append(game_reader.GetValueByPlayer(player))
                    
            for player in game_reader.GetPlayersByTeam(game_reader.GetAwayTeam()):
                if game_reader.GetTimePlayedInSecondsByPlayer(player) > 0:
                    rate_for_winning_teams.append(game_reader.GetValueByPlayer(player))
                    cur_team_win.append(game_reader.GetValueByPlayer(player))
        max_rate_for_winning_teams.append(max(cur_team_win))
        max_rate_for_losing_teams.append(max(cur_team_lose))



    print 'winning,' + str(average(rate_for_winning_teams)) + ',max,' + str(max(rate_for_winning_teams))
    print 'losing,' + str(average(rate_for_losing_teams)) + ',max,' + str(max(rate_for_losing_teams))

    print 'average max winning,' + str(average(max_rate_for_winning_teams))
    print 'average max losing,' + str(average(max_rate_for_losing_teams))
            

    
            
if args.average_rate_all_players:
    players_rate = []
    for game_reader in files:
        for player in game_reader.GetPlayersByTeam(game_reader.GetHomeTeam()):
            if game_reader.GetTimePlayedInSecondsByPlayer(player) > 0:
                players_rate.append(game_reader.GetValueByPlayer(player))
            
        for player in game_reader.GetPlayersByTeam(game_reader.GetAwayTeam()):
            if game_reader.GetTimePlayedInSecondsByPlayer(player) > 0:
                players_rate.append(game_reader.GetValueByPlayer(player))

    print 'average on all playing players,' + str(average(players_rate))

if args.average_rate_against_team:
    players_rate = []
    for game_reader in files:
        team = 'None'
        if args.team_name == game_reader.GetHomeTeam():
            team = game_reader.GetAwayTeam()
        if args.team_name == game_reader.GetAwayTeam():
            team = game_reader.GetHomeTeam()

        if team != 'None':
            for player in game_reader.GetPlayersByTeam(team):
                if game_reader.GetTimePlayedInSecondsByPlayer(player) > 0:
                    print str (game_reader.GetValueByPlayer(player)) + ',' + player
                    players_rate.append(game_reader.GetValueByPlayer(player))
    
    print 'average on players against ' + args.team_name + ',' + str(average(players_rate))

if args.average_rate_against_team_all_teams:
    for cur_team in teams_set:
        players_rate = []
        for game_reader in files:
            team = 'None'
            if cur_team == game_reader.GetHomeTeam():
                team = game_reader.GetAwayTeam()
            if cur_team == game_reader.GetAwayTeam():
                team = game_reader.GetHomeTeam()

            if team != 'None':
                for player in game_reader.GetPlayersByTeam(team):
                    if game_reader.GetTimePlayedInSecondsByPlayer(player) > 0:
                        players_rate.append(game_reader.GetValueByPlayer(player))
    
        print str(average(players_rate)) + ',' + cur_team

if args.home_court_advantage_per_team:
    for cur_team in teams_set:
        total_games = 0
        total_games_won_by_home_team = 0
        total_games_away = 0
        total_games_won_by_away_team = 0

        for game_reader in files:
            if game_reader.GetHomeTeam() == cur_team :
                total_games = total_games + 1
                if game_reader.GetHomeTeamScore() > game_reader.GetAwayTeamScore():
                    total_games_won_by_home_team = total_games_won_by_home_team + 1
            if game_reader.GetAwayTeam() == cur_team :
                total_games_away = total_games_away + 1
                if game_reader.GetHomeTeamScore() < game_reader.GetAwayTeamScore():
                    total_games_won_by_away_team = total_games_won_by_away_team + 1

        print str(float(total_games_won_by_home_team) * 100 / float(total_games)) + ',' + str(float(total_games_won_by_away_team) * 100 / float(total_games_away))  + "," + cur_team
    
if args.rebounds_against:
     for cur_team in teams_set:
          rebounds = []
          
          for game_reader in files:
               team = "None"
               if game_reader.GetHomeTeam() == cur_team:
                    team = game_reader.GetAwayTeam()
               if game_reader.GetAwayTeam() == cur_team:
                    team = game_reader.GetHomeTeam()

               if team == "None":
                    continue
               rebounds.append(game_reader.GetDefensiveReboundsByTeam(team))

          print str(average(rebounds)) + ',' + cur_team

if args.offensive_against:
     for cur_team in teams_set:
          rebounds = []
          
          for game_reader in files:
               team = "None"
               if game_reader.GetHomeTeam() == cur_team:
                    team = game_reader.GetAwayTeam()
               if game_reader.GetAwayTeam() == cur_team:
                    team = game_reader.GetHomeTeam()

               if team == "None":
                    continue
               rebounds.append(game_reader.GetOffensiveReboundsByTeam(team))

          print str(average(rebounds)) + ',' + cur_team


if args.two_pointers_made_against:
     for cur_team in teams_set:
          list = []
          
          for game_reader in files:
               team = "None"
               if game_reader.GetHomeTeam() == cur_team:
                    team = game_reader.GetAwayTeam()
               if game_reader.GetAwayTeam() == cur_team:
                    team = game_reader.GetHomeTeam()

               if team == "None":
                    continue
               list.append(game_reader.Get2PointersMadeByTeam(team))

          print str(average(list)) + ',' + cur_team
          
               


# if args.get_shooting_percentage_by_distance:
#      attempts_per_distance = defaultdict(int)
#      made_per_distance = defaultdict(int)
#      for game_reader in files:
#          game_reader.InitPlayByPlayIter()
#          while True:
#              try:
#                  game_reader.GetNext()
#                  if game_reader.IsCurrentFieldGoalAttempt():
#                      distance_from_basket = game_reader.GetDistanceFromBasket()
#                      rounded_distance = round(distance_from_basket, 0)
#                      attempts_per_distance[rounded_distance] = attempts_per_distance[rounded_distance] + 1
#                      if game_reader.IsCurrentFieldGoalMade():
#                          made_per_distance[rounded_distance] = made_per_distance[rounded_distance] + 1             

#              except StopIteration:
#                  break
#      print attempts_per_distance 
#      print made_per_distance


