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
        self.kills = 0
        self.deaths = 0
        self.assists = 0
        self.kills_this_round = 0
        self.is_connected = True
        self.is_alive = False
        self.team = 0  # 2 is T, 3 is CT?
 

class Match(object):
    """
    Match object that holds certain game info
    """
    def __init__(self, demodump):
        self.demo = demodump
        self.demo.register_on_gameevent("round_announce_match_start", self.game_start)
        self.current_round = 0
        self.players = {}
        self.demo.register_on_gameevent("player_connect", self.player_connected)
        self.demo.register_on_gameevent("player_info", self.player_connected)
        self.demo.register_on_gameevent("player_disconnect", self.player_disconnected)
        self.demo.register_on_gameevent("player_team", self.player_join_team)
        self.demo.register_on_gameevent("player_connect_full", self.player_connected_full)
    
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
            self.players[data.userid] = Player(data.index, "ERR", data.userid, "ERR")
    
    def player_disconnected(self, data):
        if data.networkid == 'BOT':  # if bot, just remove
            pass
            #self.players.pop(data.userid, None)
        else:
            self.players[data.userid].is_connected = False
    
    def player_join_team(self, data):
        if data.team == 0:  # disconnect?
            return
        if data.userid not in self.players:
            self.players[data.userid] = Player(-1, "ERR", data.userid, "ERR")
        self.players[data.userid].team = data.team
    
    def game_start(self, data):
        self.current_round = 0
        self.demo.register_on_gameevent("round_start", self.round_start)
        self.demo.register_on_gameevent("round_end", self.round_end)
        
    def round_start(self, data):
        self.current_round += 1
               
    def round_end(self, data):
        pass