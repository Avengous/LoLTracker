import LoL
from LoLRequest import Request
from LoLPlayer import Player
from LoLDB import Database as DB 
from time import time,sleep

CREATE_DATABASE = False
UPDATE_INTERVAL = 1

if CREATE_DATABASE:
	DB().createDatabase()

for id in LoL.PLAYERIDS:
	player = Player(id)
	if player.recordExists():
		if (int(time())-player.lastUpdated())/60 >= UPDATE_INTERVAL:
			print "[UPDATE] {}".format(id)
			player.update()
	else:
		print "[CREATE] {}".format(id)
		player.create()
	
	#Riot API Request Time Interval
	sleep(15)
		
		
