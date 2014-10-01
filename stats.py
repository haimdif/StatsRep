import xml.etree.ElementTree as ET
import argparse
import datetime
import time
from os import listdir
from os.path import isfile, join
from sets import Set

class GameDBReader:

    def __init__(self, name):
        self.tree = ET.parse(name)
        self.root = self.tree.getroot()
        self.team_to_side = {}
        self.side_to_team = {}
        self.player_to_team = {}
        self.player_to_code = {}
                         
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
                    self.player_to_team[player.attrib['name']] = players.attrib['side']
            
            
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

parser = argparse.ArgumentParser(description='utility to process information from games')

parser.add_argument('--print_teams', action='store_true',dest='print_teams', default=False, help='print teams')

parser.add_argument('--print_team_oe', action='store_true',dest='print_team_oe', default=False, help='print team OE')

parser.add_argument('--print_all_teams_oe', action='store_true',dest='print_all_teams_oe', default=False, help='print all teams OE')

parser.add_argument('--team', dest='team_name', help='the team to analyze')

parser.add_argument('--dir_name', dest='dir_name', help='the directory containing the files to analyze')

parser.add_argument('--print_all_players_points_per_minute', action='store_true',dest='print_all_players_points_per_minute', default=False, help='print all teams OE')

args = parser.parse_args()

files = []

for f in listdir(args.dir_name):
    if isfile(join(args.dir_name,f)):
        if f.endswith('.xml'):
           files.append(GameDBReader(f))

if args.print_teams:
    teams_set = Set()
    for game_reader in files:
        for team in game_reader.GetTeams():
            teams_set.add(team)
    print teams_set
        
if args.print_team_oe:
    for teams in game_reader.GetTeams():
        if teams == args.team_name:
            OE = float(game_reader.Get3PointersMadeByTeam(teams) + game_reader.Get2PointersMadeByTeam(teams) + game_reader.GetAssistsByTeam(teams)) / float(game_reader.Get3PointersAttemptsByTeam(teams) + game_reader.Get2PointersAttemptsByTeam(teams) + game_reader.GetAssistsByTeam(teams) + game_reader.GetTurnoversByTeam(teams) - game_reader.GetOffensiveReboundsByTeam(teams) )
            print teams + ' ' + str(OE)

if args.print_all_teams_oe:
    for teams in game_reader.GetTeams():
            OE = float(game_reader.Get3PointersMadeByTeam(teams) + game_reader.Get2PointersMadeByTeam(teams) + game_reader.GetAssistsByTeam(teams)) / float(game_reader.Get3PointersAttemptsByTeam(teams) + game_reader.Get2PointersAttemptsByTeam(teams) + game_reader.GetAssistsByTeam(teams) + game_reader.GetTurnoversByTeam(teams) - game_reader.GetOffensiveReboundsByTeam(teams) )
            print teams + ' ' + str(OE)

if args.print_all_players_points_per_minute:
    for player in game_reader.GetPlayersByTeam(args.team_name):
        if game_reader.GetTimePlayedInSecondsByPlayer(player) > 0:
            print player + ' ' +  str(float(game_reader.GetPointsByPlayer(player)*60) / float(game_reader.GetTimePlayedInSecondsByPlayer(player)))


   
    
    

 
    
