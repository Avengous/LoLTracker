#- This module interacts with the database.

import sqlite3
import time

class Database():
	
	def __init__(self):
		self.connection = sqlite3.connect('loltracker.db')
		self.db = self.connection.cursor()
	
	def _commit(self):
		self.connection.commit()
	
	def _close(self):
		self.connection.close()
	
	def _updateTable(self, table, pairs):
		print 'table', table
		print 'pairs', pairs
		#self.db.execute("INSERT INTO {0}({}) VALUES({})".format(table, pairs))
	
	def createDatabase(self):
		self.db.execute('''CREATE TABLE matches
						   ( date text,
							 matchSummonerId int,
							 queueType text,
							 matchVersion text,
							 platformId int, 
							 season text,
							 region text,
							 matchId int,
							 mapId int,
							 matchCreation text,
							 matchMode text,
							 matchDuration int,
							 matchType text,
							 PRIMARY KEY(matchId)
							 FOREIGN KEY(matchSummonerId) REFERENCES identities(summonerId)
							)''')
							
		self.db.execute('''CREATE TABLE participants
						   ( date text, 
							 pMatchId text,
							 masteries text,
							 spell1Id int,
							 spell2Id int,
							 stats text,
							 participantsId int,
							 runes text,
							 highestAchievedSeasonTier text,
							 championId int,
							 timeline text,
							 teamId int,
							 FOREIGN KEY(pMatchId) REFERENCES matches(matchId)
							)''')
							
		self.db.execute('''CREATE TABLE identities
						   ( date text,
							 lastUpdated int,
							 profileIcon text,
							 summonerId int,
							 matchHistoryUri text,
							 summonerName text,
							 PRIMARY KEY(summonerId)
							)''')
		
		self.db.execute('''CREATE TABLE users
						   ( dateCreated int,
							 lastUpdated int,
							 playerId text
							)''')
		
		self._commit()
		self._close()
	
	def createPlayer(self, playerId):
		dateCreated = int(time.time())
		lastUpdated = int(time.time())
		self.db.execute("INSERT INTO users(dateCreated, lastUpdated, playerId) VALUES({}, {}, '{}')".format(dateCreated, lastUpdated, playerId))
		self._commit()
	
	def getPlayer(self, playerId):
		record = self.db.execute("SELECT * FROM users WHERE playerId=?", (playerId,))
		return record
	
	def getPlayerLastUpdated(self, playerId):
		record = self.db.execute("SELECT * FROM users WHERE playerId=?", (playerId,))
		for row in record:
			lastUpdated = row[1]
		return lastUpdated
		
	def addMatch(self, matchItems):
		for i in range(0,13):
			print matchItems[i]