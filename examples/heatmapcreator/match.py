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
        self.demo.register_on_gameevent(40, self.game_start)
        self.current_round = 0
        self.players = {}
        self.demo.register_on_gameevent(7, self.player_connected)
        self.demo.register_on_gameevent(8, self.player_connected)
        self.demo.register_on_gameevent(9, self.player_disconnected)
        self.demo.register_on_gameevent(21, self.player_join_team)
    
    def player_connected(self, data):
        if data.userid not in self.players.keys():
            self.players[data.userid] = Player(data.index, data.name, data.userid, data.networkid)
        self.players[data.userid].is_connected = True
        
    def player_disconnected(self, data):
        if data.networkid == 'BOT':  # if bot, just remove
            self.players.pop(data.userid, None)
        else:
            self.players[data.userid].is_connected = False
    
    def player_join_team(self, data):
        if data.team == 0:  # disconnect?
            return
        self.players[data.userid].team = data.team
    
    def game_start(self, data):
        self.current_round = 0
        self.demo.register_on_gameevent(36, self.round_start)
        self.demo.register_on_gameevent(42, self.round_end)
        
    def round_start(self, data):
        self.current_round += 1
               
    def round_end(self, data):
        pass