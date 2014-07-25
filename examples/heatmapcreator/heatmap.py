'''
Created on Jul 16, 2014

Map overview values taken from here:
https://github.com/deStrO/eBot-CSGO-Web

@author: Chris
'''
from demoinfocsgo.demodump import DemoDump
from match import Match
import random
import sys
import math
from PIL import Image
from PIL import ImageDraw
import argparse



class MapOverview(object):
    sizeX = 0
    sizeY = 0
    startX = 0 
    startY = 0
    endX = 0
    endY = 0
    flip_vertical = False
    flip_horizontal = False
    resolution_x = 0
    resolution_y = 0
    map_name = None
    
    image = None
    
    def get_image(self):
        if not self.image:
            if not self.map_name:
                raise #No mapname set
            else:
                self.image = Image.open("overview/%s.png" % self.map_name)
        
        self.resolution_x = self.image.size[0]
        self.resolution_y = self.image.size[1]
        self.update_size()
        return self.image.copy() #give clean image every time
    
    
    def update_size(self):
        self.sizeX = self.endX - self.startX
        self.sizeY = self.endY - self.startY
        
    def convert_point(self, x, y):
        x += -self.startX if self.startX < 0 else self.startX
        y += -self.startY if self.startY < 0 else self.startY
        
        posX = math.floor((x / self.sizeX) * self.resolution_x)
        posY = math.floor((y / self.sizeY) * self.resolution_y)
        
        if self.flip_horizontal:
            posX = -(posX - self.resolution_x)
        if self.flip_vertical:
            posY = -(posY - self.resolution_y)
        
        return posX, posY
            
class CacheOverview(MapOverview):
    def __init__(self):
        self.startX = -1792
        self.startY = -1476
        self.endX = 3328
        self.endY = 2278
        self.flip_vertical = True
        self.map_name = "de_cache"
        self.update_size()

class Dust2Overview(MapOverview):
    def __init__(self):
        self.startX = -2216
        self.startY = -1176
        self.endX = 1792
        self.endY = 3244
        self.flip_vertical = True
        self.map_name = "de_dust2"
        self.update_size()
        
class InfernoOverview(MapOverview):
    def __init__(self):
        self.startX = -1980
        self.startY = -808
        self.endX = 2720
        self.endY = 3616
        self.flip_vertical = True
        self.map_name = "de_inferno"
        self.update_size()

class MirageOverview(MapOverview):
    def __init__(self):
        self.startX = -2672
        self.startY = -2672
        self.endX = 1440
        self.endY = 912
        self.flip_vertical = True
        self.map_name = "de_mirage"
        self.update_size()
        
class NukeOverview(MapOverview):
    def __init__(self):
        self.startX = -3008
        self.startY = -2496
        self.endX = 3523
        self.endY = 960
        self.flip_vertical = True
        self.map_name = "de_nuke"
        self.update_size()
        
class TrainOverview(MapOverview):
    def __init__(self):
        self.startX = -2036
        self.startY = -1792
        self.endX = 2028
        self.endY = 1820
        self.flip_vertical = True
        self.map_name = "de_train"
        self.update_size()

MAPS = {
        "de_cache" : CacheOverview,
        "de_dust2" : Dust2Overview,
        "de_inferno" : InfernoOverview,
        "de_mirage" : MirageOverview,
        "de_nuke" : NukeOverview,
        "de_train" : TrainOverview,
        }

class HeatmapGenerator(object):
    
    def __init__(self, filename, filter=None):
        self.demo = DemoDump()
        self.match = Match(self.demo)
        self.demo.open(filename)
        self.mapname = self.demo.demofile.demoheader.mapname
        self.map_overview = MAPS[self.mapname]()
        self.events = []
        self.event_points = {}
        self.map_overview.get_image() #Set size, make a fix for this later
        self.demo.register_on_gameevent("round_announce_match_start", self.reset)

        self.demo.register_on_gameevent("round_start", self.round_start)
        #self.demo.register_on_gameevent("smokegrenade_detonate", self.on_smoke)
        #self.demo.register_on_gameevent("flashbang_detonate", self.on_flash)

        self.filter = filter
        
    def add_event(self, event_name):
        self.events.append(event_name)
        self.event_points[event_name] = {}
        for i in range(0, 50):
            self.event_points[event_name][i] = []
        self.demo.register_on_gameevent(event_name, self.on_event)
        
    def reset(self, ignore=None):
        for i in range(0, 50):
            for event in self.events:
                self.event_points[event][i] = []
        self.current_round = 0
        
        
    def on_event(self, data):
        if self.match.current_round == 0:
            return
        if data.userid not in self.match.players.keys(): #Find out later
            print "ERROR: %i not found in player array" % data.userid
            data.userid = self.match.players[self.match.players.keys()[0]].userid
        
        player = self.match.players[data.userid]
        if self.filter is None or (str(data.userid) == self.filter or player.networkid == filter or player.name == filter):
            x, y = self.map_overview.convert_point(data.x, data.y)
            self.event_points[data.name][self.match.current_round].append((x, y, self.match.players[data.userid].team))
        
    def round_start(self, data):
        for event in self.events:
            self.event_points[event][self.match.current_round] = []
        

    def dump(self):
        self.demo.dump()
        for event in self.events:
            self.dump_halves(self.event_points[event], "%s_first_half" % event, "%s_second_half" % event)
        for userid, player in self.match.players.items():
            print vars(player)
            
        print "Total rounds %i" % self.match.current_round
        print self.match.team_score
        
    def dump_halves(self, points, first_half_name, second_half_name):
        fh_img = self.map_overview.get_image()
        sh_img = self.map_overview.get_image()
        fh_draw = ImageDraw.Draw(fh_img)
        sh_draw = ImageDraw.Draw(sh_img)
        
        
        ellipse_range = 2
        #first half
        for i in range(1, 16):
            for p in points[i]:
                color = (255,0, 0, 200) if p[2] == 2  else (0,0, 255, 200)
                fh_draw.ellipse((p[0]-ellipse_range, p[1]-ellipse_range, p[0]+ellipse_range, p[1]+ellipse_range), fill=color)
        
        fh_img.save("%s.png" % first_half_name)
        
        for i in range(16, self.match.current_round + 1):
            for p in points[i]:
                color = (255,0, 0, 200) if p[2] == 2  else (0,0, 255, 200)
                sh_draw.ellipse((p[0]-ellipse_range, p[1]-ellipse_range, p[0]+ellipse_range, p[1]+ellipse_range), fill=color)
        sh_img.save("%s.png" % second_half_name)
        
if __name__ == "__main__":

    if len(sys.argv) <= 1:
        print "heatmap.py demofile.dem"
        sys.exit()   
        
    parser = argparse.ArgumentParser(description='Create a heatmap from certain game events')
    parser.add_argument('-f', '--file', required=True, help="demo file to parse")
    parser.add_argument('-e', '--events', required=True, nargs='+', help="list of game events a heatmap needs to be generated from")
    parser.add_argument('--filter', required=False, help="userfilter to use")

    args = parser.parse_args()
        
    hmg = HeatmapGenerator(args.file, args.filter)
    [hmg.add_event(x) for x in args.events]
    hmg.dump()
    print "Done"