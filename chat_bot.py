#create the scoresheet
people = ['Professor Plum', 'Mrs. Peacock', 'Mrs. White', 'Miss Scarlett', 'Mr. Green', 'Colonel Mustard']
weapons = ['Candlestick', 'Dagger', 'Lead Pipe', 'Revolver', 'Rope', 'Wrench']
rooms = ['Kitchen', 'Ballroom', 'Conservatory', 'Dining room', 'Lounge', 'Hall', 'Study', 'Library', 'Billiard Room', 'Conservatory']
items = people + weapons + rooms
score = {}
for item in items:
	score[item] = 'O'
scoresheet = []
for item in score:
	scoresheet.append(item + " "*(20-len(item)) + score[item])

#define isnumber
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False


class ChatBot():
	scoresheet=scoresheet[:]

	def check_off(self, item):
		index=self.scoresheet.index(item)
		return self.scoresheet[index][:-1]+'X'

	def has_scoresheet(self):
		try:
			if self.scoresheet:
				return True
		except:
			return False

	def respond(self, message):
		if message.lower() == 'hi':
			return 'Hi back'
		elif message.lower() == 'hello':
			return 'Hello'
		elif 'please' in message.lower():
			return "that's a nice question"
		# elif message.lower() == 'scoresheet':
		# 	self.scoresheet = scoresheet[:]
		# 	return 'scoresheet made'
		elif is_number(message):
			self.scoresheet[int(message)-1] = self.check_off(self.scoresheet[int(message)-1])
			return 'Checked off'
		else:
			return False