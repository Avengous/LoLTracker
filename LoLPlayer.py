#- This module will manage the player data structure.

from time import sleep
from LoLDB import Database as DB
from LoLRequest import Request

class Player():
	
	def __init__(self, playerId):
		self.db = DB()
		self.playerId = playerId
		self.riot = Request()
	
	def recordExists(self):
		player = self.db.getPlayer(self.playerId)
		if len(player.fetchall()):
			return True
		else:
			return False
			
	def lastUpdated(self):
		return self.db.getPlayerLastUpdated(self.playerId)
		
	def create(self):
		self.db.createPlayer(self.playerId)
		
	def close(self):
		self.db._close()
		
	def update(self):
		while True:
			try:
				playerdata = self.riot.retrievePlayerData(self.playerId)
				break
			except:
				sleep(15)
		for match in playerdata['match_history']['matches']:
			self.db.addMatch(match.items())
		self.close()