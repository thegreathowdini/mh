import requests,json,sys

def usage():
    msg = '''usage: shuffle [cookie] [level] [upgrade]
levels\t0: novice to journeyperson, 1: master to lord, 2: baron to duke, 3: grand duke and up\n'''
    print(msg)
    quit()

def no_tickets():
    print('no tickets. quitting!')
    quit()
    
def get_card(n):
	j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/events/spooky_shuffle.php',{'action':'select_card','card_id':n,'uh':hash},cookies={'HG_TOKEN':cookies}).text)
	return [d for d in j['memory_game']['cards'] if d['id']==n][0]['name'],j['memory_game']['num_tickets']
    
cache = {
    'a':'',
    'b':''
}

levels = {
    '0':'novice_journeyman',
    '1':'master_lord',
    '2':'baron_duke',
    '3':'grand_duke_plus'  
}

if len(sys.argv) > 4 or (len(sys.argv) > 2 and sys.argv[2] not in levels) or len(sys.argv) == 1: usage()

cookies = cache[sys.argv[1]] if sys.argv[1] in cache else sys.argv[1]
if len(sys.argv) > 2: level = levels[sys.argv[2]]

try: 
    j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/gettrapcomponents.php',cookies={'HG_TOKEN':cookies}).text)
    hash = j['user']['unique_hash']
except: 
    print('invalid cookie. quitting!\n')
    quit()

j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/events/spooky_shuffle.php',{'action':'show_cards','uh':hash},cookies={'HG_TOKEN':cookies}).text)

if 'memory_game' in j and not j['memory_game']['is_complete']: 
    print('game already in progress...',end='')
    if not j['memory_game']['num_tickets']: no_tickets()
    else: print(f"resuming. tickets left: {j['memory_game']['num_tickets']}")
else: 
    if len(sys.argv) < 3:
        print('level not specified. quitting!')
        quit()
    if len(sys.argv) == 4 and not j['memory_game']['num_upgrade']: 
        print('no shuffle dust for upgrade. quitting!')
        quit()
    if 'memory_game' in j and not j['memory_game']['num_tickets']: no_tickets()
    if 'memory_game' in j and [t for t in j['memory_game']['reward_tiers'] if t['type'] == level][0]['is_locked']:
        print('no access to level. quitting!')
        quit()
    try: 
        j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/events/spooky_shuffle.php',{'action':'new_game','title_range':level,'uh':hash,'is_upgraded':'true' if len(sys.argv) == 4 else None},cookies={'HG_TOKEN':cookies}).text)
        num_tickets = j['memory_game']['num_tickets']
        print(f"game started. {num_tickets} tickets left")
    except: 
        print('failed to start game. quitting!\n')
        quit()

d,next,known_match = {}, 0, None

while next <= 17:
	if known_match:
		get_card(known_match[0])
		get_card(known_match[-1])
		known_match = None
	val1,num_tickets = get_card(next)
	print(f'card {next}: {val1:35}', end='\t')
	next += 1
	if val1 in d:
		print(f'matches card {d[val1]}')
		_,num_tickets = get_card(d[val1])
	else:
		d[val1] = next-1
		val2,num_tickets = get_card(next)
		print(f'no match for first card')
		print(f'card {next}: {val2:35}', end='\t')
		if val2 == val1: print('immediate match')
		elif val2 not in d: 
			print(f'no match. {num_tickets} tickets left')
			d[val2] = next
		else: 
			known_match = [d[val2],next]
			print(f'matches card {d[val2]}')
		next += 1
		
	if not num_tickets: 
		print('out of tickets. quitting!')
		quit()
		
print(f'done! {num_tickets} tickets left\n')