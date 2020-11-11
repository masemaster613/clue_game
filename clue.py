import random, os


class Player():
	def __init__(self, name):
		self.name=name

class Game():
	is_started = False
	right = {}
	guess = []
	winner = ''

	def start(self, players):
		people = ['Professor Plum', 'Mrs. Peacock', 'Mrs. White', 'Miss Scarlett', 'Mr. Green', 'Colonel Mustard']
		weapons = ['Candlestick', 'Dagger', 'Lead Pipe', 'Revolver', 'Rope', 'Wrench']
		rooms = ['Kitchen', 'Ballroom', 'Conservatory', 'Dining room', 'Lounge', 'Hall', 'Study', 'Library', 'Billiard Room', 'Conservatory']
		all_cards = [people, weapons, rooms]
		self.solution = []
		for i in all_cards:
			self.solution.append(i.pop(random.randint(0,len(i)-1)))
		#deal out cards
		self.hands = {}
		counter = 0
		#make a hand for each player
		for player in players:
			self.hands[player.name] = []
		deck = people + weapons + rooms
		#give them cards
		while counter < 2:
			for player in players:
				try:
					self.hands[player.name].append(deck.pop(random.randint(0,len(deck)-1)))
				except ValueError:
					counter += 1
		self.known = {}
		for player in players:
			self.known[player.name] = []
			for card in self.hands[player.name]:
				self.known[player.name].append(card)
		self.is_started = True
		self.players_turn = 0
		self.responder = 1

	def make_guess(self, guess, players):
		self.guess=guess
		for player in players:
			for item in guess:
				if item in self.hands[player.name] and player != players[self.players_turn]:
					self.right[item] = player.name
		
	def new_turn(self):
		self.right = {}
		self.guess = []
		self.players_turn += 1
		self.responder = self.players_turn + 1

# class Board():
# 	 background=os.path.join(app.root_path, 'static/images/GameboardClue.jpg')

		