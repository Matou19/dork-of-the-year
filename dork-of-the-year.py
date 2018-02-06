import urllib2
import json

class Player():
	def __init__(self, id, name, points, gamesPlayed, rank):
		self.id = id
		self.name = name
		self.points = points
		self.gamesPlayed = gamesPlayed
		self.rank = rank

	#Add in math for new game
	def addGame(self, points, gamesPlayed, rank):
		self.points += points
		self.gamesPlayed += gamesPlayed
		self.rank += rank

	def display(self):
		if self.gamesPlayed > 0:
			print(str(self.rank) + '. ' + self.name + ' - GP ' + str(self.gamesPlayed) + ' - Raw Average: ' + str(float(self.points)/self.gamesPlayed))
		else:
			# Player who played no games in time span
			# Should not hit, just for testing
			print(str(self.rank) + '. ' + self.name + ' - GP 0 - Raw Average: 0')

baseUrl = 'http://dork-prod.herokuapp.com/players/ranked?month={0}&year={1}'
year = 2017

# Global Arrays for Logic
players = []
playerIds = []
worstRankOfMonth = []

for month in range(0, 11):
	webUrl = urllib2.urlopen(baseUrl.format(month, year))
	rank = 0
	playerWithBestRating = ''
	loopedAround = False
	playersProcessedForMonth = []

	if (webUrl.getcode() == 200):
		data = json.loads(webUrl.read())
		for record in data:
			player = record['player']
			pId = player['_id']
			name = player['firstName'] + ' ' + player['lastName']
			points = record['totalPoints']
			gamesPlayed = record['gamesPlayed']
			rating = record['rating']

			# Respect Branding Rule
			if (gamesPlayed >= 10):
				rank += 1
			# Respect Branding Rule
			if (gamesPlayed >= 10) or loopedAround:
				# If Player Found
				if pId in playerIds:
					index = playerIds.index(pId)
					# If Not 10 Games Penalize
					if loopedAround:
						players[index].addGame(points, gamesPlayed, rank + 1)
					else:
						players[index].addGame(points, gamesPlayed, rank)
				else:
					# If Not 10 Games Penalize
					if loopedAround:
						localPlayer = Player(pId, name, points, gamesPlayed, rank + 1)
					else:
						localPlayer = Player(pId, name, points, gamesPlayed, rank)
					# Backfill data for Missing Months with Penalization
					for localMonth in range(0, month):
						localPlayer.addGame(0, 0, worstRankOfMonth[localMonth] + 1)
					players.append(localPlayer)
					playerIds.append(pId)
				# Player Processed
				playersProcessedForMonth.append(pId)
			else:
				# Use Player for Index for Backfill
				if playerWithBestRating == '':
					playerWithBestRating = pId
				# Player previously hit
				elif playerWithBestRating == pId:
					loopedAround = True
				# Add Player to stack for processing
				data.append(record)

		# Save Data for Future Backfilling
		worstRankOfMonth.append(rank)

		# Players Who Missed a Month Need Data for month
		for player in players:
			if player.id not in playersProcessedForMonth:
				player.addGame(0, 0, worstRankOfMonth[month] + 1)

	else:
		print('Could not get data.')

# Sort Players Before Displaying Results
players = sorted(players, key=lambda player: (player.rank, player.points))

# Display Results
for player in players:
	player.display()