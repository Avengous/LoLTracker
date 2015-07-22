from lxml import html
import requests

class LoLScraper():
	
	
	def __init__(self, playerName):
		self.player = playerName
		
	def _crawlSite(self, url):
		page = requests.get('{}{}'.format(url, self.player))
		print page.content
		return page
	
data_sources = ['http://na.op.gg/summoner/userName=']
	
for source in data_sources:
	print LoLScraper('Avengous')._crawlSite(source)