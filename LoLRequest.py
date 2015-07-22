	
#- Makes calls to the Riot API.

import LoL
import LoLSql
from riotwatcher import RiotWatcher

class LoLRequest():
	
	def __init__(self):
		self.riot = RiotWatcher(LoL.API_KEY)
		self.champion_list = self.riot.static_get_champion_list()
		
	def _checkRequestStatus(self):
		return self.riot.can_make_request()
		
	def retrievePlayerData(self, playerId):
		if self._checkRequestStatus():
			player = self.riot.get_summoner(name=playerId)
			masteries = self.riot.get_mastery_pages([player['id', ])[str(player['id'])]
			current_ranked_stats = self.riot.get_ranked_stats(player['id'])
			previous_ranked_stats = self.riot.get_ranked_stats(player['id'], season=4)
			
	
	def savePlayerData(self, playerId):
		
#LoLRequest().retrievePlayerData('Avengous')