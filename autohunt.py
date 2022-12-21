# login
username = ''
password = ''
cookie = ''

# params
interval = 15
randomness = 300
miss_chance = .15


########## CODE BEGINS HERE ##########
import requests,time,random,datetime,json,re,argparse,subprocess,functools
max_fail,timeout = 2,30

requests.get = functools.partial(requests.get,timeout=timeout)
requests.post = functools.partial(requests.post,timeout=timeout)

##### ARGUMENT HANDLING #####
defined_cycles = ['gnawnia','windmill','harbour','mountain','mousoleum','tree','furoma','burglar','digby','toxic','gauntlet','tribal','iceberg','zzt','city','train','fiery','garden','fort','halloween','xmas']

p = argparse.ArgumentParser()
p.add_argument('-A',action='store_true',help='aggressive mode: interval=15 mins, miss_probability=0, randomness=10')
p.add_argument('-P',action='store_true',help='paranoid mode: interval=30 mins, miss_probability=0.2, randomness=1800')
p.add_argument('-i',help='horn interval in mins (default %s)'%interval)
p.add_argument('-m',help='miss probability (default %s)'%miss_chance)
p.add_argument('-r',help='randomness interval in seconds (default %s)'%randomness)
p.add_argument('-w',help='min first wait time')
p.add_argument('-s',action='store_true',help='antibot silent mode')
p.add_argument('-b',action='store_true',help='antibot bypass mode')
p.add_argument('-R',help='antibot refresh rate (default 20)')
p.add_argument('-C',help='follow preset cycle. \'list\' for options')
p.add_argument('-ua',help='user agent string. preset options: firefox (default), chrome, edge, mac, iphone')
p.add_argument('-z',help='cycle parameters')
p.add_argument('-a',action='store_true',help='minimal mode')
args = p.parse_args()

if args.C == 'list':
    print('='*140+'\n-C option\tDescription\t\t\tRequirements\t\t\t\t\t\t\t-z options\n'+'='*140)
    d = [('gnawnia','town of gnawnia quest','None','None'),
    ('windmill','windmill quest','access to windmill','None'),
    ('harbour','pirates quest','access to harbour','None'),
    ('mountain','mountain quest','access to mountain + charm conduit','None'),
    ('mousoleum','catch mousevina','access to laboratory + shadow trap','None'),
    ('tree','catch fairy/cherry/hydra','access to great gnarled tree',[('f','aim for fairy'),('c','aim for cherry'),('h','aim for hydra')]),
    ('furoma','furoma cycle','access to furoma + tactical trap',[('integer','number of onyx stone to keep')]),
    ('burglar','catch master burglar','access to bazaar','None'),
    ('gauntlet','catch eclipse','access to gauntlet',[('s','use superbrie formula for potions')]),
    ('tribal','tribal isles quests','balack: access to balack\'s cove + forgotten trap',[('no opts','balack')]),
    ('','','dragon: access to dracano + draconic trap',[('d','dragon')]),
    ('','','horde: access to jungle + shadow trap',[('h','horde')]),
    ('','','chieftian: access to isles + physical/tactical/hydro traps',[('c','chieftians')]),
    ('digby','catch big bad burroughs','access to digby','None'),
    ('toxic','pollutinum quest','access to toxic spill + hydro trap',[('r','refine when possible'),('c','collect when possible')]),
    ('iceberg','go through iceberg','access to iceberg','None'),
    ('zzt','go through zzt','access to zzt + tactical trap',[('m','aim for mystic'),('t','aim for technic'),('d','aim for double king'),('c','aim for chess master'),('q','use checkmate cheese on queen'),('s','use superbrie formula for checkmate cheese')]),
    ('city','claw shot city quest','access to claw shot city + law trap','None'),
    ('train','train quest','ongoing train quest + law trap',[('s','smuggle items instead of submitting'),('f','don\'t spend fools gold')]),
    ('fiery','desert warpath quest','access to fiery warpath',[('g','go for gargantua at streak 8+'),('integer','streak at which to go for commander')]),
    ('garden','living garden quest','access to living garden + hydro/arcane/shadow traps','None'),
    ('fort','fort rox quest','access to fort rox + ??? traps','None'),
    ('halloween','halloween 2022','access to event location',[('r','don\'t brew root'),('b','don\'t use bonefort')]),
    ('xmas','xmas 2022','access to event location',[('g','use glazed pecan if available'),('p','don\'t use pecan'),('c','use snowball charms with xmas base'),('h','stay at hill'),('w','stay at workshop'),('f','stay at fortress')]),
    ]
    for c in d: print('{4}{0:<10}\t{1:<30}\t{2:<60}\t{3}'.format(c[0],c[1],c[2],'\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t'.join('%s: %s'%(p[0],p[1]) for p in c[3]) if c[3] != 'None' else c[3],'\n' if c[0] else ''))
    print('')
    quit()

if args.A and args.P:
    print('Incompatible options. Choose at most one of -A -P')
    quit()
if args.A: interval,miss_chance,randomness = 15,0,10
elif args.P: interval,miss_chance,randomness = 30,.2,1800

if args.a and args.C: 
    print('Cycles cannot be used with minimal mode')
    quit()

try:
    if args.i: interval = float(args.i)
    if args.m: miss_chance = float(args.m)
    if args.r: randomness = float(args.r)
    refresh_rate = int(args.R) if args.R else 20
except:
    print('imrR parameters must be numeric')
    quit()
cycle = args.C if args.C in defined_cycles else ''
args.z = args.z if args.z else ''
antibot_mode = 'silent' if args.s else 'bypass' if args.b or args.a else 'standard'

if args.ua == 'firefox' or not args.ua: useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0'
elif args.ua == 'chrome': useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.3'
elif args.ua == 'mac': useragent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15'
elif args.ua == 'iphone': useragent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Mobile/15E148 Safari/604.1'
elif args.ua == 'edge': useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36 Edge/100.0.1185.39'
else: useragent = args.ua

print('[%s] starting autohunt. %sinterval: %s, miss_prob: %s, randomness: %s, antibot: %s%s'%(datetime.datetime.now().replace(microsecond=0),'minimal mode. ' if args.a else 'cycle: %s, '%(cycle if cycle else 'none'),interval,miss_chance,randomness,antibot_mode,', refresh: %s'%refresh_rate if antibot_mode=='bypass' and not args.a else ''))

##### AUTHENTICATION #####
def login():
    global cookie,hash,cookies
    if not username or not password: 
        print('[%s] credentials not provided. aborting'%(datetime.datetime.now().replace(microsecond=0)))
        quit()
    d = {'action':'loginHitGrab','username':username,'password':password}
    r = requests.post('https://www.mousehuntgame.com/managers/ajax/users/session.php',d,headers=post_headers)
    try: 
        cookie,hash = r.cookies['HG_TOKEN'], json.loads(r.text)['user']['unique_hash']
        cookies = {'HG_TOKEN':cookie}
        print('[%s] authentication successful. session cookie: %s'%(datetime.datetime.now().replace(microsecond=0),cookie))
    except: 
        print('[%s] login failed. aborting'%(datetime.datetime.now().replace(microsecond=0)))
        quit()

try: cookie = cookie
except: cookie = ''
try: username,password = username,password
except: username,password = '',''
hash,horns,antibot_triggered,allowed_regions,lpt,sn_user_id,lrje,latency = '',0,False,[],0,'',0,0
post_headers = {'Accept': 'application/json, text/javascript, */*; q=0.01', 'Accept-Language': 'en-GB,en;q=0.5', 'Connection': 'keep-alive', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Sec-Fetch-Dest': 'empty', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-origin', 'TE': 'trailers', 'User-Agent':useragent}
get_headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8', 'Accept-Language': 'en-GB,en;q=0.5', 'Connection': 'keep-alive', 'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'none', 'Sec-Fetch-User': '1', 'TE': 'trailers', 'Upgrade-Insecure-Requests': '1', 'User-Agent':useragent}
api_headers = {'Accept': 'application/json, text/javascript, */*; q=0.01', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Origin': 'file://', 'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}
cookies = {'HG_TOKEN':cookie}

if cookie: print('[%s] logging in with cookie: %s'%(datetime.datetime.now().replace(microsecond=0),cookie))
else: login()

##### CYCLE HELPERS #####
def choose_cycle():
    if cycle == 'gnawnia': gnawnia()
    elif cycle == 'windmill': windmill()
    elif cycle == 'harbour': harbour()
    elif cycle == 'mountain': mountain()
    elif cycle == 'mousoleum': mousoleum()
    elif cycle == 'tree': tree()
    elif cycle == 'burglar': burglar()
    elif cycle == 'furoma': furoma()
    elif cycle == 'gauntlet': gauntlet()
    elif cycle == 'tribal': tribal()
    elif cycle == 'digby': digby()
    elif cycle == 'toxic': toxic()
    elif cycle == 'iceberg': iceberg()
    elif cycle == 'zzt': zzt()
    elif cycle == 'city': city()
    elif cycle == 'train': train()
    elif cycle == 'fiery': fiery()
    elif cycle == 'garden': garden()
    elif cycle == 'fort': fort()
    elif cycle == 'halloween': halloween()
    elif cycle == 'xmas': xmas()
    
def travel(dest): requests.post('https://www.mousehuntgame.com/managers/ajax/users/changeenvironment.php',{'uh':hash,'destination':dest},headers=post_headers,cookies=cookies)
def arm_bait(bait): requests.post('https://www.mousehuntgame.com/managers/ajax/users/changetrap.php',{'uh':hash,'bait':bait},headers=post_headers,cookies=cookies)
def arm_weapon(weapon): requests.post('https://www.mousehuntgame.com/managers/ajax/users/changetrap.php',{'uh':hash,'weapon':weapon},headers=post_headers,cookies=cookies)
def arm_base(base): requests.post('https://www.mousehuntgame.com/managers/ajax/users/changetrap.php',{'uh':hash,'base':base},headers=post_headers,cookies=cookies)
def arm_charm(charm): requests.post('https://www.mousehuntgame.com/managers/ajax/users/changetrap.php',{'uh':hash,'trinket':charm},headers=post_headers,cookies=cookies)
def hammer(item,quantity): requests.post('https://www.mousehuntgame.com/managers/ajax/users/usehammer.php',{'uh':hash,'item_type':item,'item_qty':quantity},headers=post_headers,cookies=cookies)
def buy(item,quantity): requests.post('https://www.mousehuntgame.com/managers/ajax/purchases/itempurchase.php',{'uh':hash,'type':item,'quantity':quantity,'buy':1},headers=post_headers,cookies=cookies)
def potion(p,i,qty=1): requests.post('https://www.mousehuntgame.com/managers/ajax/users/usepotion.php',{'potion':p,'num_potions':qty,'recipe_index':i,'uh':hash},cookies=cookies,headers=post_headers)
def get_recipes(j,p):
    r = [l for l in j['components'] if l['classification']=='potion' if l['type']==p and l['quantity']]
    if not r: return []
    s = max(r[0]['recipe_list'],key=lambda x:x['produced_item_yield'])['recipe_index']
    m = max([l for l in r[0]['recipe_list'] if l['consumed_item_name'] != 'SUPER|brie+'],key=lambda x:x['produced_item_yield'])['recipe_index']
    return s,m

def craft(d,qty=1):
    d = {'parts[%s]'%k:d[k] for k in d}
    d['craftQty'],d['uh'] = qty,hash
    requests.post('https://www.mousehuntgame.com/managers/ajax/users/crafting.php',d,cookies=cookies,headers=post_headers)

def prologue(): 
    j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/gettrapcomponents.php',cookies=cookies,headers=post_headers).text)
    
    current_location = j['user']['environment_type']
    current_base = j['user']['base_name'].lower().replace(' ','_')
    current_weapon = j['user']['weapon_name'].lower().replace(' ','_') + '_weapon'
    current_bait = j['user']['bait_name'].lower().replace(' ','_') if j['user']['bait_name'] else 0
    current_trinket = j['user']['trinket_name'].lower().replace('charm','trinket').replace(' ','_') if 'trinket_name' in j['user'] and j['user']['trinket_name'] else None
        
    baits = {l['type']: l['quantity'] for l in j['components'] if l['classification']=='bait' and 'quantity' in l.keys()}
    crafts = {l['type']:l['quantity'] for l in j['components'] if l['classification']=='crafting_item' and 'quantity' in l.keys()}
    stats = {l['type']:l['quantity'] for l in j['components'] if l['classification']=='stat' and 'quantity' in l.keys()}
    trinkets = {l['type']: l['quantity'] for l in j['components'] if l['classification']=='trinket' and 'quantity' in l.keys()}
    potions = {l['type']:l['quantity'] for l in j['components'] if l['classification']=='potion' and 'quantity' in l.keys()}
    bases = [c['type'] for c in j['components'] if c['classification']=='base']
    weapons = [c['type'] for c in j['components'] if c['classification']=='weapon']
    chests = {l['type']:l['quantity'] for l in j['components'] if l['classification']=='convertible' and 'quantity' in l.keys()}
    
    best_weapons = {}
    for k in set([c['power_type_name'] for c in j['components'] if c['classification']=='weapon']): best_weapons[k] = max([c for c in j['components'] if c['classification']=='weapon' and c['power_type_name']==k],key=lambda x:x['power'])['type']
    best_base = max([c for c in j['components'] if c['classification']=='base'],key=lambda x:x['power'] if 'power' in x else 0)['type']
    best_weapon = max([c for c in j['components'] if c['classification']=='weapon'],key=lambda x:x['power'] if 'power' in x else 0)['type']

    return current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j
        
##### CYCLES #####
def template(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_location = ''
    target_base,target_weapon,target_bait,target_trinket = '','','',''
    
    if target_location not in allowed_regions: return print('[%s] [%s] no access to LOCATION. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if current_location != target_location:
        travel(target_location)
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    
    if target_base or target_weapon or target_bait or target_trinket:
        if target_base and current_base != target_base: arm_base(target_base)
        if target_bait and current_bait != target_bait: arm_bait(target_bait)
        if target_weapon and current_weapon != target_weapon: arm_weapon(target_weapon)
        if target_trinket and target_trinket != current_trinket: arm_charm(target_trinket if target_trinket else 'disarm')
    elif loop_counter > 5: 
        print('looped too many times. quitting!')
        quit()
    else: template(loop_counter+1)
        
def gnawnia(loop_counter=0): 
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    if current_location != 'town_of_gnawnia':
        travel('town_of_gnawnia')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_bait = ''
    if j['user']['quests']['QuestTownOfGnawnia']['state'] == 'allBountiesComplete': return print('[%s] [%s] all bounties complete'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    elif j['user']['quests']['QuestTownOfGnawnia']['can_accept'] == 'active': requests.post('https://www.mousehuntgame.com/managers/ajax/environment/town_of_gnawnia.php',{'uh':hash,'action':'accept_bounty'},headers=post_headers,cookies=cookies)
    elif j['user']['quests']['QuestTownOfGnawnia']['can_claim'] == 'active': requests.post('https://www.mousehuntgame.com/managers/ajax/environment/town_of_gnawnia.php',{'uh':hash,'action':'claim_reward'},headers=post_headers,cookies=cookies)
    elif 'bait_like_type' in j['user']['quests']['QuestTownOfGnawnia']: target_bait = j['user']['quests']['QuestTownOfGnawnia']['bait_like_type']
        
    if target_bait:
        if target_bait not in baits or baits[target_bait] < 2: buy(target_bait,2)
        if current_bait != target_bait: arm_bait(target_bait)
        print('[%s] [%s] hunting %s with %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),j['user']['quests']['QuestTownOfGnawnia']['mouse_name'].lower(),target_bait.replace('_',' ')))
    elif loop_counter > 5: 
        print('looped too many times. quitting!')
        quit()
    else: gnawnia(loop_counter+1)    

def windmill():
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()    
    if 'windmill' not in allowed_regions: return print('[%s] [%s] no access to windmill. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if current_location != 'windmill':
        travel('windmill')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    num_cheese = int(j['user']['quests']['QuestWindmill']['items']['grilled_cheese']['quantity'])
    num_flour = int(j['user']['quests']['QuestWindmill']['items']['flour_stat_item']['quantity'])
    if num_cheese: 
        if current_bait != 'grilled_cheese': arm_bait('grilled_cheese')
        print('[%s] [%s] hunting with grilled cheese: %s left'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),num_cheese))
    elif num_flour >= 60: 
        buy('grilled_cheese_pack_convertible',1)
        windmill()
    else: print('[%s] [%s] getting flour: have %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),num_flour))

def harbour():
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    if 'harbour' not in allowed_regions: return print('[%s] [%s] no access to harbour. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if current_weapon != best_weapon: arm_weapon(best_weapon)
    if current_bait != 'brie_cheese':
        if 'brie_cheese' not in baits or baits['brie_cheese'] < 5: buy('brie_cheese',10)
        arm_bait('brie_cheese')
    if current_location != 'harbour':
        travel('harbour')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    if 'QuestHarbour' not in j['user']['quests']: return print('[%s] [%s] harbour quest not active. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if j['user']['quests']['QuestHarbour']['status'] == 'searchStarted' and j['user']['quests']['QuestHarbour']['can_claim_status'] == 'active':
        requests.post('https://www.mousehuntgame.com/managers/ajax/environment/harbour.php',{'action':'claimBooty','uh':hash},headers=post_headers,cookies=cookies)
    elif j['user']['quests']['QuestHarbour']['status'] == 'canBeginSearch':
        requests.post('https://www.mousehuntgame.com/managers/ajax/environment/harbour.php',{'action':'beginSearch','uh':hash},headers=post_headers,cookies=cookies)
        
def mountain(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_bait = ''    
    if 'mountain' not in allowed_regions: return print('[%s] [%s] no access to mountain. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if current_location != 'mountain':
        travel('mountain')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    
    if 'QuestMountain' not in j['user']['quests']: return print('[%s] [%s] mountain quest unavailable. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if 'power_trinket' not in trinkets or trinkets['power_trinket'] <= 5: buy('power_trinket',5)
    if current_trinket != 'power_trinket': arm_charm('power_trinket')
    
    if 'abominable_asiago_cheese' in baits: 
        target_bait = 'abominable_asiago_cheese'
        print('[%s] [%s] hunting with abominable asiago'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    elif 'faceted_sugar_crafting_item' in crafts and crafts['faceted_sugar_crafting_item'] >= 3 and 'ice_curd_crafting_item' in crafts and crafts['ice_curd_crafting_item'] >= 3: craft({'faceted_sugar_crafting_item':3,'ice_curd_crafting_item':3},qty=min(crafts['faceted_sugar_crafting_item']//3,crafts['ice_curd_crafting_item']//3))
    elif 'cheddore_cheese' in baits: 
        target_bait = 'cheddore_cheese'
        print('[%s] [%s] hunting with cheddore. faceted sugar: %s, ice curd: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),crafts['faceted_sugar_crafting_item'] if 'faceted_sugar_crafting_item' in crafts else 0,crafts['ice_curd_crafting_item'] if 'ice_curd_crafting_item' in crafts else 0))
    elif j['user']['quests']['QuestMountain']['boulder_status'] == 'can_claim': requests.post('https://www.mousehuntgame.com/managers/ajax/environment/mountain.php',{'action':'claim_reward','uh':hash},cookies=cookies,headers=post_headers)
    else:
        target_bait = 'brie_cheese'
        if target_bait not in baits or baits[target_bait] <= 10: buy(target_bait,100)
        print('[%s] [%s] hitting boulder. boulder hp: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),j['user']['quests']['QuestMountain']['boulder_hp']))
        
    if target_bait:
        if current_bait != target_bait: arm_bait(target_bait)
    elif loop_counter > 5: 
        print('looped too many times. quitting!')
        quit()
    else: mountain(loop_counter+1)

def mousoleum(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_bait,target_location,target_weapon = '','',''
    
    if 'laboratory' not in allowed_regions: return print('[%s] [%s] no access to laboratory. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if 'Shadow' not in best_weapons: return print('[%s] [%s] no shadow weapon. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if 'brie_cheese' not in baits or baits['brie_cheese'] < 70: buy('brie_cheese',66)
    
    if 'radioactive_blue_cheese' not in baits or 'mousoleum' not in allowed_regions: 
        if 'radioactive_blue_cheese_potion' in potions: potion('radioactive_blue_cheese_potion',get_recipes(j,'radioactive_blue_cheese_potion')[1])
        elif 'greater_radioactive_blue_cheese_potion' in potions: potion('greater_radioactive_blue_cheese_potion',get_recipes(j,'greater_radioactive_blue_cheese_potion')[1])
        else: 
            target_bait,target_location,target_weapon = 'brie_cheese','laboratory',best_weapons['Shadow']
            print('[%s] [%s] hunting with %s at %s: %s left'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),target_bait.replace('_',' '),target_location.replace('_',' '),baits[target_bait]))
    else:         
        if current_location != 'mousoleum':
            travel('mousoleum')
            current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
        if j['user']['quests']['QuestMousoleum']['has_wall']:
            if j['user']['quests']['QuestMousoleum']['wall_health'] <= 20 and int(j['user']['quests']['QuestMousoleum']['items']['mousoleum_wall_stat_item']['quantity']): requests.post('https://www.mousehuntgame.com/managers/ajax/environment/mousoleum.php',{'action':'repair_wall','uh':hash},cookies=cookies,headers=post_headers)
            elif 'crimson_cheese' in baits: 
                target_bait,target_location,target_weapon = 'crimson_cheese','mousoleum',best_weapons['Shadow']
                print('[%s] [%s] hunting with %s at %s. wall health: %s, slats obtained: %s, radioactive cheese left: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),target_bait.replace('_',' '),target_location.replace('_',' '),j['user']['quests']['QuestMousoleum']['wall_health'],j['user']['quests']['QuestMousoleum']['items']['mousoleum_wall_stat_item']['quantity'],baits[target_bait]))
            elif 'crimson_curd_crafting_item' in crafts and crafts['crimson_curd_crafting_item'] >= 6: craft({'crimson_curd_crafting_item':6},qty=crafts['crimson_curd_crafting_item']//6)
            else: 
                target_bait,target_weapon,target_location = 'radioactive_blue_cheese',best_weapons['Shadow'],'mousoleum'
                print('[%s] [%s] wall up, collecting crimson curds. curds: %s, wall health: %s, slats on hand: %s, radioactive cheese left: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),crafts['crimson_curd_crafting_item'] if 'crimson_curd_crafting_item' in crafts else 0,j['user']['quests']['QuestMousoleum']['wall_health'],j['user']['quests']['QuestMousoleum']['items']['mousoleum_wall_stat_item']['quantity'],baits[target_bait]))
        elif int(j['user']['quests']['QuestMousoleum']['items']['mousoleum_wall_stat_item']['quantity']) >= 30: requests.post('https://www.mousehuntgame.com/managers/ajax/environment/mousoleum.php',{'action':'build_wall','uh':hash},cookies=cookies,headers=post_headers)
        else:
            target_bait,target_weapon,target_location = 'radioactive_blue_cheese',best_weapons['Shadow'],'mousoleum'
            print('[%s] [%s] collecting slats for wall. slats obtained: %s, radioactive cheese left: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),j['user']['quests']['QuestMousoleum']['items']['mousoleum_wall_stat_item']['quantity'],baits[target_bait]))

    if target_bait:
        if current_bait != target_bait: arm_bait(target_bait)
        if current_location != target_location: travel(target_location)
        if target_weapon and current_weapon != target_weapon: arm_weapon(target_weapon)
    elif loop_counter > 5: 
        print('looped too many times. quitting!')
        quit()
    else: mousoleum(loop_counter+1)       

def tree(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_location,target_weapon,target_bait = '',best_weapons['Tactical'] if 'Tactical' in best_weapons else best_weapon  ,''
    
    if 'great_gnarled_tree' not in allowed_regions: return print('[%s] [%s] no access to tree. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if 'brie_cheese' not in baits or baits['brie_cheese'] <= 15: buy('brie_cheese',10)
    
    if 'gnarled_cheese' in baits and ('f' in args.z or ('h' in args.z and 'lagoon' not in allowed_regions)):
        target_location, target_bait = 'great_gnarled_tree','gnarled_cheese'
        print('[%s] [%s] hunting with gnarled cheese: %s left'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),baits['gnarled_cheese']))
    elif 'cherry_cheese' in baits and 'c' in args.z: 
        target_location,target_bait = 'great_gnarled_tree','cherry_cheese'
        print('[%s] [%s] hunting with cherry cheese: %s left'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),baits['cherry_cheese']))
    elif 'wicked_gnarly_cheese' in baits and 'h' in args.z and 'lagoon' in allowed_regions:
        target_location,target_bait = 'lagoon','wicked_gnarly_cheese'
        print('[%s] [%s] hunting for hydra with wicked gnarly cheese: %s left'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),baits['wicked_gnarly_cheese']))
    elif 'gnarled_cheese' in baits and 'h' in args.z: 
        target_location,target_bait = 'lagoon','gnarled_cheese'
        print('[%s] [%s] hunting for hydra with gnarled cheese: %s left'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),baits['gnarled_cheese']))
    elif 'gnarled_cheese_potion' in potions and ('f' in args.z or 'h' in args.z): potion('gnarled_cheese_potion',get_recipes(j,'gnarled_cheese_potion')[1])
    elif 'wicked_gnarly_potion' in potions and 'h' in args.z: potion('wicked_gnarly_potion',get_recipes(j,'wicked_gnarly_potion')[1])
    elif 'cherry_potion' in potions and 'c' in args.z: potion('cherry_potion',get_recipes(j,'cherry_potion')[1])
    else: 
        target_location,target_bait = 'great_gnarled_tree','brie_cheese'
        print('[%s] [%s] hunting for potions'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
        
    if target_bait:
        if target_bait and current_bait != target_bait: arm_bait(target_bait)
        if target_weapon and current_weapon != target_weapon: arm_weapon(target_weapon)
        if current_location != target_location and target_location in allowed_regions: travel(target_location)
    elif loop_counter > 5: 
        print('looped too many times. quitting!')
        quit()
    else: tree(loop_counter+1)

def furoma(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_bait = ''
    
    if 'dojo' not in allowed_regions: return print('[%s] [%s] no access to furoma. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if 'Tactical' not in best_weapons: return print('[%s] [%s] no tactical weapon. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if current_weapon != best_weapons['Tactical']: arm_weapon(best_weapons['Tactical'])
    
    keep_onyx = int(''.join([c for c in '0'+args.z if c.isdigit()]))
    
    if 'onyx_gorgonzola_cheese' in baits: target_location, target_bait = 'pinnacle_chamber', 'onyx_gorgonzola_cheese'
    elif 'onyx_stone_craft_item' in crafts and crafts['onyx_stone_craft_item'] >= keep_onyx:
        num = crafts['onyx_stone_craft_item']-keep_onyx
        if current_location != 'pinnacle_chamber': travel('pinnacle_chamber')
        buy('curds_and_whey_craft_item',60*num)
        buy('ionized_salt_craft_item',6*num)
        craft({'curds_and_whey_craft_item':60,'ionized_salt_craft_item':6,'onyx_stone_craft_item':1},num)
    elif 'rumble_cheese' in baits: target_location, target_bait = 'pinnacle_chamber', 'rumble_cheese'
    elif 'masters_seal_craft_item' in crafts:
        if current_location != 'pinnacle_chamber': travel('pinnacle_chamber')
        buy('curds_and_whey_craft_item',20*crafts['masters_seal_craft_item'])
        buy('ionized_salt_craft_item',crafts['masters_seal_craft_item'])
        craft({'curds_and_whey_craft_item':20,'ionized_salt_craft_item':1,'masters_seal_craft_item':1},crafts['masters_seal_craft_item'])
    elif 'master_claw_shard_craft_item' not in crafts:
        if 'susheese_cheese' in baits: target_location, target_bait = 'meditation_room', 'susheese_cheese'
        elif 'token_of_the_cheese_claw_craft_item' in crafts and crafts['token_of_the_cheese_claw_craft_item'] >= 3:
            num = crafts['token_of_the_cheese_claw_craft_item']//3
            if current_location != 'meditation_room': travel('meditation_room')
            buy('curds_and_whey_craft_item',num)
            buy('nori_craft_item',3*num)
            buy('burroughs_salmon_craft_item',num)
            craft({'token_of_the_cheese_claw_craft_item':3,'curds_and_whey_craft_item':3,'nori_craft_item':1,'burroughs_salmon_craft_item':1},num)
        else: 
            target_location, target_bait = 'dojo','brie_cheese'
            print('[%s] [%s] hunting for claw token at dojo: gotten %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),crafts['token_of_the_cheese_claw_craft_item'] if 'token_of_the_cheese_claw_craft_item' in crafts else 0))
    elif 'master_fang_shard_craft_item' not in crafts:
        if 'combat_cheese' in baits: target_location, target_bait = 'meditation_room', 'combat_cheese'
        elif 'token_of_the_cheese_fang_craft_item' in crafts and crafts['token_of_the_cheese_fang_craft_item'] >= 3:
            num = crafts['token_of_the_cheese_fang_craft_item']//3
            if current_location != 'meditation_room': travel('meditation_room')
            buy('curds_and_whey_craft_item',5*num)
            buy('splintered_wood_craft_item',num)
            buy('paintbrand_paint_craft_item',num) 
            craft({'token_of_the_cheese_fang_craft_item':3,'curds_and_whey_craft_item':5,'splintered_wood_craft_item':1,'paintbrand_paint_craft_item':1},num)
        else: 
            target_location, target_bait = 'dojo','brie_cheese'
            print('[%s] [%s] hunting for fang token at dojo: gotten %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),crafts['token_of_the_cheese_fang_craft_item'] if 'token_of_the_cheese_fang_craft_item' in crafts else 0))
    elif 'master_belt_shard_craft_item' not in crafts:
        if 'glutter_cheese' in baits: target_location, target_bait = 'meditation_room', 'glutter_cheese'
        elif 'token_of_the_cheese_belt_craft_item' in crafts and crafts['token_of_the_cheese_belt_craft_item'] >= 3:
            if current_location != 'meditation_room': travel('meditation_room')
            num = crafts['token_of_the_cheese_belt_craft_item']//3
            buy('curds_and_whey_craft_item',7*num)
            buy('invisiglu_craft_item',num)
            buy('cheesy_fluffs_craft_item',num)
            craft({'token_of_the_cheese_belt_craft_item':3,'curds_and_whey_craft_item':7,'invisiglu_craft_item':1,'cheesy_fluffs_craft_item':1},num)
        else: 
            target_location, target_bait = 'dojo','brie_cheese'
            print('[%s] [%s] hunting for belt token at dojo: gotten %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),crafts['token_of_the_cheese_belt_craft_item'] if 'token_of_the_cheese_belt_craft_item' in crafts else 0))
    else:
        num = min(crafts['master_belt_shard_craft_item'],crafts['master_claw_shard_craft_item'],crafts['master_fang_shard_craft_item'])
        if current_location != 'pinnacle_chamber': travel('pinnacle_chamber')
        buy('curds_and_whey_craft_item',20*num)
        buy('ionized_salt_craft_item',num)
        craft({'curds_and_whey_craft_item':20,'ionized_salt_craft_item':1,'master_claw_shard_craft_item':1,'master_belt_shard_craft_item':1,'master_fang_shard_craft_item':1},num)
                
    if target_bait:
        if target_bait and current_bait != target_bait: arm_bait(target_bait)
        if target_location and current_location != target_location: travel(target_location)
        if target_location != 'dojo': print('[%s] [%s] hunting with %s at %s: %s left'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),target_bait.replace('_',' '),target_location.replace('_',' '),baits[target_bait]))
    elif loop_counter > 5: 
        print('looped too many times. quitting!')
        quit()
    else: furoma(loop_counter+1)

def burglar(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()    
    if 'bazaar' not in allowed_regions: return print('[%s] [%s] no access to bazaar. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if 'brie_cheese' not in baits or baits['brie_cheese'] < 10: buy('brie_cheese',10)
    target_bait = 'gilded_cheese' if 'gilded_cheese' in baits else 'brie_cheese'    
    if current_weapon != best_weapon: arm_weapon(best_weapon)
    if current_location != 'bazaar': travel(target_location)
    if current_bait != target_bait: arm_bait(target_bait)
    print('[%s] [%s] hunting with %s: %s left'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),target_bait.replace('_',' '),baits[target_bait]))

def gauntlet(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_bait,target_weapon = '',''
    
    if 'kings_gauntlet' not in allowed_regions: return print('[%s] [%s] no access to gauntlet. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if current_location != 'kings_gauntlet': travel('kings_gauntlet')
            
    if 'gauntlet_cheese_8' in baits: target_bait, target_weapon = 'gauntlet_cheese_8', best_weapons['Forgotten'] if 'Forgotten' in best_weapons else best_weapon
    elif 'gauntlet_potion_8' in potions: 
        s,m = get_recipes(j,'gauntlet_potion_8')
        potion('gauntlet_potion_8',s if 's' in args.z and 'super_brie_cheese' in baits else m)
    elif 'gauntlet_cheese_7' in baits: target_bait, target_weapon = 'gauntlet_cheese_7', best_weapons['Hydro'] if 'Hydro' in best_weapons else best_weapon
    elif 'gauntlet_potion_7' in potions: 
        if 'brie_cheese' not in baits or baits['brie_cheese'] < 2: buy('brie_cheese',2)
        s,m = get_recipes(j,'gauntlet_potion_7')
        potion('gauntlet_potion_7',s if 's' in args.z and 'super_brie_cheese' in baits else m)
    elif 'gauntlet_cheese_6' in baits: target_bait, target_weapon = 'gauntlet_cheese_6', best_weapons['Arcane'] if 'Arcane' in best_weapons else best_weapon
    elif 'gauntlet_potion_6' in potions: 
        if 'brie_cheese' not in baits or baits['brie_cheese'] < 3: buy('brie_cheese',3)
        s,m = get_recipes(j,'gauntlet_potion_6')
        potion('gauntlet_potion_6',s if 's' in args.z and 'super_brie_cheese' in baits else m)
    elif 'gauntlet_cheese_5' in baits: target_bait, target_weapon = 'gauntlet_cheese_5', best_weapons['Shadow'] if 'Shadow' in best_weapons else best_weapon
    elif 'gauntlet_potion_5' in potions: 
        if 'brie_cheese' not in baits or baits['brie_cheese'] < 4: buy('brie_cheese',4)
        s,m = get_recipes(j,'gauntlet_potion_5')
        potion('gauntlet_potion_5',s if 's' in args.z and 'super_brie_cheese' in baits else m)
    elif 'gauntlet_cheese_4' in baits: target_bait, target_weapon = 'gauntlet_cheese_4', best_weapons['Tactical'] if 'Tactical' in best_weapons else best_weapon
    elif 'gauntlet_potion_4' in potions: 
        if 'brie_cheese' not in baits or baits['brie_cheese'] < 4: buy('brie_cheese',4)
        s,m = get_recipes(j,'gauntlet_potion_4')
        potion('gauntlet_potion_4',s if 's' in args.z and 'super_brie_cheese' in baits else m)
    elif 'gauntlet_cheese_3' in baits: target_bait, target_weapon = 'gauntlet_cheese_3', best_weapons['Tactical'] if 'Tactical' in best_weapons else best_weapon
    elif 'gauntlet_potion_3' in potions: 
        if 'swiss_cheese' not in baits or baits['swiss_cheese'] < 5: buy('swiss_cheese',5)
        s,m = get_recipes(j,'gauntlet_potion_3')
        potion('gauntlet_potion_3',s if 's' in args.z and 'super_brie_cheese' in baits else m)
    elif 'gauntlet_cheese_2' in baits: target_bait, target_weapon = 'gauntlet_cheese_2', best_weapons['Physical']
    elif 'gauntlet_potion_2' in potions: 
        if 'swiss_cheese' not in baits or baits['swiss_cheese'] < 4: buy('swiss',4)
        s,m = get_recipes(j,'gauntlet_potion_2')
        potion('gauntlet_potion_2',s if 's' in args.z and 'super_brie_cheese' in baits else m)
    else:
        target_bait, target_weapon = 'brie_cheese', best_weapons['Physical']
        if 'brie_cheese' not in baits: buy('brie_cheese',10)
    if target_bait:
        if target_weapon != current_weapon: arm_weapon(target_weapon)
        if target_bait != current_bait: arm_bait(target_bait)
        print('[%s] [%s] hunting at tier %s with %s. %s bait left'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),target_bait[-1] if target_bait[-1] in '8765432' else '1',target_weapon.replace('_weapon','').replace('_',' '),baits[target_bait]))
    elif loop_counter > 5: 
        print('looped too many times. quitting!')
        quit()
    else: gauntlet(loop_counter+1)

def tribal(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_weapon, target_bait, target_location, target_item = '','','',''
    
    if 'nerg_plains' not in allowed_regions: return print('[%s] [%s] no access to tribal isles. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    for type in ['Hydro','Physical','Tactical']:
        if type not in best_weapons: return print('[%s] [%s] no %s weapon. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),type.lower()))
        
    if 'dragons_chest_convertible' in chests: requests.post('https://www.mousehuntgame.com/managers/ajax/users/useconvertible.php',{'item_type':'dragons_chest_convertible','uh':hash,'item_qty':1},headers=post_headers,cookies=cookies)
    done,seeds_num = 0,0
    
    if ('c' not in args.z and 'h' not in args.z and 'd' not in args.z and 'balacks_cove' in allowed_regions and 'Forgotten' in best_weapons) and ('vengeful_vanilla_stilton_cheese' in baits or ('raisins_of_wrath' in crafts and 'pinch_of_annoyance_crafting_item' in crafts and 'bottled_up_rage_crafting_item' in crafts and 'vanilla_bean_crafting_item' in crafts) or 'vanilla_stilton_cheese' in baits or ('vanilla_bean_crafting_item' in crafts and crafts['vanilla_bean_crafting_item'] >= 15)):
        if current_location != 'balacks_cove': travel('balacks_cove')
        if json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/gettrapcomponents.php',cookies=cookies).text)['user']['quests']['QuestBalacksCove']['tide']['level'] == 'low': 
            done = 1
            if 'vengeful_vanilla_stilton_cheese' in baits: target_location, target_bait, target_weapon = 'balacks_cove','vengeful_vanilla_stilton_cheese',best_weapons['Forgotten']
            elif 'raisins_of_wrath' in crafts and 'pinch_of_annoyance_crafting_item' in crafts and 'bottled_up_rage_crafting_item' in crafts and 'vanilla_bean_crafting_item' in crafts:
                num = min(crafts['raisins_of_wrath'],crafts['pinch_of_annoyance_crafting_item'],crafts['bottled_up_rage_crafting_item'],crafts['vanilla_bean_crafting_item'])
                buy('curds_and_whey_craft_item',num)
                buy('coconut_milk_craft_item',num)
                buy('ionized_salt_craft_item',num)
                craft({'curds_and_whey_craft_item':1,'coconut_milk_craft_item':1,'ionized_salt_craft_item':1,'vanilla_bean_crafting_item':1,'raisins_of_wrath':1,'pinch_of_annoyance_crafting_item':1,'bottled_up_rage_crafting_item':1},num)
            elif 'vanilla_stilton_cheese' in baits: 
                target_bait, target_weapon, target_item = 'vanilla_stilton_cheese',best_weapons['Forgotten'],'pinch'
                print('[%s] [%s] hunting with vanilla stilton. raisins of wrath: %s, pinch of annoyance: %s, bottled-up rage: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),crafts['raisins_of_wrath'] if 'raisins_of_wrath' in crafts else 0,crafts['pinch_of_annoyance_crafting_item'] if 'pinch_of_annoyance_crafting_item' in crafts else 0,crafts['bottled_up_rage_crafting_item'] if 'bottled_up_rage_crafting_item' in crafts else 0))
            else: 
                buy('curds_and_whey_craft_item',15*crafts['vanilla_bean_crafting_item']//15)
                buy('coconut_milk_craft_item',15*crafts['vanilla_bean_crafting_item']//15)
                buy('salt_craft_item',15*crafts['vanilla_bean_crafting_item']//15)
                craft({'curds_and_whey_craft_item':15,'coconut_milk_craft_item':15,'salt_craft_item':15,'vanilla_bean_crafting_item':15},crafts['vanilla_bean_crafting_item']//15)
    if done: done = 0
    elif 'c' not in args.z and 'h' not in args.z and 'dracano' in allowed_regions and 'Draconic' in best_weapons and 'inferno_havarti_cheese' in baits: target_location, target_bait, target_weapon, target_item = 'dracano','inferno_havarti_cheese',best_weapons['Draconic'],'vanilla_bean_crafting_item'
    elif 'c' not in args.z and 'h' not in args.z and 'inferno_pepper_craft_item' in crafts and crafts['inferno_pepper_craft_item'] >= 6 and 'fire_salt_craft_item' in crafts and crafts['fire_salt_craft_item'] >= 6:
        num = min(crafts['inferno_pepper_craft_item']//6,crafts['fire_salt_craft_item']//6)
        buy('curds_and_whey_craft_item',18*num)
        buy('coconut_milk_craft_item',16*num)
        craft({'curds_and_whey_craft_item':18,'coconut_milk_craft_item':16,'fire_salt_craft_item':6,'inferno_pepper_craft_item':6},num)
    elif 'c' not in args.z and 'h' not in args.z and ('inferno_pepper_craft_item' not in crafts or crafts['inferno_pepper_craft_item'] < 6):
        if 'blue_pepper_seed_craft_item' in crafts and 'red_pepper_seed_craft_item' in crafts and 'yellow_pepper_seed_craft_item' in crafts and 'c' not in args.z:
            num = min(crafts['blue_pepper_seed_craft_item'],crafts['red_pepper_seed_craft_item'],crafts['yellow_pepper_seed_craft_item'])
            if 'plant_pot_craft_item' not in crafts: 
                if current_location not in ['dracano','derr_dunes','elub_shore','nerg_plains']: travel('dracano')
                buy('plant_pot_craft_item',num)
            craft({'blue_pepper_seed_craft_item':1,'red_pepper_seed_craft_item':1,'yellow_pepper_seed_craft_item':1,'plant_pot_craft_item':1},num)
            time.sleep(1)
            requests.post('https://www.mousehuntgame.com/managers/ajax/users/useconvertible.php',{'item_type':'white_pepper_plant_convertible','uh':hash,'item_qty':num},cookies=cookies,headers=post_headers)
        else: done,seeds_num = 1,1
    elif ('fire_salt_craft_item' not in crafts or crafts['fire_salt_craft_item'] < 6 or 'h' in args.z) and 'c' not in args.z and 'Shadow' in best_weapons and 'jungle_of_dread' in allowed_regions:
        if 'dragon_ember' in crafts and 'h' not in args.z: hammer('dragon_ember',crafts['dragon_ember'])
        for havarti in ['spicy_havarti_cheese','magical_havarti_cheese','sweet_havarti_cheese','crunchy_havarti_cheese','creamy_havarti_cheese','pungent_havarti_cheese']:
            if havarti in baits: 
                target_location, target_bait, target_weapon, target_item = 'jungle_of_dread',havarti,best_weapons['Shadow'],'fire_salt_craft_item'
                break
        else:
            for pepper in [('magical_blue_pepper_craft_item',2),('sweet_yellow_pepper_craft_item',6),('spicy_red_pepper_craft_item',12),('crunchy_green_pepper_craft_item',4),('pungent_purple_pepper_craft_item',8),('creamy_orange_pepper_craft_item',10)]:
                if pepper[0] in crafts and crafts[pepper[0]] >= 6:
                    if current_location != 'jungle_of_dread': travel('jungle_of_dread')
                    num = crafts[pepper[0]]//6
                    buy('curds_and_whey_craft_item',18*num)
                    buy('salt_craft_item',6*num)
                    buy('coconut_milk_craft_item',pepper[1]*num)
                    craft({'curds_and_whey_craft_item':18,'salt_craft_item':6,'coconut_milk_craft_item':pepper[1],pepper[0]:6},num)
                    done = 1
            if done: done = 0
            elif 'blue_pepper_seed_craft_item' in crafts and 'red_pepper_seed_craft_item' in crafts and 'yellow_pepper_seed_craft_item' in crafts and crafts['blue_pepper_seed_craft_item'] >= 4 and crafts['red_pepper_seed_craft_item'] >= 4 and crafts['yellow_pepper_seed_craft_item'] >= 4:
                print('[%s] [%s] crafting plants. wait about 15s...'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
                if current_location != 'jungle_of_dread': travel('jungle_of_dread')
                buy('plant_pot_craft_item',6)
                craft({'plant_pot_craft_item':1,'blue_pepper_seed_craft_item':2})
                time.sleep(1)
                craft({'plant_pot_craft_item':1,'red_pepper_seed_craft_item':2})
                time.sleep(1)
                craft({'plant_pot_craft_item':1,'yellow_pepper_seed_craft_item':2})
                time.sleep(1)
                craft({'plant_pot_craft_item':1,'blue_pepper_seed_craft_item':1,'red_pepper_seed_craft_item':1})
                time.sleep(1)
                craft({'plant_pot_craft_item':1,'yellow_pepper_seed_craft_item':1,'red_pepper_seed_craft_item':1})
                time.sleep(1)
                craft({'plant_pot_craft_item':1,'blue_pepper_seed_craft_item':1,'yellow_pepper_seed_craft_item':1})
                for colour in ['blue','red','yellow','green','purple','orange']:
                    time.sleep(1)
                    requests.post('https://www.mousehuntgame.com/managers/ajax/users/useconvertible.php',{'item_type':'%s_pepper_plant_convertible'%colour,'uh':hash,'item_qty':1},headers=post_headers,cookies=cookies)
            else: done,seeds_num = 1,4
    else: done = 1
    if not done: pass
    elif 'red_pepper_seed_craft_item' not in crafts or ('c' in args.z and 'yellow_pepper_seed_craft_item' in crafts and crafts['red_pepper_seed_craft_item'] < crafts['yellow_pepper_seed_craft_item'] and 'blue_pepper_seed_craft_item' in crafts and crafts['red_pepper_seed_craft_item'] < crafts['blue_pepper_seed_craft_item']) or crafts['red_pepper_seed_craft_item'] < seeds_num:
        if 'crunchy_cheese' in baits: target_location, target_bait, target_weapon = 'derr_dunes','crunchy_cheese',best_weapons['Physical']
        elif 'delicious_stone_craft_item' in crafts and crafts['delicious_stone_craft_item'] >= 30: 
            num = crafts['delicious_stone_craft_item']//30
            if current_location != 'derr_dunes': travel('derr_dunes')
            buy('curds_and_whey_craft_item',10*num)
            buy('coconut_milk_craft_item',20*num)
            buy('salt_craft_item',30*num)
            craft({'curds_and_whey_craft_item':10,'coconut_milk_craft_item':20,'salt_craft_item':30,'delicious_stone_craft_item':30},num)
        else: target_location, target_bait, target_weapon, target_item = 'derr_dunes','gouda_cheese',best_weapons['Physical'],'delicious_stone_craft_item'
    elif 'yellow_pepper_seed_craft_item' not in crafts or ('c' in args.z and 'blue_pepper_seed_craft_item' in crafts and crafts['yellow_pepper_seed_craft_item'] < crafts['blue_pepper_seed_craft_item']) or crafts['yellow_pepper_seed_craft_item'] < seeds_num:
        if 'gumbo_cheese' in baits: target_location, target_bait, target_weapon = 'nerg_plains','gumbo_cheese',best_weapons['Tactical']
        elif 'savoury_vegetables_craft_item' in crafts and crafts['savoury_vegetables_craft_item'] >= 30: 
            num = crafts['savoury_vegetables_craft_item']//30
            if current_location != 'nerg_plains': travel('nerg_plains')
            buy('curds_and_whey_craft_item',90*num)
            buy('coconut_milk_craft_item',15*num)
            buy('salt_craft_item',num)
            craft({'curds_and_whey_craft_item':90,'coconut_milk_craft_item':15,'salt_craft_item':1,'savoury_vegetables_craft_item':30},num)
        else: target_location, target_bait, target_weapon, target_item = 'nerg_plains','gouda_cheese',best_weapons['Tactical'], 'savoury_vegetables_craft_item'
    else: 
        if 'shell_cheese' in baits: target_location, target_bait, target_weapon = 'elub_shore','shell_cheese',best_weapons['Hydro']
        elif 'seashell_craft_item' in crafts and crafts['seashell_craft_item'] >= 30: 
            num = crafts['seashell_craft_item']//30
            if current_location != 'elub_shore': travel('elub_shore')
            buy('curds_and_whey_craft_item',60*num)
            buy('coconut_milk_craft_item',10*num)
            buy('salt_craft_item',40*num)
            craft({'curds_and_whey_craft_item':60,'coconut_milk_craft_item':10,'salt_craft_item':40,'seashell_craft_item':30},num)
        else: target_location, target_bait, target_weapon, target_item = 'elub_shore','gouda_cheese',best_weapons['Hydro'], 'seashell_craft_item'

    if target_weapon or target_bait or target_location:
        if target_location and current_location != target_location: travel(target_location)
        if target_bait and current_bait != target_bait: arm_bait(target_bait)
        if target_weapon and current_weapon != target_weapon: arm_weapon(target_weapon)
        if not target_item: print('[%s] [%s] hunting at %s with %s: %s %s left'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),target_location.replace('_',' '),target_weapon.replace('_',' '),baits[target_bait],target_bait.replace('_',' ')))
        elif target_item != 'pinch': print('[%s] [%s] hunting for %s, gotten %s. %s %s left'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),target_item.replace('_craft_item','').replace('_',' '),crafts[target_item] if target_item in crafts else 0,baits[target_bait],target_bait.replace('_',' ')))
    elif loop_counter > 10: 
        print('looped too many times. quitting!')
        quit()
    else: tribal(loop_counter+1)
    
def digby(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_weapon, target_location, target_bait, target_base, target_trinket = '','','','',''
    
    if 'laboratory' not in allowed_regions: return print('[%s] [%s] no access to laboratory. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if 'town_of_digby' not in allowed_regions: return print('[%s] [%s] no access to digby. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    
    if 'limelight_cheese' in baits: 
        target_location, target_bait, target_weapon, target_base, target_trinket = 'town_of_digby', 'limelight_cheese', best_weapons['Physical'], best_base,'drilling_trinket' if 'drilling_trinket' in trinkets else None
        print('[%s] [%s] hunting with limelight at digby: %s left'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),baits['limelight_cheese']))
    elif 'radioactive_sludge_craft_item' in crafts and crafts['radioactive_sludge_craft_item'] >= 3:
        num = crafts['radioactive_sludge_craft_item']//3
        if current_location != 'town_of_digby': travel('town_of_digby')
        buy('curds_and_whey_craft_item',30*num)
        buy('living_shard_crafting_item',3*num)
        craft({'curds_and_whey_craft_item':30,'living_shard_crafting_item':3,'radioactive_sludge_craft_item':3},num)
    elif 'radioactive_blue_cheese' in baits:
        target_location, target_bait, target_weapon, target_base, target_trinket = 'mountain', 'radioactive_blue_cheese', best_weapons['Physical'], 'explosive_base' if 'explosive_base' in bases else best_base, None
        print('[%s] [%s] getting sludge: have %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),crafts['radioactive_sludge_craft_item'] if 'radioactive_sludge_craft_item' in crafts else 0))
    elif 'radioactive_blue_cheese_potion' in potions: potion('radioactive_blue_cheese_potion',get_recipes(j,'radioactive_blue_cheese_potion')[1])
    elif 'greater_radioactive_blue_cheese_potion' in potions: potion('greater_radioactive_blue_cheese_potion',get_recipes(j,'greater_radioactive_blue_cheese_potion')[1])
    else: 
        target_location, target_bait, target_weapon, target_base, target_trinket = 'laboratory', 'brie_cheese', best_weapons['Physical'], best_base, None
        print('[%s] [%s] hunting for radioactive potion'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
        
    if target_location:
        if target_location != current_location: travel(target_location)
        if target_bait != current_bait: arm_bait(target_bait)
        if target_weapon != current_weapon: arm_weapon(target_weapon)
        if target_base != current_base: arm_base(target_base)
        if target_trinket != current_trinket: arm_charm(target_trinket if target_trinket else 'disarm')
    elif loop_counter > 5: 
        print('looped too many times. quitting!')
        quit()
    else: digby(loop_counter+1)

def toxic(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_weapon, target_location, target_bait, target_base, target_trinket = '','','','',''
    if 'brie_cheese' not in baits or baits['brie_cheese'] < 30: buy('brie_cheese',30)
    
    if 'pollution_outbreak' not in allowed_regions: return print('[%s] [%s] no access to toxic spill. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if 'Hydro' not in best_weapons: return print('[%s] [%s] no hydro trap. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    done,rank_diff = 0,[]
    
    if 'radioactive_sludge_craft_item' in crafts and 'radioactive_curd_crafting_item' in crafts and crafts['radioactive_curd_crafting_item'] >= 2:
        num = min(crafts['radioactive_curd_crafting_item']//2,crafts['radioactive_sludge_craft_item'])
        if 'ionized_salt_craft_item' not in crafts or crafts['ionized_salt_craft_item'] < num: 
            #if 'laboratory' != current_location: travel('laboratory')
            buy('ionized_salt_craft_item',num)
        craft({'ionized_salt_craft_item':1,'radioactive_sludge_craft_item':1,'radioactive_curd_crafting_item':2},qty=num)
    if 'super_radioactive_blue_potion' in potions and 'radioactive_blue_cheese' in baits and baits['radioactive_blue_cheese'] >= 6: potion('super_radioactive_blue_potion',get_recipes(j,'super_radioactive_blue_potion')[1],qty=min(potions['super_radioactive_blue_potion'],baits['radioactive_blue_cheese']//6))
    
    if 'super_radioactive_blue_cheese' in baits or 'magical_radioactive_blue_cheese' in baits:
        k = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/pages/page.php',{'uh':hash,'page_class':'Travel'},cookies=cookies,headers=post_headers).text)
        ranks = ['Hero','Knight','Lord/Lady','Baron/Baroness','Count/Countess','Duke/Duchess','Grand Duke/Grand Duchess','Archduke/Archduchess']
        current_rank = ranks.index(k['user']['title_name'])
        required_rank = ranks.index([p for p in [p for p in k['page']['tabs'][0]['regions'] if p['type']=='burroughs'][0]['environments'] if p['type']=='pollution_outbreak'][0]['title_name'])
        if required_rank > current_rank: rank_diff = [required_rank,current_rank]
        else:
            if current_location != 'pollution_outbreak':
                travel('pollution_outbreak')
                current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
            j = j['user']['quests']['QuestPollutionOutbreak']
            done,target_location,target_weapon,target_base = 1,'pollution_outbreak',best_weapons['Hydro'],best_base
            mp,rs,rq,rp,cp = j['max_pollutinum'],j['refine_status'],j['refine_quantity'],j['refined_pollutinum'],j['items']['crude_pollutinum_stat_item']['quantity'] if 'crude_pollutinum_stat_item' in j['items'] else 0
            
            if (rs == 'default' and (cp + rq > mp or ('r' in args.z and cp > rq))) or (rs == 'active' and (cp < rq or ('c' in args.z and cp + rq < mp))): 
                requests.post('https://www.mousehuntgame.com/managers/ajax/environment/pollution_outbreak.php',{'uh':hash,'action':'toggle_refine_mode'},headers=post_headers,cookies=cookies)
                rs = 'default' if rs == 'active' else 'active'
            
            if 'magical_radioactive_blue_cheese' in baits: target_bait = 'magical_radioactive_blue_cheese'
            else: target_bait = 'super_radioactive_blue_cheese'
            if rs == 'active': target_trinket = 'super_staling_trinket' if 'super_staling_trinket' in trinkets else 'staling_trinket' if 'staling_trinket' in trinkets else None
            else: target_trinket = 'super_soap_trinket' if 'super_soap_trinket' in trinkets else 'soap_trinket' if 'soap_trinket' in trinkets else None
            
            print('[%s] [%s] hunting at spill with %s. bait left: %s, mode: %s, crude: %s, refined: %s. '%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),'magical' if target_bait=='magical_radioactive_blue_cheese' else 'rancid',baits[target_bait],'collecting' if rs == 'default' or rs == 'disabled' else 'refining',cp, rp))
                
    if done: pass
    elif 'radioactive_sludge_craft_item' in crafts and 'radioactive_blue_cheese' in baits and baits['radioactive_blue_cheese'] >= 2: hammer('radioactive_blue_cheese',min(crafts['radioactive_sludge_craft_item'],baits['radioactive_blue_cheese']//2)*2)
    elif 'super_radioactive_blue_potion' not in potions and 'radioactive_blue_cheese' in baits:
        target_location, target_bait, target_weapon, target_base = 'mountain', 'radioactive_blue_cheese', best_weapons['Physical'], 'explosive_base'
        print('[%s] [%s] getting sludge: have %s%s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),crafts['radioactive_sludge_craft_item'] if 'radioactive_sludge_craft_item' in crafts else 0,'. required rank: %s, current rank: %s'%(rank_diff[0],rank_diff[1]) if rank_diff else ''))
    elif 'radioactive_blue_cheese_potion' in potions: potion('radioactive_blue_cheese_potion',get_recipes(j,'radioactive_blue_cheese_potion')[1])
    elif 'greater_radioactive_blue_cheese_potion' in potions: potion('greater_radioactive_blue_cheese_potion',get_recipes(j,'greater_radioactive_blue_cheese_potion')[1])
    else: 
        target_location, target_bait, target_weapon, target_base, target_trinket = 'laboratory', 'brie_cheese', best_weapons['Physical'], best_base, None
        print('[%s] [%s] hunting for radioactive potion%s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),'. required rank: %s, current rank: %s'%(rank_diff[0],rank_diff[1]) if rank_diff else ''))
        
    if target_bait:
        if target_location and target_location != current_location: travel(target_location)
        if target_bait and target_bait != current_bait: arm_bait(target_bait)
        if target_weapon and target_weapon != current_weapon: arm_weapon(target_weapon)
        if target_base and target_base != current_base: arm_base(target_base)
        if target_trinket != current_trinket: arm_charm(target_trinket if target_trinket else 'disarm')
    elif loop_counter > 5: 
        print('looped too many times. quitting!')
        quit()
    else: toxic(loop_counter+1)

def iceberg():
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    
    if 'iceberg' not in allowed_regions: return print('[%s] [%s] no access to iceberg. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    
    if current_location != 'iceberg':
        travel('iceberg')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    progress = int(j['user']['quests']['QuestIceberg']['user_progress'])
    turns = j['user']['quests']['QuestIceberg']['turns_taken']
    
    num_trinket = 0
    if 'trinket_name' in j['user'] and current_trinket in ['sticky_trinket','wax_trinket']: num_trinket = int(j['user']['trinket_quantity'])
    elif 'wax_trinket' in trinkets: 
        current_trinket,num_trinket = 'wax_trinket',trinkets['wax_trinket']
        arm_charm(current_trinket)
    elif 'sticky_trinket' in trinkets: 
        current_trinket,num_trinket = 'sticky_trinket',trinkets['sticky_trinket']
        arm_charm(current_trinket)
    
    if 'gouda_cheese' not in baits or baits['gouda_cheese'] <= 10: buy('gouda_cheese',100)
    if current_bait != 'gouda_cheese': arm_bait('gouda_cheese')
    
    good_weapons = ['steam_laser_mk_iii_weapon','steam_laser_mk_ii_weapon','steam_laser_mk_i_weapon']
    for weapon in good_weapons: 
        if weapon in weapons: 
            target_weapon = weapon
            break
    else: 
        print('[%s] [%s] no steam laser weapon. aborting!'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
        quit()
    if current_weapon != target_weapon: arm_weapon(target_weapon)
    
    if progress <= 300: segment,target_base = 'treacherous tunnels','magnet_base'
    elif progress <= 600: segment,target_base = 'brutal bulwark','spiked_base'
    elif progress <= 1600: segment,target_base = 'bombing run','remote_detonator_base'
    elif progress < 1800: segment,target_base = 'mad depths','hearthstone_base'
    elif progress == 1800: segment,target_base = 'icewing\'s lair','deep_freeze_base'
    else: segment,target_base = 'hidden depths','deep_freeze_base'
    
    target_base = 'iceberg_boiler_base' if 'iceberg_boiler_base' in bases else target_base if target_base in bases else best_base
    if target_base != current_base: arm_base(target_base)
    print('[%s] [%s] progress: %s feet (%s), hunt #%s. %s left: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),progress,segment,turns,current_trinket,num_trinket))

def zzt_parse(i): return 'not trying' if i < 0 else 'done' if i > 15 else 'got queen' if i > 14 else 'got %s rook%s'%(i-12,'s' if i-13 else '') if i > 12 else 'got %s bishop%s'%(i-10,'s' if i-11 else '') if i > 10 else 'got %s knight%s'%(i-8,'s' if i-9 else '') if i > 8 else 'got %s pawn%s'%(i,'' if i == 1 else 's')
def zzt():
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_bait, target_weapon, target_trinket, target_base = '','','',''
    
    if 'seasonal_garden' not in allowed_regions: return print('[%s] [%s] no access to zzt. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if 'Tactical' not in best_weapons: return print('[%s] [%s] no tactical trap. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    
    if current_location not in ['seasonal_garden','zugzwang_tower']:
        travel('seasonal_garden')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    amplifier, maxamp = int(j['user']['viewing_atts']['zzt_amplifier']), int(j['user']['viewing_atts']['zzt_max_amplifier'])
    if 'gouda_cheese' not in baits or baits['gouda_cheese'] <= 10: buy('gouda_cheese',100)
    
    if 'mystic_curd_crafting_item' in crafts and 'tech_cheese_mould_crafting_item' in crafts:
        if 'ionized_salt_craft_item' not in crafts or crafts['ionized_salt_craft_item'] < 12: buy('ionized_salt_craft_item',12)
        num_sb = baits['super_brie_cheese'] if 'super_brie_cheese' in baits and args.z and 's' in args.z else 0
        num_me = crafts['magic_essence_craft_item'] if 'magic_essence_craft_item' in crafts and args.z and 's' in args.z else 0
        if num_sb + num_me >= 6:
            hammer('super_brie_cheese',6-num_me)
            craft({'tech_cheese_mould_crafting_item':1,'mystic_curd_crafting_item':1,'ionized_salt_craft_item':12,'magic_essence_craft_item':6})
        else: craft({'tech_cheese_mould_crafting_item':1,'mystic_curd_crafting_item':1,'ionized_salt_craft_item':12})
        
    if amplifier == maxamp or (current_location == 'zugzwang_tower' and amplifier):
        if current_location != 'zugzwang_tower': 
            travel('zugzwang_tower')
            current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
        tech_progress, mage_progress = int(j['user']['viewing_atts']['zzt_tech_progress']), int(j['user']['viewing_atts']['zzt_mage_progress'])
        target_base = best_base if amplifier < 60 or 'wooden_base_with_target' not in bases else 'wooden_base_with_target'
        
        if args.z and 'm' in args.z and 't' not in args.z: tech_progress = -1 if mage_progress < 16 else tech_progress
        elif args.z and 't' in args.z and 'm' not in args.z: mage_progress = -1 if tech_progress < 16 else mage_progress
        if mage_progress == tech_progress:
            if random.random() >= 0.5: mage_progress -= 1
            else: tech_progress -= 1

        if (mage_progress == 16 or tech_progress == 16) and 'c' in args.z and 'checkmate_cheese' in baits: target_bait,target_weapon,target_trinket = 'checkmate_cheese',best_weapons['Tactical'],None
        elif mage_progress == 16 or tech_progress > mage_progress: 
            target_weapon = 'technic_low_weapon' if tech_progress < 8 else 'obvious_ambush_weapon' if 'obvious_ambush_weapon' in weapons else best_weapons['Tactical']
            target_trinket = 'rook_crumble_trinket' if tech_progress in [12,13] and 'rook_crumble_trinket' in trinkets else 'spellbook_trinket' if amplifier < 60 and 'spellbook_trinket' in trinkets else None
            target_bait = 'checkmate_cheese' if 'checkmate_cheese' in baits and tech_progress >= (14 if args.z and 'q' in args.z else 15) and (args.z and ('c' in args.z or 'd' in args.z)) and mage_progress != 16 else 'gouda_cheese'
        else: 
            target_weapon = 'mystic_low_weapon' if mage_progress < 8 else 'blackstone_pass_weapon' if 'blackstone_pass_weapon' in weapons else best_weapons['Tactical']
            target_trinket = 'rook_crumble_trinket' if mage_progress in [12,13] and 'rook_crumble_trinket' in trinkets else 'spellbook_trinket' if amplifier < 60 and 'spellbook_trinket' in trinkets else None
            target_bait = 'checkmate_cheese' if 'checkmate_cheese' in baits and mage_progress >= (14 if args.z and 'q' in args.z else 15) and (args.z and ('c' in args.z or 'd' in args.z)) and tech_progress != 16 else 'gouda_cheese'

        print('[%s] [%s] hunting at tower. mystic progress: %s/16 (%s), technic progress: %s/16 (%s). amplifier: %s/%s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),mage_progress,zzt_parse(mage_progress),tech_progress,zzt_parse(tech_progress),amplifier,maxamp))
    else: 
        if current_location != 'seasonal_garden': 
            travel('seasonal_garden')
            current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
        season = j['user']['viewing_atts']['season']
        
        target_base = best_base
        target_bait,target_trinket = 'gouda_cheese','amplifier_trinket' if 'amplifier_trinket' in trinkets else None
        num_trinket = trinkets[target_trinket] if target_trinket in trinkets else 0
        if season == 'sr': target_weapon = best_weapons['Tactical']
        elif season == 'sg': target_weapon = best_weapons['Physical'] if 'Physical' in best_weapons else best_weapons['Tactical']
        elif season == 'fl': target_weapon = best_weapons['Shadow'] if 'Shadow' in best_weapons else best_weapons['Tactical']
        elif season == 'wr': target_weapon = best_weapons['Hydro'] if 'Hydro' in best_weapons else best_weapons['Tactical']
        
        print('[%s] [%s] charging amplifier: %s/%s. amplifier charms: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),amplifier,maxamp,num_trinket))
    
    if current_weapon != target_weapon: arm_weapon(target_weapon)
    if current_bait != target_bait: arm_bait(target_bait)
    if current_base != target_base: arm_base(best_base)
    if current_trinket != target_trinket: arm_charm(target_trinket if target_trinket else 'disarm')

def city():
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    if 'claw_shot_city' not in allowed_regions: return print('[%s] [%s] no access to claw shot city. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if 'Law' not in best_weapons: return print('[%s] [%s] no law trap. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if current_location != 'claw_shot_city': 
        travel('claw_shot_city')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    if current_base != best_base: arm_base(best_base)
    if current_weapon != best_weapons['Law']: arm_weapon(best_weapons['Law'])
    if 'brie_cheese' not in baits or baits['brie_cheese'] < 20: buy('brie_cheese',30)
    if current_bait != 'brie_cheese': arm_bait('brie_cheese')
    if 'mining_trinket' not in trinkets or trinkets['mining_trinket'] < 10: buy('mining_trinket',10)
    target_trinket = 'sheriff_badge_trinket' if 'sheriff_badge_trinket' in trinkets and j['user']['quests']['QuestClawShotCity']['phase'] in ['need_poster','has_reward'] and 'wanted_poster_convertible' not in chests else 'cactus_trinket' if 'cactus_trinket' in trinkets else 'mining_trinket'
    if current_trinket != target_trinket: arm_charm(target_trinket)
    if j['user']['quests']['QuestClawShotCity']['phase'] == 'has_reward': 
        mapid = j['user']['quests']['QuestRelicHunter']['maps'][0]['map_id']
        requests.post('https://www.mousehuntgame.com/managers/ajax/users/treasuremap.php',{'action':'claim','uh':hash,'map_id':mapid},headers=post_headers,cookies=cookies)
    if 'wanted_poster_convertible' in chests and j['user']['quests']['QuestClawShotCity']['phase'] in ['has_poster','has_reward']: requests.post('https://www.mousehuntgame.com/managers/ajax/users/useconvertible.php',{'item_type':'wanted_poster_convertible','uh':hash,'item_qty':1},headers=post_headers,cookies=cookies)
    if 'bounty_reward_f_convertible' in chests: requests.post('https://www.mousehuntgame.com/managers/ajax/users/useconvertible.php',{'item_type':'bounty_reward_f_convertible','uh':hash,'item_qty':1},headers=post_headers,cookies=cookies)
    
def train():
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_weapon,target_trinket = best_weapons['Law'],''
    
    if 'Law' not in best_weapons: return print('[%s] [%s] no law trap. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if 'train_station' not in allowed_regions: return print('[%s] [%s] no access to train station. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if current_location != 'train_station':
        travel('train_station')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    if 'QuestTrainStation' not in j['user']['quests'] or not j['user']['quests']['QuestTrainStation']['on_train']: return print('[%s] [%s] no train quest active. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if 'brie_cheese' not in baits or baits['brie_cheese'] < 20: buy('brie_cheese',30)
    if current_bait != 'brie_cheese': arm_bait('brie_cheese')

    fg = [c['quantity'] for c in j['components'] if c['type']=='fools_gold_stat_item']
    fg = fg[0] if fg else 0
    j = j['user']['quests']['QuestTrainStation']
    phase,phase_time,target_points,current_points = j['current_phase'],j['phase_seconds_remaining'],j['team_goal'],j['score']
    
    if phase == 'supplies':
        if 'engine_doubler_weapon' in weapons: target_weapon = 'engine_doubler_weapon'
        crates = j['minigame']['supply_crates']
        if crates and 's' not in args.z: requests.post('https://www.mousehuntgame.com/managers/ajax/environment/train_station.php',{'uh':hash,'action':'load_supply_crates'},headers=post_headers,cookies=cookies)
        supply_hoarder_rounds = j['minigame']['supply_hoarder_turns']
        if supply_hoarder_rounds or ('book_warmer_trinket' not in trinkets and (current_points >= target_points or not fg or 'f' in args.z)):
            target_trinket = 'mining_trinket'
            if 'mining_trinket' not in trinkets or trinkets['mining_trinket'] < 10: buy('mining_trinket',30)    
            report = 'hoarder rounds: %s'%(supply_hoarder_rounds if supply_hoarder_rounds else 'not trying')   
        else: 
            target_trinket = 'book_warmer_trinket'
            if 'book_warmer_trinket' not in trinkets and fg: buy('book_warmer_trinket',1)
            report = 'using charm'
        report += ', crates: %s'%crates
    elif phase == 'boarding': 
        if 'bandit_deflector_weapon' in weapons: target_weapon = 'bandit_deflector_weapon'
        repellents = j['minigame']['mouse_repellent']
        if repellents and 's' not in args.z: requests.post('https://www.mousehuntgame.com/managers/ajax/environment/train_station.php',{'uh':hash,'action':'use_mouse_repellent'},headers=post_headers,cookies=cookies)
        target_trinket = 'trouble_area_%s_trinket'%j['minigame']['trouble_area']        
        report = 'area: %s '%j['minigame']['trouble_area']
        if target_trinket not in trinkets and (current_points >= target_points or not fg or 'f' in args.z):
            target_trinket = 'mining_trinket'
            if 'mining_trinket' not in trinkets or trinkets['mining_trinket'] < 10: buy('mining_trinket',30)
            report += '(no charm)'
        else: 
            if target_trinket not in trinkets and fg: buy(target_trinket,1)
            report += '(charm)'
        report += ', repellant: %s'%repellents
    elif phase == 'bridge_jump':
        if 'supply_grabber_weapon' in weapons: target_weapon = 'supply_grabber_weapon'
        coals = j['minigame']['fuel_nuggets']
        points = coals if coals < 10 else coals*2 - 10
        if 's' not in args.z and (coals >= 20 or (points >= target_points - current_points and current_points < target_points)): requests.post('https://www.mousehuntgame.com/managers/ajax/environment/train_station.php',{'uh':hash,'action':'use_fuel_nuggets'},headers=post_headers,cookies=cookies)
        for trinket in ['train_magmatic_crystal_trinket','train_black_powder_trinket','train_coal_trinket']:
            if trinket in trinkets and current_points < target_points: 
                target_trinket = trinket
                break
        else:
            if fg and 'f' not in args.z and current_points < target_points:
                target_trinket = 'train_coal_trinket'
                if target_trinket not in trinkets: buy(target_trinket,1)            
            else: 
                target_trinket = 'mining_trinket'
                if target_trinket not in trinkets or trinkets[target_trinket] < 10: buy(target_trinket,30)
        report = 'coals: %s, charm: %s'%(coals,target_trinket)
    
    print('[%s] [%s] fools gold: %s, points: %s/%s. phase: %s (%02d:%02d:%02d left), %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),fg,current_points,target_points,phase,phase_time//3600,(phase_time%3600)//60,phase_time%60,report))
    if current_weapon != target_weapon: arm_weapon(target_weapon)
    if current_base != best_base: arm_base(best_base)
    if target_trinket != current_trinket: arm_charm(target_trinket if target_trinket else 'disarm')
        
def fiery(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_weapon,target_trinket = '',''
    commander_threshold = int(''.join([c for c in '0'+args.z if c.isdigit()]))
    
    if 'desert_warpath' not in allowed_regions: return print('[%s] [%s] no access to fiery warpath. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if current_location != 'desert_warpath':
        travel('desert_warpath')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    if 'gouda_cheese' not in baits or baits['gouda_cheese'] < 20: buy('gouda_cheese',20)
    if current_bait != 'gouda_cheese': arm_bait('gouda_cheese')
    if current_base != best_base: arm_base(best_base)
    
    level = j['user']['viewing_atts']['desert_warpath']['wave']
    streak = j['user']['viewing_atts']['desert_warpath']['streak_quantity']   
    mice = {m:j['user']['viewing_atts']['desert_warpath']['mice'][m]['quantity'] for m in j['user']['viewing_atts']['desert_warpath']['mice'] if j['user']['viewing_atts']['desert_warpath']['mice'][m]['quantity']}
    
    if 'desert_horseshoe_crafting_item' in crafts and 'simple_orb_crafting_item' in crafts: 
        num = min(crafts['desert_horseshoe_crafting_item'],crafts['simple_orb_crafting_item'])
        buy('charmbit_crafting_item',2*num)
        buy('ionized_salt_craft_item',num)
        craft({'desert_horseshoe_crafting_item':1,'simple_orb_crafting_item':1,'ionized_salt_craft_item':1,'charmbit_crafting_item':2},num)
    elif 'heatproof_mage_cloth_crafting_item' in crafts and 'simple_orb_crafting_item' in crafts: 
        num = min(crafts['heatproof_mage_cloth_crafting_item'],crafts['simple_orb_crafting_item'])
        buy('charmbit_crafting_item',2*num)
        buy('ionized_salt_craft_item',num)
        craft({'heatproof_mage_cloth_crafting_item':1,'simple_orb_crafting_item':1,'ionized_salt_craft_item':1,'charmbit_crafting_item':2},num)
    
    if commander_threshold and streak >= commander_threshold: target,target_weapon,target_trinket = 'commander',best_weapon,'super_flame_march_general_trinket' if 'super_flame_march_general_trinket' in trinkets else 'flame_march_general_trinket'
    elif streak > (6 if 'g' in args.z else 9): target,target_weapon,target_trinket = 'gargantua',best_weapons['Draconic'],'gargantua_trinket'
    elif level == 1: 
        target_weapon = best_weapons['Physical']
        for m in ['desert_warrior_weak','desert_scout_weak','desert_archer_weak']:
            type = m.split('_')[1]
            if m in mice and mice[m]: target,target_trinket = m,'super_flame_march_%s_trinket'%(type) if 'super_flame_march_%s_trinket'%(type) in trinkets else 'flame_march_%s_trinket'%(type); break
    elif level == 2: 
        for m in ['desert_warrior','desert_scout','desert_archer','desert_mage','desert_cavalry']:
            type = m.split('_')[1]
            if m in mice and mice[m]: target,target_trinket,target_weapon = m,'super_flame_march_%s_trinket'%(type) if 'super_flame_march_%s_trinket'%(type) in trinkets else 'flame_march_%s_trinket'%(type),best_weapons['Tactical'] if type=='cavalry' else best_weapons['Hydro'] if type=='mage' else best_weapons['Physical']; break
    elif level == 3:
        for m in ['desert_warrior_epic','desert_scout_epic','desert_archer_epic','desert_mage_strong','desert_cavalry_strong','desert_artillery']:
            type = m.split('_')[1]
            if m in mice and mice[m]: target,target_trinket,target_weapon = m,'super_flame_march_%s_trinket'%(type) if 'super_flame_march_%s_trinket'%(type) in trinkets else 'flame_march_%s_trinket'%(type),best_weapons['Tactical'] if type=='cavalry' else best_weapons['Hydro'] if type=='mage' else best_weapons['Arcane'] if type=='artillery' else best_weapons['Physical']; break
    else: target,target_trinket,target_weapon = 'desert_elite_gaurd' if 'desert_elite_gaurd' in mice else 'desert_boss',None,best_weapons['Physical']
    
    if target_weapon:
        if target_weapon and current_weapon != target_weapon: arm_weapon(target_weapon)
        if target_trinket not in trinkets:
            if target_trinket in ['flame_march_warrior_trinket','flame_march_scout_trinket','flame_march_archer_trinket']: buy(target_trinket,10)
            else: target_trinket = None
        if target_trinket != current_trinket: arm_charm(target_trinket if target_trinket else 'disarm')
        print('[%s] [%s] level: %s, streak: %s. target: %s, quantity: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),level,streak,target,mice[target] if target in mice else '1'))
    elif loop_counter > 5: 
        print('looped too many times. quitting!')
        quit()
    else: fiery(loop_counter+1)

def fort(): pass

def garden(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_weapon, target_bait, target_location, target_trinket = '','','',''
    
    if 'desert_oasis' not in allowed_regions: return print('[%s] [%s] no access to living garden. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    for type in ['Hydro','Arcane','Shadow']:
        if type not in best_weapons: return print('[%s] [%s] no %s weapon. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),type.lower()))
    
    if current_location not in ['desert_oasis','lost_city','sand_dunes']:
        travel('desert_oasis')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    for i in ['QuestLivingGarden','QuestLostCity','QuestSandDunes']:
        if i in j['user']['quests']: normal = j['user']['quests'][i]['is_normal']; break

    if ('dewthief_petal_crafting_item' in crafts and crafts['dewthief_petal_crafting_item'] > 1) or ('duskshade_petal_crafting_item' in crafts and crafts['duskshade_petal_crafting_item'] > 1 and 'dreamfluff_herbs_crafting_item' in crafts and crafts['dreamfluff_herbs_crafting_item'] > 1) or ('graveblossom_petal_crafting_item' in crafts and crafts['graveblossom_petal_crafting_item'] > 1) or ('lunaria_petal_crafting_item' in crafts and crafts['lunaria_petal_crafting_item'] > 1 and 'plumepearl_herbs_crafting_item' in crafts and crafts['plumepearl_herbs_crafting_item'] > 1):
        if current_location not in ['desert_oasis','lost_city','sand_dunes']: travel('desert_oasis')
        if 'dewthief_petal_crafting_item' in crafts and crafts['dewthief_petal_crafting_item'] > 1: buy('dewthief_camembert_cheese',crafts['dewthief_petal_crafting_item']-1)
        if 'duskshade_petal_crafting_item' in crafts and crafts['duskshade_petal_crafting_item'] > 1 and 'dreamfluff_herbs_crafting_item' in crafts and crafts['dreamfluff_herbs_crafting_item'] > 1: buy('duskshade_camembert_cheese',min(crafts['duskshade_petal_crafting_item'],crafts['dreamfluff_herbs_crafting_item'])-1)
        if 'graveblossom_petal_crafting_item' in crafts and crafts['graveblossom_petal_crafting_item'] > 1: buy('graveblossom_camembert_cheese',crafts['graveblossom_petal_crafting_item']-1)
        if 'lunaria_petal_crafting_item' in crafts and crafts['lunaria_petal_crafting_item'] > 1 and 'plumepearl_herbs_crafting_item' in crafts and crafts['plumepearl_herbs_crafting_item'] > 1: buy('lunaria_camembert_cheese',min(crafts['lunaria_petal_crafting_item'],crafts['plumepearl_herbs_crafting_item'])-1)    
    elif not normal:
        if 'lunaria_camembert_cheese' in baits or 'graveblossom_camembert_cheese' not in baits:
            if current_location != 'desert_oasis':
                travel('desert_oasis')
                current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
                
            bucket,red_drops,yellow_drops,timer = j['user']['quests']['QuestLivingGarden']['minigame']['vials_state'],j['user']['quests']['QuestLivingGarden']['minigame']['red_drops'],j['user']['quests']['QuestLivingGarden']['minigame']['yellow_drops'],j['user']['quests']['QuestLivingGarden']['minigame']['timer']
            target_weapon, target_bait, target_trinket = best_weapons['Hydro'],'lunaria_camembert_cheese' if 'lunaria_camembert_cheese' in baits else 'duskshade_camembert_cheese' if 'duskshade_camembert_cheese' in baits else 'gouda_cheese',None
            
            if target_bait == 'lunaria_camembert_cheese': pass
            elif red_drops >= 10 and yellow_drops >= 10: requests.post('https://www.mousehuntgame.com/managers/ajax/environment/livinggarden.php',{'action':'dump_bucket','uh':hash},cookies=cookies,headers=post_headers)
            elif red_drops < 10: target_trinket = 'red_sponge_trinket'
            else: target_trinket = 'yellow_sponge_trinket'
            
            if target_trinket and target_trinket not in trinkets:
                if 'essence_b_crafting_item' in crafts: buy(target_trinket,1)
                else: target_trinket = None
                
            print(('[%s] [%s] hunting with %s at twisted %s: %s left. %s bucket: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),target_bait,current_location,baits[target_bait],bucket,'red: %s/10, yellow: %s/10, red charms: %s, yellow charms: %s'%(red_drops,yellow_drops,trinkets['red_sponge_trinket'] if 'red_sponge_trinket' in trinkets else 0,trinkets['yellow_sponge_trinket'] if 'yellow_sponge_trinket' in trinkets else 0) if bucket == 'filling' else '%s turns left'%timer)).replace('_cheese','').replace('_',' '))
            
        elif 'lunaria_petal_crafting_item' in crafts and crafts['lunaria_petal_crafting_item'] > 1:
            if current_location != 'lost_city':
                travel('lost_city')
                current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
            
            curses = [d for d in j['user']['quests']['QuestLostCity']['minigame']['curses'] if d['active']]
            target_weapon, target_bait, target_trinket = best_weapons['Arcane'],'graveblossom_camembert_cheese',None
            if curses: target_trinket = curses[0]['charm']['name'].lower().replace(' charm','_trinket')
            
            if target_trinket and target_trinket not in trinkets:
                if 'essence_b_crafting_item' in crafts: buy(target_trinket,1)
                else: target_trinket = None
            
            print(('[%s] [%s] hunting with %s at twisted %s: %s left. curses: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),target_bait,current_location,baits[target_bait],', '.join(d['type'] for d in curses) if curses else 'off')).replace('_cheese','').replace('_',' '))
            
        else:
            if current_location != 'sand_dunes':
                travel('sand_dunes')
                current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
            
            salts = j['user']['quests']['QuestSandDunes']['minigame']['salt_charms_used']
            target_weapon, target_bait, target_trinket = best_weapons['Shadow'],'graveblossom_camembert_cheese','grub_scent_trinket' if salts >= 40 else 'grub_salt_trinket'
            
            if target_trinket and target_trinket not in trinkets:
                if target_trinket == 'grub_scent_trinket' and 'essence_c_crafting_item' in crafts: buy(target_trinket,1)
                elif target_trinket == 'grub_salt_trinket' and 'essence_b_crafting_item' in crafts: buy(target_trinket,1)
                else: target_trinket = None
            
            print(('[%s] [%s] hunting with %s at twisted %s: %s left. salts: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),target_bait,current_location,baits[target_bait],salts)).replace('_cheese','').replace('_',' '))
            
    elif ('duskshade_camembert_cheese' in baits and baits['duskshade_camembert_cheese'] > 20) or 'dewthief_camembert_cheese' not in baits:
        if current_location != 'desert_oasis':
            travel('desert_oasis')
            current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
            
        bucket,drops,timer = j['user']['quests']['QuestLivingGarden']['minigame']['bucket_state'],j['user']['quests']['QuestLivingGarden']['minigame']['dewdrops'],j['user']['quests']['QuestLivingGarden']['minigame']['timer']
        target_weapon, target_bait = best_weapons['Hydro'],'duskshade_camembert_cheese' if 'duskshade_camembert_cheese' in baits and baits['duskshade_camembert_cheese'] > 20 else 'gouda_cheese'
        target_trinket = 'sponge_trinket' if bucket == 'filling' and drops < 20 and target_bait == 'gouda_cheese' else None
        
        if drops >= 20: requests.post('https://www.mousehuntgame.com/managers/ajax/environment/livinggarden.php',{'action':'dump_bucket','uh':hash},cookies=cookies,headers=post_headers)        
        if target_trinket and target_trinket not in trinkets:
            if 'essence_a_crafting_item' in crafts: buy(target_trinket,min(crafts['essence_a_crafting_item'],20-drops))
            else: target_trinket = None
            
        print(('[%s] [%s] hunting with %s at normal %s: %s left. %s bucket: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),target_bait,current_location,baits[target_bait],bucket,'%s/%s, sponge charms: %s'%(drops,20,trinkets['sponge_trinket'] if 'sponge_trinket' in trinkets else 0) if bucket == 'filling' else '%s turns left'%timer)).replace('_cheese','').replace('_',' '))
        
    elif 'duskshade_petal_crafting_item' in crafts and crafts['duskshade_petal_crafting_item'] > 1:
        if current_location != 'lost_city':
            travel('lost_city')
            current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
        curse = j['user']['quests']['QuestLostCity']['minigame']['is_cursed']
        target_weapon, target_bait, target_trinket = best_weapons['Arcane'],'dewthief_camembert_cheese', 'searcher_trinket' if curse else None
        
        if target_trinket and target_trinket not in trinkets:
            if 'essence_a_crafting_item' in crafts: buy(target_trinket,1)
            else: target_trinket = None
        
        print(('[%s] [%s] hunting with %s at normal %s: %s left. curse: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),target_bait,current_location,baits[target_bait],'on' if curse else 'off')).replace('_cheese','').replace('_',' '))
        
    else:
        if current_location != 'sand_dunes':
            travel('sand_dunes')
            current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
        
        stampede = j['user']['quests']['QuestSandDunes']['minigame']['has_stampede']
        target_weapon, target_bait, target_trinket = best_weapons['Shadow'],'dewthief_camembert_cheese','grubling_chow_trinket' if stampede else None
        if target_trinket and target_trinket not in trinkets:
            if 'essence_a_crafting_item' in crafts: buy(target_trinket,1)
            else: target_trinket = None
        
        print(('[%s] [%s] hunting with %s at normal %s: %s left. stampede: %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),target_bait,current_location,baits[target_bait],'on' if stampede else 'off')).replace('_cheese','').replace('_',' '))

    if current_base != best_base: arm_base(best_base)
    if 'gouda_cheese' not in baits or baits['gouda_cheese'] < 15: buy('gouda_cheese',15)    
    if target_weapon:
        if current_weapon != target_weapon: arm_weapon(target_weapon)
        if current_bait != target_bait: arm_bait(target_bait)
        if current_trinket != target_trinket : arm_charm(target_trinket if target_trinket else 'disarm')
    elif loop_counter > 5: 
        print('looped too many times. quitting!')
        quit()
    else: garden(loop_counter+1)

def halloween(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
        
    if 'halloween_event_location' not in allowed_regions: return print('[%s] [%s] no access to halloween location. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    if 'alchemists_cookbook_base' in bases: best_base = 'alchemists_cookbook_base'
    target_weapon = 'boiling_cauldron_weapon' if 'boiling_cauldron_weapon' in weapons else best_weapon
    target_bait,target_trinket = '',''
    if current_location != 'halloween_event_location':
        travel('halloween_event_location')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    r = j['user']['quests']['QuestHalloweenBoilingCauldron']
    if 'brie_cheese' not in baits or baits['brie_cheese'] < 15: buy('brie_cheese',15)
    
    cauldron_0_queue_len = len([c for c in r['cauldrons'][0]['queue'] if c['type']])
    cauldron_0_time = r['cauldrons'][0]['brew_time'] if r['cauldrons'][0]['brew_time'] else 0
    cauldron_1_queue_len = len([c for c in r['cauldrons'][1]['queue'] if c['type']])
    cauldron_1_time = r['cauldrons'][1]['brew_time'] if r['cauldrons'][1]['brew_time'] else 0
    caldron_priority = sorted([(0,cauldron_0_time!=0,cauldron_0_queue_len,cauldron_0_time),(1,cauldron_1_time!=0,cauldron_1_queue_len,cauldron_1_time)],key=lambda x:(x[1],x[2],x[3],x[0]))
    event_items = {k:r['items'][k]['quantity'] for k in r['items'] if 'cauldron_tier_' in k}
    brewable = ['cauldron_tier_%s_recipe'%i for i in range(1,5) for _ in range(event_items['cauldron_tier_%s_ingredient_stat_item'%i]//15)]
    num_root = r['items']['cauldron_potion_ingredient_stat_item']['quantity']
    if num_root >= 15 and 'r' not in args.z: 
        for _ in range(num_root//15): brewable = ['halloween_extract_cauldron_recipe'] + brewable
    
    if caldron_priority[0][2] <= 1 and brewable:
        d = {'uh':hash,'action':'brew_recipe','slot':caldron_priority[0][0],'recipe_type':brewable.pop()}
        requests.post('https://www.mousehuntgame.com/managers/ajax/events/halloween_boiling_cauldron.php',d,cookies=cookies,headers=post_headers)            
    if caldron_priority[1][2] <= 1 and brewable:
        d = {'uh':hash,'action':'brew_recipe','slot':caldron_priority[1][0],'recipe_type':brewable.pop()}
        requests.post('https://www.mousehuntgame.com/managers/ajax/events/halloween_boiling_cauldron.php',d,cookies=cookies,headers=post_headers)            
    
    if r['reward_track']['can_claim']:
        d = {'uh':hash,'action':'claim_reward'}
        requests.post('https://www.mousehuntgame.com/managers/ajax/events/halloween_boiling_cauldron.php',d,cookies=cookies,headers=post_headers)
    
    event_trinkets = ['spooky_trinket','extra_spooky_trinket','extreme_spooky_trinket','ultimate_spooky_trinket']
    event_trinkets = [c for c in event_trinkets if c in trinkets]
    for i in range(4,0,-1):
        if event_items['cauldron_tier_%s_cheese'%i]:
            if i == 2 and 'b' in args.z: continue
            target_bait,target_base = 'cauldron_tier_%s_cheese'%i,best_base
            if i == 3 and event_trinkets: target_trinket = event_trinkets[0]
            elif i == 4 and event_trinkets: target_trinket = event_trinkets[-1]
            else: target_trinket = ''
            break
    else: target_bait,target_base,target_trinket = 'brie_cheese',best_base,''
    
    if target_bait:
        if target_base and current_base != target_base: arm_base(target_base)
        if target_bait and current_bait != target_bait: arm_bait(target_bait)
        if target_weapon and current_weapon != target_weapon: arm_weapon(target_weapon)
        if target_trinket != current_trinket: arm_charm(target_trinket if target_trinket else 'disarm')
        level = 1 if target_bait == 'brie_cheese' else int(target_bait.split('_')[2])+1
        print('[%s] [%s] level %s, %s bait left%s. roots: %s. %s%s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),level-1,baits[target_bait],'; obtained %s x tier %s ingredient'%(event_items['cauldron_tier_%s_ingredient_stat_item'%level],level) if level <= 4 else '',num_root,'cauldron 0: time %s, queue %s. '%(cauldron_0_time,cauldron_0_queue_len) if cauldron_0_time else '','cauldron 1: time %s, queue %s. '%(cauldron_1_time,cauldron_1_queue_len) if cauldron_1_time else ''))
    elif loop_counter > 5: 
        print('looped too many times. quitting!')
        quit()
    else: halloween(loop_counter+1)
    
def xmas(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
        
    if 'winter_hunt_grove' not in allowed_regions: return print('[%s] [%s] no access to xmas location. hunting normally'%(datetime.datetime.now().replace(microsecond=0),cycle.upper()))
    
    golem = {type:(stats['golem_part_%s_stat_item'%type] if 'golem_part_%s_stat_item'%type in stats else 0) for type in ['head','torso','limb']}
    ng = min(golem['head'],golem['torso'],golem['limb']//4)
    cn = max(0,(ng+1)*4-golem['limb'])*6
    need = {'limb': bool(cn), 'head': golem['head']==ng, 'torso': golem['torso']==ng}
    cn += (12 if need['head'] else 0) + (12 if need['torso'] else 0)
    if 'QuestGolemWorkshop' in j['user']['quests']:
        for type in ['head','torso','limb']:
            if need[type]: cn -= j['user']['quests']['QuestGolemWorkshop']['workshop'][type]['progress']
            
    fl = j['user']['quests']['QuestIceFortress']['shield']['health'] if 'QuestIceFortress' in j['user']['quests'] else 36
    
    if 'h' not in args.z and 'w' not in args.z and ('f' in args.z or not fl or ('hailstone_stat_item' in stats and (stats['hailstone_stat_item'] >= fl or 'compressed_cinnamon_coal_stat_item' not in stats or cn > stats['compressed_cinnamon_coal_stat_item']))):
        if current_location != 'winter_hunt_fortress':
            travel('winter_hunt_fortress')
            current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
        if not j['user']['quests']['QuestIceFortress']['cannons']['cinnamon_cannon']['is_active'] and 'hailstone_stat_item' in stats: requests.post('https://www.mousehuntgame.com/managers/ajax/events/winter_hunt_ice_fortress.php',{'action':'toggle_cannon','uh':hash,'cannon_type':'cinnamon'},cookies=cookies,headers=post_headers)
        for type in ['snow','charm']: 
            if j['user']['quests']['QuestIceFortress']['cannons']['%s_cannon'%type]['is_active']: requests.post('https://www.mousehuntgame.com/managers/ajax/events/winter_hunt_ice_fortress.php',{'action':'toggle_cannon','uh':hash,'cannon_type':type},cookies=cookies,headers=post_headers)
        report = 'FORTRESS: hailstones: %s, cinnamons: %s/%s, fortress health: %s'%(stats['hailstone_stat_item'] if 'hailstone_stat_item' in stats else 0,stats['compressed_cinnamon_coal_stat_item'] if 'compressed_cinnamon_coal_stat_item' in stats else 0,cn,j['user']['quests']['QuestIceFortress']['shield']['health'])
    elif 'w' in args.z or ('h' not in args.z and 'compressed_cinnamon_coal_stat_item' in stats and cn <= stats['compressed_cinnamon_coal_stat_item']):
        if current_location != 'winter_hunt_workshop':
            travel('winter_hunt_workshop')
            current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
        for type in ['head','torso','limb']:
            if ('compressed_cinnamon_coal_stat_item' in stats and need[type]) != bool(j['user']['quests']['QuestGolemWorkshop']['workshop'][type]['is_active']): requests.post('https://www.mousehuntgame.com/managers/ajax/events/winter_hunt_golem_workshop.php',{'action':'toggle_maker','uh':hash,'maker_type':type},cookies=cookies,headers=post_headers)
        report = 'WORKSHOP: cinnamons: %s, %s'%(stats['compressed_cinnamon_coal_stat_item'] if 'compressed_cinnamon_coal_stat_item' in stats else 0,', '.join('%s forge: %s'%(c,j['user']['quests']['QuestGolemWorkshop']['workshop'][c]['num_hunts_remaining'] if need[c] else 'OFF') for c in ['head','torso','limb']))
    else:
        if current_location != 'winter_hunt_grove': 
            travel('winter_hunt_grove')
            current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,stats,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
        report = 'HILL: cinnamons: %s/%s, hailstones: %s/%s'%(stats['compressed_cinnamon_coal_stat_item'] if 'compressed_cinnamon_coal_stat_item' in stats else 0,cn,stats['hailstone_stat_item'] if 'hailstone_stat_item' in stats else 0,fl)
    
    for k in ['QuestGolemWorkshop','QuestIceFortress','QuestCinnamonTreeGrove']:
        if k in j['user']['quests']: 
            golem_progress = [c['hunts_remaining'] for c in j['user']['quests'][k]['golems']]
            for i in range(3):
                if j['user']['quests'][k]['golems'][i]['can_claim']: requests.post('https://www.mousehuntgame.com/managers/ajax/events/winter_hunt_region.php',{'action':'claim_reward','uh':hash,'slot':i},cookies=cookies,headers=post_headers)
            break
    
    if current_weapon != best_weapon: arm_weapon(best_weapon)
    best_base = 'seasonal_gift_of_the_day_base' if 'seasonal_gift_of_the_day_base' in bases else best_base
    if current_base != best_base: arm_base(best_base)
    
    if 'gouda_cheese' not in baits or baits['gouda_cheese'] < 15: buy('gouda_cheese',15)
    if current_location == 'winter_hunt_fortress' and fl == 0: target_bait = 'gouda_cheese'
    elif 'glazed_pecan_pecorino_cheese' in baits and 'g' in args.z: target_bait = 'glazed_pecan_pecorino_cheese'
    elif 'p' not in args.z and 'pecan_pecorino_cheese' in baits and baits['pecan_pecorino_cheese'] > 1: target_bait = 'pecan_pecorino_cheese'
    else: target_bait = 'gouda_cheese'
    if current_bait != target_bait: arm_bait(target_bait)
    
    target_trinket = ''
    if 'c' in args.z and best_base == 'seasonal_gift_of_the_day_base':
        for trinket in ['snowball_trinket','super_snowball_trinket','ultimate_snowball_trinket']:
            if trinket in trinkets: target_trinket = trinket; break
    if target_trinket != current_trinket: arm_charm(target_trinket if target_trinket else 'disarm')
    
    print('[%s] [%s] PARTS: %s. GOLEM TIME: %s. %s'%(datetime.datetime.now().replace(microsecond=0),cycle.upper(),', '.join('%s: %s'%(c,golem[c]) for c in golem),golem_progress,report))
       
       
##### HORN #####
def status_check(v=True):
    global hash,allowed_regions,antibot_triggered,lpt,sn_user_id,lrje
    if antibot_triggered or args.a:
        d = {'v':3,'client_id':'Cordova:iOS','client_version':'1.135.2','login_token':cookie}
        r = requests.post('https://www.mousehuntgame.com/api/action/passiveturn',d,headers=api_headers)
        if r.status_code != 200:
            print('[%s] session expired. logging in again'%(datetime.datetime.now().replace(microsecond=0)))
            login()
            d = {'v':3,'client_id':'Cordova:iOS','client_version':'1.135.2','login_token':cookie}
            r = requests.post('https://www.mousehuntgame.com/api/action/passiveturn',d,headers=api_headers)
        j = json.loads(r.text)
        hash,sn_user_id,lpt,next_horn,have_bait,gold,points = j['user']['uh'],j['user']['sn_user_id'],j['user']['last_passiveturn_timestamp'],j['user']['next_activeturn_seconds'],j['user']['trap']['bait_id'],j['user']['gold'],j['user']['points']
        if not horns%refresh_rate: antibot_triggered = 'The King has sent you a special reward' in requests.get('https://www.mousehuntgame.com/camp.php',cookies=cookies,headers=get_headers).text
    else: 
        r = requests.get('https://www.mousehuntgame.com/camp.php',cookies=cookies)
        if r.url == 'https://www.mousehuntgame.com/login.php':
            print('[%s] session expired. logging in again'%(datetime.datetime.now().replace(microsecond=0)))
            login()
            r = requests.get('https://www.mousehuntgame.com/camp.php',cookies=cookies).text
        r = r.text
        hash,sn_user_id,lrje,next_horn,have_bait,gold,points = re.findall('"unique_hash":"([^"]*)"',r)[0],re.findall('"sn_user_id":"([^"]*)"',r)[0],re.findall('lastReadJournalEntryId = ([^;]*);',r)[0],int(re.findall('"next_activeturn_seconds":(\d*)',r)[0]),'"bait_quantity":0' not in r,re.findall('"gold":([^,]*)',r)[0],re.findall('"points":([^,]*)',r)[0]
        if 'The King has sent you a special reward' in r: 
            if not antibot_mode == 'bypass': antibot(r)
            else:
                antibot_triggered = True
                return status_check()
    if not horns and not args.a: allowed_regions = regions()
    if not have_bait and not args.a: change_bait()
    if v: print('[%s] current gold: %s, current points: %s; horns so far: %s%s, last horn latency: %s'%(datetime.datetime.now().replace(microsecond=0),gold,points,horns,', antibot: %s'%('ACTIVE' if antibot_triggered else 'inactive') if antibot_mode == 'bypass' else '',latency))
    return next_horn

def wait(delay_mins,norandom=False):
    next_wait = delay_mins*60 + random.random()*randomness
    if norandom: next_wait = delay_mins*60
    m,s,ms = int(next_wait//60),int(next_wait%60),int((next_wait*1000)%1000)
    n = ('%s'%(datetime.datetime.now().replace(microsecond=0)+datetime.timedelta(minutes=m,seconds=s))).split(' ')[1]
    print('[%s] next horn in %s mins %s secs at %s'%(datetime.datetime.now().replace(microsecond=0),m,s,n))
    time.sleep(next_wait)
    
def print_entry(t):
    try: 
        for m in re.findall('<[^>]*>',t): t = t.replace(m,'')
        s = t.index('!',20) if '!' in t[20:-2] else t.index('.',(t.index('oz.')+3) if 'oz.' in t else 0)
        if t[:s+1]: print('[%s] %s'%(datetime.datetime.now().replace(microsecond=0),t[:s+1].lstrip()))
        if t[s+1:]: print_entry(t[s+1:])
    except: print('[%s] %s'%(datetime.datetime.now().replace(microsecond=0),t.lstrip()))    

def horn():
    global latency
    fail = 0
    try: lpt = lpt
    except: lpt = int(time.time()) - 15*60
    while 1:
        if not args.a: 
            wait_time = status_check()
            while wait_time: 
                print('[%s] horn not ready'%(datetime.datetime.now().replace(microsecond=0)))
                wait(float((wait_time+2)/60),norandom=True)
                wait_time = status_check()
            horn_time = int(time.time())
            if cycle: choose_cycle()
        latency_start = time.time()
        if antibot_triggered or args.a:
            d = {'v':3,'client_id':'Cordova:iOS','client_version':'1.135.2','last_passiveturn_timestamp':lpt,'login_token':cookie}
            j = json.loads(requests.post('https://www.mousehuntgame.com/api/action/turn/me',d,headers=api_headers).text)
            success,wait_time = j['success'],j['user']['next_activeturn_seconds']
        else:
            d = {"uh":hash,"last_read_journal_entry_id":lrje,"hg_is_ajax":1,"sn":"Hitgrab"}
            j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/turns/activeturn.php',d,cookies=cookies,headers=post_headers).text)
            success,wait_time = j['success'],j['user']['next_activeturn_seconds']
        if success:
            latency = round(time.time()-latency_start,3)
            if args.a: print('[%s] horn success (latency %s). horns so far: %s'%(datetime.datetime.now().replace(microsecond=0),latency,horns+1))
            elif antibot_triggered:
                d = {'v':3,'client_id':'Cordova:iOS','client_version':'1.135.2','offset':0,'limit':72,'return_user':'true','login_token':cookie}        
                r = json.loads(requests.post('https://www.mousehuntgame.com/api/get/journalentries/me',d,headers=api_headers).text)
                for entry in r['entries']:
                    if entry['timestamp'] < horn_time: break
                    print_entry(entry['text'])
            else:
                for entry in j['journal_markup']:
                    if entry['render_data']['entry_timestamp'] < horn_time-2: break
                    print_entry(entry['render_data']['text'])
            return 1
        else:
            fail += 1
            if fail >= max_fail:
                print('[%s] %s consecutive horn failures. aborting'%(datetime.datetime.now().replace(microsecond=0),fail))
                quit()
            if wait_time: 
                print('[%s] horn not ready'%(datetime.datetime.now().replace(microsecond=0)))
                wait(float((wait_time+2)/60),norandom=True)
            else: 
                print('[%s] failed to sound the horn. trying again in 3 secs...'%(datetime.datetime.now().replace(microsecond=0)))
                time.sleep(3)

def change_bait():
    print('[%s] out of bait. checking availability...'%(datetime.datetime.now().replace(microsecond=0)))
    r = requests.post('https://www.mousehuntgame.com/managers/ajax/users/gettrapcomponents.php',cookies=cookies,headers=post_headers)
    j = json.loads(r.text)['components']
    d = {l['type']:l['quantity'] for l in j if l['classification']=='bait' and 'quantity' in l.keys()}
    if not d:
        print('[%s] no bait in inventory. aborting'%(datetime.datetime.now().replace(microsecond=0)))
        quit()
    t = max(d.keys(),key=lambda x:d[x])
    arm_bait(t)
    print('[%s] armed %s'%(datetime.datetime.now().replace(microsecond=0),t.replace('_',' ')))
    
def regions():
    j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/pages/page.php',{'uh':hash,'page_class':'Travel'},cookies=cookies).text)
    return [s['type'] for r in j['page']['tabs'][0]['regions'] for s in r['environments'] if s['description'] != "You haven't unlocked this environment yet!"]

def antibot(text):
    print('[%s] antibot triggered'%(datetime.datetime.now().replace(microsecond=0)))
    while 1:
        url = re.findall('<img src="([^"]*)" alt="King\'s Reward">',text)[0]
        with open('kingsreward.png','wb') as f: f.write(requests.get(url).content)
        if antibot_mode != 'silent': subprocess.run(['kingsreward.png'],shell=True,stderr=subprocess.DEVNULL)
        while 1:
            v = input('[%s] enter captcha value, type \'url\' to see image url, or press ENTER to view image...'%(datetime.datetime.now().replace(microsecond=0)))
            if v.lower() == 'url': print('[%s] %s'%(datetime.datetime.now().replace(microsecond=0),url))
            elif v == '': 
                subprocess.run(['kingsreward.png'],shell=True,stderr=subprocess.DEVNULL)
                print("\033[F",end='')
            elif len(v)==5 and v.isalnum(): break
            else: print('[%s] captcha code must be 5 alphanumeric characters'%(datetime.datetime.now().replace(microsecond=0)))
        text = requests.get('https://www.mousehuntgame.com/camp.php',cookies=cookies,headers=get_headers).text
        if 'The King has sent you a special reward' not in text: return print('[%s] already solved'%(datetime.datetime.now().replace(microsecond=0)))
        subprocess.run(['del','kingsreward.png'],shell=True,stderr=subprocess.DEVNULL)
        d = {'puzzle_answer':v,'uh':hash}
        r = requests.post('https://www.mousehuntgame.com/managers/ajax/users/solvePuzzle.php',d,cookies=cookies,headers=post_headers)
        if 'Reward claimed!' in r.text: return print('[%s] code correct'%(datetime.datetime.now().replace(microsecond=0)))
        elif 'Incorrect claim code, please try again' in r.text: print('[%s] incorrect code. code is now different'%(datetime.datetime.now().replace(microsecond=0)))
        else: print('[%s] something went wrong. check if code might have changed'%(datetime.datetime.now().replace(microsecond=0)))
        text = requests.get('https://www.mousehuntgame.com/camp.php',cookies=cookies).text

initial_wait = 0 if args.a else status_check(False)
if initial_wait > 60: choose_cycle()
wait(max(float((initial_wait+1)/60),float(args.w if args.w else 0)),norandom=True)
while 1:
    if random.random() >= miss_chance or horns==0: 
        horns += horn()
        wait(interval)
    else: 
        print('[%s] giving this one a miss'%(datetime.datetime.now().replace(microsecond=0)))
        wait(random.random()*interval)
        
