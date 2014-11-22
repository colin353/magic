from libmagic import *

deckname = "commander.json"

f = open(deckname)
deck = json.loads(f.read())
f.close()

h = Hand()

h.drawCards( deck )

f = open('deck-list.txt', 'w')

n = 1

f.write("\n--- Lands ---\n\n")
for l in h.lands():
	f.write(" %d. %s\n" % (n, l.name) )
	n += 1

f.write("\n--- Creatures ---\n\n")
for l in h.creatures():
	f.write(" %d. %s \t\t[%s]\n" % (n, l.name, l.mana_cost()) )
	n += 1

f.write("\n--- Spells ---\n\n")
for l in h.spells():
	f.write(" %d. %s \t\t[%s]\n" % (n, l.name, l.mana_cost()) )
	n += 1
