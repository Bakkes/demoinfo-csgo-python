'''
Created on Jul 11, 2014

@author: Chris
'''
import sys
from demodump import DemoDump
if __name__ == '__main__':
    demo = DemoDump()
    filename = sys.argv[1]
    
    if len(sys.argv) <= 1:
        print "main.py demofile.dem"
        sys.exit()
    
    if(demo.open(filename)):
        demo.dump()