demoinfo-csgo-python
====================

demoinfocsgo is a python library that is able to parse CSGO GOTV and POV demos.

It currently currently has the following features:
- Registering a callback when a net or svc message is found.
- Registering a callback when a certain game event happened (see [examples/highlightfinder.py](https://github.com/Bakkes/demoinfo-csgo-python/blob/master/examples/highlightfinder.py) and [data/game_events.txt](https://github.com/Bakkes/demoinfo-csgo-python/blob/master/data/game_events.txt))

TODO:
- Parsing usermessages
- Parsing stringtables

## Examples
Example usage:
```
demo = DemoDump() #Create demodump instance
demo.open("gotv.dem") #open a demo file

#register on events
demo.register_on_netmsg(net_SetConVar, on_list_received) #net_SetConVar = net message id, 2nd param is callback
demo.register_on_gameevent("player_connect", player_connected) #player_connect = game event name (see data/game_events.txt), 2nd param is callback

demo.dump() #start analyzing the demo
```
For full examples check the [examples](https://github.com/Bakkes/demoinfo-csgo-python/blob/master/examples/) folder.

## Tooling
This project also includes some extra tools, such as the packet analyzer. This tool was made using the demoinfocsgo library:
![Picture](http://i.imgur.com/botaslu.png)
The source can be found in in the [packetinspector](https://github.com/Bakkes/demoinfo-csgo-python/tree/master/packetinspector) directory.
