from time import sleep
from LoLDB import Database as DB

class Player():
	
	def __init__(self, playerId):
		self.db = DB()
		self.playerId = playerId
		
	def hasRecord(self):
		try:
			self.db._select('players', 'name', self.playerId).fetchall()[0]
			return True
		except:
			return False
		
	def lastUpdated(self):
		return self.db.getPlayerLastUpdated(self.playerId).fetchone()[0]
		
	def retrieveMatches(self, newPlayer=False):
		self.db.addMatchHistory(self.playerId, newRecord=newPlayer)