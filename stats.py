import xml.etree.ElementTree as ET

class GameDBReader:

    def __init__(self, name):
        self.tree = ET.parse(name)
        self.root = self.tree.getroot()
        self.team_to_side = {}
        self.side_to_team = {}
                         
        for team in self.root.findall('.//homename'):
            self.team_to_side[team.text] = '1'
            self.side_to_team['1'] = team.text
    
        for team in self.root.findall('.//awayname'):
            self.team_to_side[team.text] = '0'
            self.side_to_team['0'] = team.text
            
    def GetTeams(self):
        return self.team_to_side.keys()
            
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

                
game_reader = GameDBReader('isrleaguecup-418.xml')

for teams in game_reader.GetTeams():
    OE = float(game_reader.Get3PointersMadeByTeam(teams) + game_reader.Get2PointersMadeByTeam(teams) + game_reader.GetAssistsByTeam(teams)) / float(game_reader.Get3PointersAttemptsByTeam(teams) + game_reader.Get2PointersAttemptsByTeam(teams) + game_reader.GetAssistsByTeam(teams) + game_reader.GetTurnoversByTeam(teams) - game_reader.GetOffensiveReboundsByTeam(teams) )
    print teams + ' ' + str(OE)
    


   
    
    

 
    