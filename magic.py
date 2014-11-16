# Magic.py
# a program that lets you build a deck in JSON format.

import json, re, binascii


f = open('allcards.json')
card_database 	= json.loads( f.read() )
card_names		= [ k.encode('ascii','ignore').decode('ascii') for k in list(card_database.keys()) ]
f.close()

deck = []

while True:
	command = input('Card >')

	if command == 'save':
		filename = input('Name of deck: ')
		f = open("%s.json" % filename, 'w')
		f.write( json.dumps(deck) )
		f.close()
		print("OK. Deck saved to \"%s.json\"." % filename)
		continue

	number = 0
	thecard = None
	for k in card_names:
		if re.search(command, k, re.IGNORECASE):
			# Save the card to come back to it later
			thecard = k
			# Only show 10 cards
			if number < 10:
				print(" %d. %s" % (number,k))
			number += 1

	# If there are many others, let them know
	if number > 10:
		print("and %d more..." % (number - 10))	

	# If there is only one, it is selected
	if number == 1:
		command = input("Append: \"%s\"? [Y/n/#]" % thecard)
		# Allow the person to decline the card.
		if 'n' == command.lower():
			continue

		try:
			count = int(command)
		except Exception:
			count = 1

		for c in range(count):
			deck.append( card_database[thecard] )
		
		print("OK. Deck has %d cards." % len(deck))

