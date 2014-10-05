import xml.etree.ElementTree as ET
import argparse
import datetime
import time
from os import listdir
from os.path import isfile, join
from sets import Set
from sets import ImmutableSet

class GameDBReader:

    def __init__(self, name):
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
            

    def InitPlayByPlayIter(self):
        self.iter = self.root.iterfind('.//film')
        
    def GetNext(self):
        self.cur_elem = self.iter.next()

    def GetCurScore(self):
        return self.cur_elem.attrib['score']

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
            if self.player_to_team[player] == self.team_to_side[name]:
                ret_list.append(player)
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

    def GetPointsByPlayer(self, name):
        for player_stats in self.root.findall('.//player'):
            if player_stats.attrib['name'] == name:
                return int(player_stats.attrib['points'])
            
    def GetTimePlayedInSecondsByPlayer(self, name):
        for player_stats in self.root.findall('.//player'):
            if player_stats.attrib['name'] == name:
                pt = datetime.datetime.strptime(player_stats.attrib['min'],'%M:%S')
                return pt.second + pt.minute*60
            
    def GetStarters(self,team_name):
        return self.team_to_starters[ self.team_to_side[team_name] ] 
    

def offensive_efficiency(three_p_made, two_p_made, assists_made, three_p_attempts, two_p_attempts, turnovers, off_rebounds):
    return float(three_p_made + two_p_made  + assists_made) / float(three_p_attempts + two_p_attempts + assists_made + turnovers - off_rebounds)

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

parser.add_argument('--print_all_players_points_per_minute_all_teams', action='store_true',dest='print_all_players_points_per_minute_all_teams', default=False, help='print all teams points per minute in all teams')

parser.add_argument('--print_points_per_players', action='store_true',dest='print_points_per_players', default=False, help='print points per five players')

args = parser.parse_args()

files = []

for f in listdir(args.dir_name):
    if isfile(join(args.dir_name,f)):
        if f.endswith('.xml'):
           files.append(GameDBReader(f))

teams_set = Set()
for game_reader in files:
    for team in game_reader.GetTeams():
        teams_set.add(team)

if args.print_teams:
    print teams_set
        
if args.print_team_oe:
    print args.team_name + ' ' + str(get_team_oe(files,args.team_name))

    
if args.print_all_teams_oe:
    for team in teams_set:
        print team + ' ' + str(get_team_oe(files,team))
    

if args.print_all_players_points_per_minute:
    for game_reader in files:
        print 'game:'        
        for player in game_reader.GetPlayersByTeam(args.team_name):
            if game_reader.GetTimePlayedInSecondsByPlayer(player) > 0:
                print player + ' ' +  str(float(game_reader.GetPointsByPlayer(player)*60) / float(game_reader.GetTimePlayedInSecondsByPlayer(player)))


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
                print player + ' ' + '0'
            else:
                print player + ' ' + str(float(cur_players_points[player]*60)/float(cur_players_minutes[player]))

if args.print_points_per_players:
    points_scored_by_fivers = {}
    for game_reader in files:
        game_reader.InitPlayByPlayIter()
        cur_fivers = game_reader.GetStarters(args.team_name)
        key_fivers = ImmutableSet(cur_fivers)
        points_scored_by_fivers[key_fivers] = 0 
        while True:
            try:
                game_reader.GetNext()
                if game_reader.IsCurrentSwitch(args.team_name):
                    cur_fivers.remove(game_reader.GetCurrentPlayerOut())
                    cur_fivers.add(game_reader.GetCurrentPlayerIn())

                if (game_reader.IsCurrentScored(args.team_name)):
                    key_fivers = ImmutableSet(cur_fivers)
                    points_scored_by_fivers[key_fivers] = points_scored_by_fivers.get(key_fivers, 0) + game_reader.GetCurrentScored()
                    
            except StopIteration:
                break
        for fivers in points_scored_by_fivers.keys():
            print str(fivers) + ' ' + str(points_scored_by_fivers[fivers])
    
    

 
     
