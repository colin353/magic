# Simulate.py
# a simulation which calculates magic deck performance.

import json, re, random
import matplotlib.pyplot as plot
from libmagic import *

deckname = "commander.json"

f = open(deckname)
deck = json.loads(f.read())
f.close()

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