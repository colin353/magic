# Simulate.py
# a simulation which calculates magic deck performance.

import json, re, random
import matplotlib.pyplot as plot
from libmagic import *

deckname = "commander.json"

f = open(deckname)
deck = json.loads(f.read())
f.close()

# The card class determines the properties of the card.
class Card(object):
	def __init__(self, card_definition):
		self.card_definition = card_definition

		self.name = card_definition['name'].encode('ascii','ignore').decode('ascii')
		self.type = card_definition['type']

		if 'text' in card_definition:
			self.text = card_definition['text']
		else:
			self.text = ""

		self._mana_value 	= [ { } ]
		self._mana_cost 	= [ { } ]

		self.tapped = False
		self.marked = False

	# This function lets each class decide if they think a particular
	# card definition classifies as "theirs".
	@staticmethod
	def get_card_type(card_definition):
		valid_types = [Land, Creature, Spell]
		default_type = Card

		for t in valid_types:
			if t.is_card_type(card_definition):
				return t(card_definition)

		# Otherwise:
		print("Unable to classify card: %s " % card_definition)
		return default_type(card_definition)

	def __repr__(self):
		return "%s<%s>" % (self.__class__.__name__, self.name.encode('ascii','ignore').decode('ascii'))

	# Returns the amount of mana that the card generates. The result is a list of options
	# quantities of mana.
	def mana_value(self):
		return self._mana_value

	def mana_cost(self):
		return self._mana_cost

	def clear_marks(self):
		self.marked = False

	# This function interprets a mana cost string. For example: {R}{3} = red + 3 colourless.
	def _interpret_mana(self, mana_string):
		mana = { }
		color_codes = { 'X':'colorless', 'R': 'red', 'W': 'white', 'B': 'black', 'U':'blue', 'G':'green' }
		for letter in [ q[1:] for q in mana_string.split('}')[:-1] ]:
			# First test if the color is colorless.
			try:
				colorless = int(letter)
				if 'colorless' in mana:
					mana['colorless'] += colorless
				else:
					mana['colorless'] = colorless
				continue
			except Exception:
				pass
			
			# Now, test if it is a color code (R, W, etc.)
			if letter in color_codes:
				if color_codes[letter] in mana:
					mana[color_codes[letter]] += 1
				else: 
					mana[color_codes[letter]] = 1
			else:
				raise Exception("Unexpected mana color: %s in <%s>" % (letter,self.name))

		return mana

# The land cards are: basic lands, dual colour lands, special lands.
class Land(Card):
	@staticmethod
	def is_card_type(card_definition):
		if re.search("Land", card_definition['type']):
			return True
		else:
			return False

	def __init__(self, card_definition):
		# Super initialize
		Card.__init__(self, card_definition)

		# By default, the card won't enter tapped.
		self._enters_tapped = False

		# Figure out how much mana it is worth: first consider basic lands
		if self.name == "Mountain":
			self._mana_value = [ { 'red': 1 } ]
		elif self.name == "Plains":
			self._mana_value = [ { 'white': 1 } ]
		elif self.name == "Swamp":
			self._mana_value = [ { 'black': 1 } ]
		elif self.name == "Island":
			self._mana_value = [ { 'blue': 1 } ]
		elif self.name == "Forest":
			self._mana_value = [ { 'green': 1 } ]

		# Non-basic lands: determine if the card enters tapped
		if re.search("enters the battlefield tapped", self.text, re.IGNORECASE):
			self._enters_tapped = True

		# Non-basic lands: determine if one/several colour groups are mentioned.
		m = re.search("\{T\}: Add ((?:\{.\})+) to your mana pool.", self.text)
		if m:
			self._mana_value = [ self._interpret_mana( m.group(1) ) ]

		# Non-basic lands: determine if an either/or land is in play:
		m = re.search("\{T\}: Add ((?:\{.\})+) or ((?:\{.\})+) to your mana pool.", self.text)
		if m:
			self._mana_value = [ self._interpret_mana( m.group(1) ), self._interpret_mana( m.group(2) ) ]

	def enters_tapped(self):
		return self._enters_tapped

class Creature(Card):
	@staticmethod
	def is_card_type(card_definition):
		if re.search("Creature", card_definition['type']):
			return True
		else:
			return False

	def __init__(self, card_definition):
		# Super initialize
		Card.__init__(self, card_definition)

		# Calculate the mana cost of the creature
		self._mana_cost = self._interpret_mana( card_definition['manaCost'] )

class Spell(Card):
	@staticmethod
	def is_card_type(card_definition):
		if re.search("Sorcery", card_definition['type']):
			return True
		elif re.search("Enchantment", card_definition['type']):
			return True
		elif re.search("Artifact", card_definition['type']):
			return True
		elif re.search("Instant", card_definition['type']):
			return True
		else:
			return False

	def __init__(self, card_definition):
		# Super initialize
		Card.__init__(self, card_definition)

		# Calculate the mana cost of the creature
		self._mana_cost = self._interpret_mana( card_definition['manaCost'] )

class Hand(object):
	def __init__(self):
		self.cards = [ ] 

	def lands(self):
		_lands = []
		for c in self.cards:
			if type(c) == Land:
				_lands.append(c)
		return _lands

	def creatures(self):
		_creatures = []
		for c in self.cards:
			if type(c) == Creature:
				_creatures.append(c)
		return _creatures

	def spells(self):
		_spells = []
		for c in self.cards:
			if type(c) == Spell:
				_spells.append(c)
		return _spells

	# Removes a random land from the hand and plays it.
	def playLand(self):
		for c in self.cards:
			if type(c) == Land:
				self.cards.remove(c)
				return c
		else:
			return None

	def castableCards(self):
		_castable = []
		for c in self.cards:
			if type(c) != Land:
				_castable.append(c)
		return _castable

	def drawCards(self, card_definitions):
		for c in card_definitions:
			self.drawCard(c)

	def drawCard(self, card_definition):
		self.cards.append( Card.get_card_type( card_definition ) )

class Battlefield(object):
	def __init__(self):
		self.lands = [ ]
		self.mana_pool = { }

	def addLand(self, land_card):
		if land_card.enters_tapped():
			land_card.tapped = True
		self.lands.append( land_card )

	# Untap all lands
	def untap(self):
		for l in self.lands:
			l.tapped = False

	# This function gets the accessible lands from the table.
	def accessibleLands(self):
		workinglands = []
		for l in self.lands:
			if not l.tapped and not l.marked:
				workinglands.append(l)

		return workinglands

	# Simple lands only have one "option": no "or".
	def simpleLands(self, lands):
		simplelands = []
		for l in lands:
			# Only monocolor, single-option lands (essentially: basic lands.)
			if len(l.mana_value()) == 1:
				simplelands.append(l)

		return simplelands

	def empty_mana_pool(self):
		self.mana_pool = { }

	# Add some mana to the mana pool.
	def add_to_mana_pool(self, mana):
		for k,v in mana.items():
			if k in self.mana_pool:
				self.mana_pool[k] += v
			else:
				self.mana_pool[k] = v

	# Compares the amount of mana in the pool to the current cost
	def remaining_mana_required(self, mana_cost):
		pool_left = self.mana_pool.copy()
		remainder = { }
		# First calculate if the color costs are met
		for k in ['red', 'blue', 'black', 'green', 'white']:
			if k in mana_cost and mana_cost[k] > 0:
				if k in pool_left and mana_cost[k] <= pool_left[k]:
					pool_left[k] -= mana_cost[k]
				elif k in pool_left:
					remainder[k] = mana_cost[k] - pool_left[k]
					pool_left[k] = 0
				else:
					remainder[k] = mana_cost[k]

		colorless = 0
		# Now we'll calculate the colorless cost:
		for k in ['red', 'blue', 'black', 'green', 'white', 'colorless']:
			if k in pool_left:
				colorless += pool_left[k]

		if 'colorless' in mana_cost and colorless < mana_cost['colorless']:
			remainder['colorless'] = mana_cost['colorless'] - colorless

		return remainder

	# This function decides whether the mana requirements overlap.
	def _is_card_relevant(self, mana1, mana2):
		for k in set(mana1).intersection(mana2):
			if mana1[k] > 0 and mana2[k] > 0:
				return True
		return False

	# This function calculates the maximum number of each color you can currently
	# muster. It counts each option as a separate value.
	def spendable_mana(self):
		output = { 'red': 0, 'blue': 0, 'black': 0, 'green': 0, 'white': 0, 'colorless': 0 }
		for l in self.accessibleLands():
			for option in l.mana_value():
				for k,v in option.items():
					output[k] += v
		return output
		
	# This function determines if a particular mana can be spent.
	def canSpendMana(self, mana_cost):
		method = [ ]
		# First, let's unmark the cards.
		for l in self.lands:
			l.clear_marks()

		# And we'll clear the mana pool
		self.empty_mana_pool()

		# Now let's get all accessible lands.
		lands = self.accessibleLands()
		#print("There are %d accessible lands." % len(lands))

		# Now let's start by considering only simple lands. We'll try to pay off as much
		# color costs as possible.
		simplelands = self.simpleLands(lands)
		count = 0
		for s in simplelands:
			if self._is_card_relevant(s.mana_value()[0], self.remaining_mana_required( mana_cost )):
				# We'll mark the card, indicating "to be used", and add the mana pool
				s.marked = True
				count += 1
				self.add_to_mana_pool(s.mana_value()[0])
				method.append( s )

		#print("Used %d simple lands." % count)

		productive = True
		while productive == True:
			cards_used = 0
			# Now let's consider multi-option lands from the remaining lands,
			# but only those that have one possible option.
			for s in self.accessibleLands():
				options = 0
				thisoption = None
				for option in s.mana_value():
					if self._is_card_relevant( option, self.remaining_mana_required( mana_cost ) ):
						thisoption = option
						options += 1
				# Consider only single-option cards.
				if options == 1:
					s.marked = True
					self.add_to_mana_pool(thisoption)
					method.append(s)
					cards_used += 1

			if cards_used == 0:
				productive = False

		# Now let's consider all other multi-option lands. Because this could get
		# super complex, I'll just choose naively. To first order it'll be right, I think.
		for s in self.accessibleLands():
			options = 0
			thisoption = None
			for option in s.mana_value():
				if self._is_card_relevant( option, self.remaining_mana_required( mana_cost ) ):
					thisoption = option
					options += 1
			if options > 0:
				s.marked = True
				self.add_to_mana_pool(thisoption)
				method.append(s)

		#if len(method) > 0:
		#	print("Method: ")
		#	for k in method:
		#		print("\"%s\" (%s)" % ( k.name, k.mana_value() ))


		# Now we're out of lands. Did we pay the appropriate cost?
		if len( self.remaining_mana_required(mana_cost).keys() ) == 0:
			return True
		else:
			pass
			#print("Unable to afford mana cost. Remaining mana required: %s" % self.remaining_mana_required(mana_cost) )

# The total turns
turns = []
for i in range(10):
	turns.append( {'green': [], 'red': [], 'white': []})

firstmarath = []

for i in range(5000):
	
	# Randomly shuffle deck to generate library.
	random.shuffle(deck)

	library = deck.copy()

	b = Battlefield()
	h = Hand()

	# Draw 7 cards
	for i in range(7):
		h.drawCard( library.pop() )

	thismarath = False
	for turn in range(1,10):
		#print("Turn %d." % turn)
		b.untap()
		draw = library.pop()

		h.drawCard( draw )
		#print(" - Drew: %s " % h.cards[-1:])

		# Can play one land
		land = h.playLand()
		if land != None:
			#print(" - Played land: %s" % land)
			b.addLand( land )

		#print(" - Capable of playing: %s" % b.spendable_mana() )
		spendable = b.spendable_mana()
		turns[turn]['green'].append( spendable['green'] )
		turns[turn]['red'].append( spendable['red'] )
		turns[turn]['white'].append( spendable['white'] )

		if thismarath == False:
			if b.canSpendMana({'red':1,'green':1,'white':1}):
				firstmarath.append(turn)
				thismarath = True



plot.hist(firstmarath, bins=[1,2,3,4,5,6,7,8,9,10])
plot.title("Turn first able to play Marath (WRG)")
plot.xlabel("Turn number")
plot.ylabel("Number of occurances (out of 10000)")
plot.show()

total = len(firstmarath)
cumulative = []
now = 0
for i in range(1,10):
	for x in firstmarath:
		if x == i:
			now += 1
	cumulative.append(100 * now / total)

plot.plot(range(1,10), cumulative)
plot.title("Probability of being able to play Marath on/before turn X")
plot.xlabel("Turn number")
plot.ylabel("Probability [%]")
plot.show()