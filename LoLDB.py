#- This module interacts with the database.

import sqlite3
import time
import json

class Database():
	
	def __init__(self):
		self.connection = sqlite3.connect('loltracker.db')
		self.db = self.connection.cursor()
	
	def _commit(self):
		self.connection.commit()
	
	def _close(self):
		self.connection.close()
		
	def _dict_to_str(self, dict):
		value = str(dict).replace("u'",'') \
						 .replace(',','-') \
						 .replace('{', '') \
						 .replace('}', '') \
						 .replace(' ', '') \
						 .replace("'", '') \
						 .replace(':','_') \
						 .replace('[', '') \
						 .replace(']', '')
		return "'{}'".format(value)
	
	def _updateTable(self, table, keys, replace=False):
		date = str(int(time.time()))
		key_string = ['date']
		value_string = [date]
		for key in keys:
			key_string.append(key)
			if type(keys[key]) is int:
				vk = str(keys[key])
			elif type(keys[key]) is dict:
				vk = self._dict_to_str(keys[key])
			elif type(keys[key]) is list:
				vk = self._dict_to_str(keys[key])
			else:
				vk = "'{}'".format(keys[key])
			value_string.append(vk)
			
		key = ','.join(key_string)
		value = ','.join(value_string)
		
		if replace:
			self.db.execute("INSERT OR REPLACE INTO {0}({1}) VALUES({2})".format(table, key, value))
		else:
			self.db.execute("INSERT INTO {0}({1}) VALUES({2})".format(table, key, value))
		self._commit()
	
	def _execute(self, table, fields):
		cmd = "CREATE TABLE `{0}` (`tid` INTEGER NOT NULL UNIQUE,{1}, PRIMARY KEY(tid))".format(table, fields)
		self.db.execute(cmd)
	
	def _returnCompatField(self, type):
		if type in [str, unicode]:
			return 'text'
		elif type in [int, long, bool]:
			return 'int'
		elif type in [float]:
			return 'real'
		else:
			print 'Untracked Type:', type
			return None
	
	def createDatabase(self):
		player = Request().retrievePlayerData(LoL.PLAYERIDS[0])
		
		fields = []
		for item in player['summoner']:
			fields.append('{} {}'.format(item, self._returnCompatField(type(player['summoner'][item]))))
		self._execute('players', ','.join(fields))
		
		fields = []
		skip_next = False
		matchData = player['match_history']['matches'][0]
		for item in matchData:
			if type(matchData[item]) is not list:
				fields.append('{} {}'.format(item, self._returnCompatField(type(matchData[item]))))
			else:
				for subitem in matchData[item][0]:
					if type(matchData[item][0][subitem]) is not list and type(matchData[item][0][subitem]) is not dict:
						if not skip_next:
							fields.append('{} {}'.format(subitem, self._returnCompatField(type(matchData[item][0][subitem]))))
						if subitem == 'participantId':
							skip_next = True
					elif type(matchData[item][0][subitem]) is list:
						#This adds fields for runes and masteries.
						fields.append('{} {}'.format(subitem, 'text'))
					elif type(matchData[item][0][subitem]) is dict:
						#This adds fields for match stats and deltas.
						for dictitem in matchData[item][0][subitem]:
							if type(matchData[item][0][subitem][dictitem]) is not dict:
								fields.append('{} {}'.format(dictitem, self._returnCompatField(type(matchData[item][0][subitem][dictitem]))))
							elif type(matchData[item][0][subitem][dictitem]) is dict:
								for subdictitem in matchData[item][0][subitem][dictitem]:
									fields.append('{} {}'.format('{}{}'.format(dictitem,subdictitem), self._returnCompatField(type(matchData[item][0][subitem][dictitem][subdictitem]))))
		self._execute('matches', ','.join(fields))
	
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
	
	def checkIfIdentityExists(self, summonerId):
		record = self.db.execute("SELECT * FROM identities WHERE summonerId=?", (summonerId,))
		id = 0
		for row in record:
			id = row[3]
			pass
		if id == summonerId:
			return True
		else:
			return False
	
	def checkIfMatchExists(self, matchId):
		record = self.db.execute("SELECT * FROM matches WHERE matchId=?", (matchId,))
		id = 0
		for row in record:
			id = row[7]
			pass
		if id == matchId:
			return True
		else:
			return False
	
	def updateUser(self, summonerName):
		record = self.db.execute("SELECT * FROM users WHERE playerId=?", (summonerName,))
		dc = 0
		lu = 0
		pid = ''
		for row in record:
			dc = row[0]
			lu = int(time.time())
			pid = row[2]
			pass
		self.db.execute("INSERT OR REPLACE INTO users(dateCreated,lastUpdated,playerId) VALUES({0},{1},'{2}')".format(dc,lu,pid))
		self._commit()
	
	def addMatch(self, matchItems):
		matchData = {}
		for item in matchItems:
			matchData[item[0]] = item[1]
			
		#Update Identity
		identityKeys = {}
		identity = matchData['participantIdentities'][0].items()
		identityKeys['lastUpdated'] = int(time.time())
		for item in identity:
			try:
				if len(item[1]) > 1:
					for i in item[1]:
						identityKeys[i] = item[1][i]
				else:
					identityKeys[item[0]] = item[1]
			except:
				identityKeys[item[0]] = item[1]	
		if self.checkIfIdentityExists(identityKeys['summonerId']):
			self._updateTable('identities', identityKeys, replace=True)
		else:
			self._updateTable('identities', identityKeys)
		
		#Check if match has already been recorded.
		if self.checkIfMatchExists(matchData['matchId'] + identityKeys['summonerId']):
			return
		
		#Log
		print '	[ADD] {}'.format(matchData['matchId'])
		
		#Update Matches
		matchesKeys = {}
		matchesKeys['matchSummonerId'] = identityKeys['summonerId']
		matchesKeys['queueType'] = matchData['queueType']
		matchesKeys['matchVersion'] = matchData['matchVersion']
		matchesKeys['platformId'] = matchData['platformId']
		matchesKeys['season'] = matchData['season']
		matchesKeys['region'] = matchData['region']
		matchesKeys['matchId'] = matchData['matchId'] + identityKeys['summonerId']
		matchesKeys['mapId'] = matchData['mapId']
		matchesKeys['matchCreation'] = matchData['matchCreation']
		matchesKeys['matchMode'] = matchData['matchMode']
		matchesKeys['matchDuration'] = matchData['matchDuration']
		matchesKeys['matchType'] = matchData['matchType']
		self._updateTable('matches', matchesKeys)
		
		#Update Participants
		participantKeys = {}
		participantKeys['pMatchId'] = matchesKeys['matchId'] + identityKeys['summonerId']
		participant = matchData['participants'][0].items()
		for item in participant:
			try:
				if len(item[1]) > 1:
					for i in item[1]:
						participantKeys[i] = item[1][i]
				else:
					participantKeys[item[0]] = item[1]
			except:
				participantKeys[item[0]] = item[1]
		self._updateTable('participants', participantKeys)
		
		#Update User
		self.updateUser(identityKeys['summonerName'])
		
		