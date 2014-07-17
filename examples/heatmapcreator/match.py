'''
Created on Jul 16, 2014

@author: Chris
'''
from demoinfocsgo.demodump import DemoDump

class Team:
    TEAM_T = 2
    TEAM_CT = 3

class Player(object):
    def __init__(self, index, name, userid, networkid):
        self.index = index
        self.name = name
        self.userid = userid
        self.networkid = networkid

        self.is_connected = True
        self.team = 0  # 2 is T, 3 is CT?
        
        self.reset_stats()
        
    def reset_stats(self):
        self.kills = 0
        self.deaths = 0
        self.assists = 0
        self.headshots = 0
        self.suicides = 0
 

class Match(object):
    """
    Match object that holds certain game info
    """
    def __init__(self, demodump):
        self.demo = demodump
        self.demo.register_on_gameevent("round_announce_match_start", self.game_start)
        self.current_round = 0
        self.players = {}
        self.team_score = [[0, 0], [0, 0]]
        self.demo.register_on_gameevent("player_connect", self.player_connected)
        self.demo.register_on_gameevent("player_info", self.player_connected)
        self.demo.register_on_gameevent("player_disconnect", self.player_disconnected)
        self.demo.register_on_gameevent("player_team", self.player_join_team)
        self.demo.register_on_gameevent("player_connect_full", self.player_connected_full)
        self.demo.register_on_gameevent("round_start", self.round_start)
        self.demo.register_on_gameevent("round_end", self.round_end)
        self.demo.register_on_gameevent("item_purchase", self.item_purchase)
        self.demo.register_on_gameevent("player_spawn", self.player_spawn)
        self.demo.register_on_gameevent("player_death", self.player_death)
        
        
    def player_death(self, data):
        if data.userid not in self.players:
            print "Player %i died, but could not be found" % data.userid
            return
        self.players[data.userid].deaths += 1
        
        if data.userid != data.attacker:  # not suicide?
            self.players[data.attacker].kills += 1
            if data.headshot:
                self.players[data.attacker].headshots += 1
        else:
            self.players[data.attacker].suicides += 1
            
            
        if data.assister != 0:  # someone assisted
            self.players[data.assister].assists += 1
            
    def item_purchase(self, data): #to update recent teams
        if data.userid not in self.players.keys():
            self.players[data.userid] = Player(-1, "PURCHASE", data.userid, "ERR")
        self.players[data.userid].team = data.team
    
    def player_spawn(self, data):
        if data.userid not in self.players.keys():
            self.players[data.userid] = Player(-1, "SPAWN", data.userid, "ERR")
        self.players[data.userid].team = data.teamnum
        
    def player_connected(self, data):
        if data.userid not in self.players.keys():
            self.players[data.userid] = Player(data.index, data.name, data.userid, data.networkid)
        self.players[data.userid].is_connected = True
        self.players[data.userid].index = data.index
        self.players[data.userid].name = data.name
        self.players[data.userid].userid = data.userid
        self.players[data.userid].networkid = data.networkid

    def player_connected_full(self, data):
        if data.userid not in self.players:
            self.players[data.userid] = Player(data.index, "CONNECTED_FULL", data.userid, "ERR")
    
    def player_disconnected(self, data):
        if data.networkid == 'BOT':  # if bot, just remove
            pass
            #self.players.pop(data.userid, None)
        else:
            self.players[data.userid].is_connected = False
            self.players[data.userid].networkid = data.networkid
            self.players[data.userid].name = data.name
    
    def player_join_team(self, data):
        if data.team == 0:  # disconnect?
            return
        if data.userid not in self.players:
            self.players[data.userid] = Player(-1, "JOIN_TEAM", data.userid, "ERR")
        self.players[data.userid].team = data.team
    
    def game_start(self, data):
        self.current_round = 0
        self.team_score = [[0, 0], [0, 0]]
        for index, player in self.players.items():
            player.reset_stats()
        
        
    
    def round_start(self, data):
        self.current_round += 1
               
    def round_end(self, data):
        half = self.current_round >= 15
        self.team_score[half][data.winner-2] += 1 #T = index 0, CT = index 1
        pass