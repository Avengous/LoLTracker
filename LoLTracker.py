import LoL
from LoLRequest import Request
from LoLPlayer import Player
from LoLDB import Database as DB 
from time import time,sleep

UPDATE_INTERVAL = 60

try:
	DB().createDatabase()
except:
	pass
	
while True:
	for id in LoL.PLAYERIDS:
		player = Player(id)
		if not player.hasRecord():
			print "[CREATE] {}".format(id)
			player.retrieveMatches(newPlayer=True)
		elif player.lastUpdated()/60 >= UPDATE_INTERVAL:
			print "[UPDATE] {}".format(id)
			player.retrieveMatches()
	sleep(15)