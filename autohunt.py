# login
username = ''
password = ''
cookie = ''

# params
interval = 15
randomness = 300
miss_chance = .15


########## CODE BEGINS HERE ##########
import requests,time,random,datetime,json,re,argparse,os
max_fail = 2

##### ARGUMENT HANDLING #####
defined_cycles = ['gnawnia','windmill','harbour','mountain','mousoleum','tree','furoma','burglar','digby','toxic','gauntlet','tribal','iceberg','zzt','halloween']

p = argparse.ArgumentParser()
p.add_argument('-A',action='store_true',help='aggressive mode: interval=15 mins, miss_probability=0, randomness=10')
p.add_argument('-P',action='store_true',help='paranoid mode: interval=30 mins, miss_probability=0.2, randomness=1800')
p.add_argument('-i',help='horn interval in mins')
p.add_argument('-m',help='miss probability')
p.add_argument('-r',help='randomness interval in seconds')
p.add_argument('-w',help='min first wait time')
p.add_argument('-s',action='store_true',help='silent mode. don\'t open captcha image automatically')
p.add_argument('-O',help='delay in secs for out-of-band antibot solving')
p.add_argument('-ua',help='user agent string. preset options: firefox (default), chrome, edge, mac, iphone')
p.add_argument('-C',help='follow preset cycle. options: %s'%(', '.join(defined_cycles)))
p.add_argument('-z',help='cycle parameters')
p.add_argument('-L',help='log file')
args = p.parse_args()

if args.A and args.P:
    print('Incompatible options. Choose at most one of -A -P')
    quit()
if args.A: interval,miss_chance,randomness = 15,0,10
elif args.P: interval,miss_chance,randomness = 30,.2,1800

if args.i: interval = float(args.i)
if args.m: miss_chance = float(args.m)
if args.r: randomness = float(args.r)
try:
    if args.O: assert int(args.O) > 0
except: 
    print('out of band parameter must be a positive integer')
    quit()
cycle = args.C if args.C in defined_cycles else ''
args.z = args.z if args.z else ''
if cycle == 'furoma' and args.z: keep_onyx = int(''.join([c for c in '0'+args.z if c.isdigit()]))

if args.ua == 'firefox' or not args.ua: useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0'
elif args.ua == 'chrome': useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.3'
elif args.ua == 'mac': useragent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15'
elif args.ua == 'iphone': useragent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Mobile/15E148 Safari/604.1'
elif args.ua == 'edge': useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36 Edge/100.0.1185.39'
else: useragent = args.ua

if args.L:
    try: open(args.L,'r')
    except: 
        with open(args.L,'w') as f: f.write('Timestamp;User;Rank;Trap;Base;Charm;Location;Bait;Type;Power;Bonus;Luck;Attraction;Cheese_Effect;Accuracy;Mouse;Result_Class;Log\n')

print('[%s] starting autohunt. cycle: %s, interval: %s, miss_prob: %s, randomness: %s, antibot=%s'%(datetime.datetime.now().replace(microsecond=0),cycle if cycle else 'none',interval,miss_chance,randomness,'OOB %s sec'%args.O if args.O else 'silent' if args.s else 'standard'))

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
hash,horns,lrje,allowed_regions = '',0,0,[]
post_headers = {'Accept': 'application/json, text/javascript, */*; q=0.01', 'Accept-Language': 'en-GB,en;q=0.5', 'Connection': 'keep-alive', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Sec-Fetch-Dest': 'empty', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-origin', 'TE': 'trailers', 'User-Agent': useragent}
get_headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8', 'Accept-Language': 'en-GB,en;q=0.5', 'Connection': 'keep-alive', 'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'none', 'Sec-Fetch-User': '1', 'TE': 'trailers', 'Upgrade-Insecure-Requests': '1', 'User-Agent': useragent}
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
    elif cycle == 'halloween': halloween()
    
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
    j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/gettrapcomponents.php',cookies=cookies).text)
    
    current_location = j['user']['environment_type']
    current_base = j['user']['base_name'].lower().replace(' ','_')
    current_weapon = j['user']['weapon_name'].lower().replace(' ','_') + '_weapon'
    current_bait = j['user']['bait_name'].lower().replace(' ','_') if j['user']['bait_name'] else 0
    current_trinket = j['user']['trinket_name'].lower().replace('charm','trinket').replace(' ','_') if 'trinket_name' in j['user'] and j['user']['trinket_name'] else None
        
    baits = {l['type']: l['quantity'] for l in j['components'] if l['classification']=='bait' and 'quantity' in l.keys()}
    crafts = {l['type']:l['quantity'] for l in j['components'] if l['classification']=='crafting_item' and 'quantity' in l.keys()}
    trinkets = {l['type']: l['quantity'] for l in j['components'] if l['classification']=='trinket' and 'quantity' in l.keys()}
    potions = {l['type']:l['quantity'] for l in j['components'] if l['classification']=='potion' and 'quantity' in l.keys()}
    bases = [c['type'] for c in j['components'] if c['classification']=='base']
    weapons = [c['type'] for c in j['components'] if c['classification']=='weapon']
    chests = {l['type']:l['quantity'] for l in j['components'] if l['classification']=='convertible' and 'quantity' in l.keys()}
    
    best_weapons = {}
    for k in set([c['power_type_name'] for c in j['components'] if c['classification']=='weapon']): best_weapons[k] = max([c for c in j['components'] if c['classification']=='weapon' and c['power_type_name']==k],key=lambda x:x['power'])['type']
    best_base = max([c for c in j['components'] if c['classification']=='base'],key=lambda x:x['power'] if 'power' in x else 0)['type']
    best_weapon = max([c for c in j['components'] if c['classification']=='weapon'],key=lambda x:x['power'] if 'power' in x else 0)['type']

    return current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j
        
##### CYCLES #####
def template(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_location = ''
    target_base,target_weapon,target_bait,target_trinket = '','','',''
    
    if target_location not in allowed_regions: return print('[TITLE] no access to region')
    if current_location != target_location:
        travel(target_location)
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    
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
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    if current_location != 'town_of_gnawnia':
        travel('town_of_gnawnia')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_bait = ''
    if j['user']['quests']['QuestTownOfGnawnia']['state'] == 'allBountiesComplete': return print('[%s] [GNAWNIA] all bounties complete'%(datetime.datetime.now().replace(microsecond=0)))
    elif j['user']['quests']['QuestTownOfGnawnia']['can_accept'] == 'active': requests.post('https://www.mousehuntgame.com/managers/ajax/environment/town_of_gnawnia.php',{'uh':hash,'action':'accept_bounty'},headers=post_headers,cookies=cookies)
    elif j['user']['quests']['QuestTownOfGnawnia']['can_claim'] == 'active': requests.post('https://www.mousehuntgame.com/managers/ajax/environment/town_of_gnawnia.php',{'uh':hash,'action':'claim_reward'},headers=post_headers,cookies=cookies)
    elif 'bait_like_type' in j['user']['quests']['QuestTownOfGnawnia']: target_bait = j['user']['quests']['QuestTownOfGnawnia']['bait_like_type']
        
    if target_bait:
        if target_bait not in baits or baits[target_bait] < 2: buy(target_bait,2)
        if current_bait != target_bait: arm_bait(target_bait)
        print('[%s] [GNAWNIA] hunting %s with %s'%(datetime.datetime.now().replace(microsecond=0),j['user']['quests']['QuestTownOfGnawnia']['mouse_name'].lower(),target_bait.replace('_',' ')))
    elif loop_counter > 5: 
        print('looped too many times. quitting!')
        quit()
    else: gnawnia(loop_counter+1)    

def windmill():
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    
    if target_location not in allowed_regions: return print('[WINDMILL] no access to windmill. hunting normally')
    if current_location != 'windmill':
        travel('windmill')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    num_cheese = int(j['user']['quests']['QuestWindmill']['items']['grilled_cheese']['quantity'])
    num_flour = int(j['user']['quests']['QuestWindmill']['items']['flour_stat_item']['quantity'])
    if num_cheese: 
        if current_bait != 'grilled_cheese': arm_bait('grilled_cheese')
        print('[%s] [WINDMILL] hunting with grilled cheese: %s left'%(datetime.datetime.now().replace(microsecond=0),num_cheese))
    elif num_flour >= 60: 
        buy('grilled_cheese_pack_convertible',1)
        windmill()
    else: print('[%s] [WINDMILL] getting flour: have %s'%(datetime.datetime.now().replace(microsecond=0),num_flour))

def harbour():
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    if target_location not in allowed_regions: return print('[HARBOUR] no access to harbour. hunting normally')
    if current_location != 'harbour':
        travel('harbour')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    if 'QuestHarbour' not in j['user']['quests']: return
    if j['user']['quests']['QuestHarbour']['status'] == 'searchStarted' and j['user']['quests']['QuestHarbour']['can_claim_status'] == 'active':
        requests.post('https://www.mousehuntgame.com/managers/ajax/environment/harbour.php',{'action':'claimBooty','uh':hash},headers=post_headers,cookies=cookies)
    elif j['user']['quests']['QuestHarbour']['status'] == 'canBeginSearch':
        requests.post('https://www.mousehuntgame.com/managers/ajax/environment/harbour.php',{'action':'beginSearch','uh':hash},headers=post_headers,cookies=cookies)
        
def mountain(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_location,target_bait = 'mountain',''
    
    if target_location not in allowed_regions: return print('[MOUNTAIN] no access to mountain. hunting normally')
    if current_location != target_location:
        travel(target_location)
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    
    if 'power_trinket' not in trinkets or trinkets['power_trinket'] <= 5: buy('power_trinket',5)
    if current_trinket != 'power_trinket': arm_charm('power_trinket')
    
    if 'abominable_asiago_cheese' in baits: 
        target_bait = 'abominable_asiago_cheese'
        print('[%s] [MOUNTAIN] hunting with abominable asiago'%(datetime.datetime.now().replace(microsecond=0)))
    elif 'faceted_sugar_crafting_item' in crafts and crafts['faceted_sugar_crafting_item'] >= 3 and 'ice_curd_crafting_item' in crafts and crafts['ice_curd_crafting_item'] >= 3: craft({'faceted_sugar_crafting_item':3,'ice_curd_crafting_item':3})
    elif 'cheddore_cheese' in baits: 
        target_bait = 'cheddore_cheese'
        print('[%s] [MOUNTAIN] hunting with cheddore. faceted sugar: %s, ice curd: %s'%(datetime.datetime.now().replace(microsecond=0),crafts['faceted_sugar_crafting_item'] if 'faceted_sugar_crafting_item' in crafts else 0,crafts['ice_curd_crafting_item'] if 'ice_curd_crafting_item' in crafts else 0))
    elif j['user']['quests']['QuestMountain']['boulder_status'] == 'can_claim': requests.post('https://www.mousehuntgame.com/managers/ajax/environment/mountain.php',{'action':'claim_reward','uh':hash},cookies=cookies,headers=post_headers)
    else:
        target_bait = 'brie_cheese'
        if target_bait not in baits or baits[target_bait] <= 10: buy(target_bait,100)
        print('[%s] [MOUNTAIN] hitting boulder. boulder hp: %s'%(datetime.datetime.now().replace(microsecond=0),j['user']['quests']['QuestMountain']['boulder_hp']))
        
    if target_bait:
        if current_bait != target_bait: arm_bait(target_bait)
    elif loop_counter > 5: 
        print('looped too many times. quitting!')
        quit()
    else: mountain(loop_counter+1)

def mousoleum(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_bait,target_location,target_weapon = '','',''
    
    if 'laboratory' not in allowed_regions: return print('[MOUSOLEUM] no access to laboratory. hunting normally')
    if 'Shadow' not in best_weapons: return print('[MOUSOLEUM] no shadow weapon. hunting normally')
    if 'radioactive_blue_cheese' not in baits or 'mousoleum' not in allowed_regions: 
        if 'radioactive_blue_cheese_potion' in potions: 
            buy('brie_cheese',20)
            s,m = get_recipes(j,'radioactive_blue_cheese_potion')
            potion('radioactive_blue_cheese_potion',m)
        elif 'greater_radioactive_blue_cheese_potion' in potions: 
            buy('brie_cheese',66)
            s,m = get_recipes(j,'greater_radioactive_blue_cheese_potion')
            potion('greater_radioactive_blue_cheese_potion',m)
        else: 
            target_bait,target_location,target_weapon = 'brie_cheese','laboratory',best_weapons['Shadow']
            if 'brie_cheese' not in baits or baits['brie_cheese'] <= 10: buy('brie_cheese',10)
            print('[%s] [MOUSOLEUM] hunting with %s at %s: %s left'%(datetime.datetime.now().replace(microsecond=0),target_bait.replace('_',' '),target_location.replace('_',' '),baits[target_bait]))
    else:         
        if current_location != 'mousoleum':
            travel('mousoleum')
            current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
        if j['user']['quests']['QuestMousoleum']['has_wall']:
            if j['user']['quests']['QuestMousoleum']['wall_health'] <= 20 and int(j['user']['quests']['QuestMousoleum']['items']['mousoleum_wall_stat_item']['quantity']): requests.post('https://www.mousehuntgame.com/managers/ajax/environment/mousoleum.php',{'action':'repair_wall','uh':hash},cookies=cookies,headers=post_headers)
            elif 'crimson_cheese' in baits: 
                target_bait,target_location,target_weapon = 'crimson_cheese','mousoleum',best_weapons['Shadow']
                print('[%s] [MOUSOLEUM] hunting with %s at %s. wall health: %s, slats obtained: %s, radioactive cheese left: %s'%(datetime.datetime.now().replace(microsecond=0),target_bait.replace('_',' '),target_location.replace('_',' '),j['user']['quests']['QuestMousoleum']['wall_health'],j['user']['quests']['QuestMousoleum']['items']['mousoleum_wall_stat_item']['quantity'],baits[target_bait]))
            elif 'crimson_curd_crafting_item' in crafts and crafts['crimson_curd_crafting_item'] >= 6: craft({'crimson_curd_crafting_item':6})
            else: 
                target_bait,target_weapon,target_location = 'radioactive_blue_cheese',best_weapons['Shadow'],'mousoleum'
                print('[%s] [MOUSOLEUM] wall up, collecting crimson curds. curds: %s, wall health: %s, slats on hand: %s, radioactive cheese left: %s'%(datetime.datetime.now().replace(microsecond=0),crafts['crimson_curd_crafting_item'] if 'crimson_curd_crafting_item' in crafts else 0,j['user']['quests']['QuestMousoleum']['wall_health'],j['user']['quests']['QuestMousoleum']['items']['mousoleum_wall_stat_item']['quantity'],baits[target_bait]))
        elif int(j['user']['quests']['QuestMousoleum']['items']['mousoleum_wall_stat_item']['quantity']) >= 30: requests.post('https://www.mousehuntgame.com/managers/ajax/environment/mousoleum.php',{'action':'build_wall','uh':hash},cookies=cookies,headers=post_headers)
        else:
            target_bait,target_weapon,target_location = 'radioactive_blue_cheese',best_weapons['Shadow'],'mousoleum'
            print('[%s] [MOUSOLEUM] collecting slats for wall. slats obtained: %s, radioactive cheese left: %s'%(datetime.datetime.now().replace(microsecond=0),j['user']['quests']['QuestMousoleum']['items']['mousoleum_wall_stat_item']['quantity'],baits[target_bait]))

    if target_bait:
        if current_bait != target_bait: arm_bait(target_bait)
        if current_location != target_location: travel(target_location)
        if target_weapon and current_weapon != target_weapon: arm_weapon(target_weapon)
    elif loop_counter > 5: 
        print('looped too many times. quitting!')
        quit()
    else: mousoleum(loop_counter+1)       

def tree(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_location,target_weapon,target_bait = best_weapons['Tactical'] if 'Tactical' in best_weapons else best_weapon,'',''
    
    if 'great_gnarled_tree' not in allowed_regions: return print('[TREE] no access to tree. hunting normally')
    if 'brie_cheese' not in baits or baits['brie_cheese'] <= 15: buy('brie_cheese',10)
    
    if 'gnarled_cheese' in baits and 'f' in args.z: 
        target_location, target_bait = 'great_gnarled_tree','gnarled_cheese'
        print('[%s] [TREE] hunting with gnarled cheese: %s left'%(datetime.datetime.now().replace(microsecond=0),baits['gnarled_cheese']))
    elif 'cherry_cheese' in baits and 'c' in args.z: 
        target_location,target_bait = 'great_gnarled_tree','cherry_cheese'
        print('[%s] [TREE] hunting with cherry cheese: %s left'%(datetime.datetime.now().replace(microsecond=0),baits['cherry_cheese']))
    elif 'wicked_gnarly_cheese' in baits and 'h' in args.z: 
        target_location,target_bait = 'lagoon','wicked_gnarly_cheese'
        print('[%s] [TREE] hunting with wicked gnarly cheese: %s left'%(datetime.datetime.now().replace(microsecond=0),baits['wicked_gnarly_cheese']))
    elif 'gnarled_cheese' in baits and 'h' in args.z: 
        target_location,target_bait = 'lagoon','gnarled_cheese'
        print('[%s] [TREE] hunting with gnarled cheese: %s left'%(datetime.datetime.now().replace(microsecond=0),baits['gnarled_cheese']))
    elif 'gnarled_cheese_potion' in potions and ('f' in args.z or 'h' in args.z):
        s,m = get_recipes(j,'gnarled_cheese_potion')
        potion('gnarled_cheese_potion',m)
    elif 'wicked_gnarly_potion' in potions and 'h' in args.z: 
        s,m = get_recipes(j,'wicked_gnarly_potion')
        potion('wicked_gnarly_potion',m)
    elif 'cherry_potion' in potions and 'c' in args.z: 
        s,m = get_recipes(j,'cherry_potion')
        potion('cherry_potion',m)
    else: 
        target_location,target_bait = 'great_gnarled_tree','brie_cheese'
        print('[%s] [TREE] hunting for potions'%(datetime.datetime.now().replace(microsecond=0)))
        
    if target_bait:
        if target_bait and current_bait != target_bait: arm_bait(target_bait)
        if target_weapon and current_weapon != target_weapon: arm_weapon(target_weapon)
        if current_location != target_location and target_location in allowed_regions: travel(target_location)
    elif loop_counter > 5: 
        print('looped too many times. quitting!')
        quit()
    else: tree(loop_counter+1)

def furoma(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_bait = ''
    
    if 'dojo' not in allowed_regions: return print('[FUROMA] no access to furoma. hunting normally')
    if 'Tactical' not in best_weapons: return print('[FUROMA] no tactical weapon. hunting normally')
    if current_weapon != best_weapons['Tactical']: arm_weapon(best_weapons['Tactical'])
    
    if 'onyx_gorgonzola_cheese' in baits: target_location, target_bait = 'pinnacle_chamber', 'onyx_gorgonzola_cheese'
    elif 'onyx_stone_craft_item' in crafts and crafts['onyx_stone_craft_item'] >= keep_onyx:
        if current_location != 'pinnacle_chamber': travel('pinnacle_chamber')
        buy('curds_and_whey_craft_item',60)
        buy('ionized_salt_craft_item',6)
        craft({'curds_and_whey_craft_item':60,'ionized_salt_craft_item':6,'onyx_stone_craft_item':1})
    elif 'rumble_cheese' in baits: target_location, target_bait = 'pinnacle_chamber', 'rumble_cheese'
    elif 'masters_seal_craft_item' in crafts:
        if current_location != 'pinnacle_chamber': travel('pinnacle_chamber')
        buy('curds_and_whey_craft_item',20)
        buy('ionized_salt_craft_item',1)
        craft({'curds_and_whey_craft_item':20,'ionized_salt_craft_item':1,'masters_seal_craft_item':1})
    elif 'master_claw_shard_craft_item' not in crafts:
        if 'susheese_cheese' in baits: target_location, target_bait = 'meditation_room', 'susheese_cheese'
        elif 'token_of_the_cheese_claw_craft_item' in crafts and crafts['token_of_the_cheese_claw_craft_item'] >= 3:
            if current_location != 'meditation_room': travel('meditation_room')
            buy('curds_and_whey_craft_item',1)
            buy('nori_craft_item',3)
            buy('burroughs_salmon_craft_item',1)
            craft({'token_of_the_cheese_claw_craft_item':3,'curds_and_whey_craft_item':3,'nori_craft_item':1,'burroughs_salmon_craft_item':1})
        else: 
            target_location, target_bait = 'dojo','brie_cheese'
            print('[%s] [FUROMA] hunting for claw token at dojo: gotten %s'%(datetime.datetime.now().replace(microsecond=0),crafts['token_of_the_cheese_claw_craft_item'] if 'token_of_the_cheese_claw_craft_item' in crafts else 0))
    elif 'master_fang_shard_craft_item' not in crafts:
        if 'combat_cheese' in baits: target_location, target_bait = 'meditation_room', 'combat_cheese'
        elif 'token_of_the_cheese_fang_craft_item' in crafts and crafts['token_of_the_cheese_fang_craft_item'] >= 3:
            if current_location != 'meditation_room': travel('meditation_room')
            buy('curds_and_whey_craft_item',5)
            buy('splintered_wood_craft_item',1)
            buy('paintbrand_paint_craft_item',1)
            craft({'token_of_the_cheese_fang_craft_item':3,'curds_and_whey_craft_item':5,'splintered_wood_craft_item':1,'paintbrand_paint_craft_item':1})
        else: 
            target_location, target_bait = 'dojo','brie_cheese'
            print('[%s] [FUROMA] hunting for fang token at dojo: gotten %s'%(datetime.datetime.now().replace(microsecond=0),crafts['token_of_the_cheese_fang_craft_item'] if 'token_of_the_cheese_fang_craft_item' in crafts else 0))
    elif 'master_belt_shard_craft_item' not in crafts:
        if 'glutter_cheese' in baits: target_location, target_bait = 'meditation_room', 'glutter_cheese'
        elif 'token_of_the_cheese_belt_craft_item' in crafts and crafts['token_of_the_cheese_belt_craft_item'] >= 3:
            if current_location != 'meditation_room': travel('meditation_room')
            buy('curds_and_whey_craft_item',7)
            buy('invisiglu_craft_item',1)
            buy('cheesy_fluffs_craft_item',1)
            craft({'token_of_the_cheese_belt_craft_item':3,'curds_and_whey_craft_item':7,'invisiglu_craft_item':1,'cheesy_fluffs_craft_item':1})
        else: 
            target_location, target_bait = 'dojo','brie_cheese'
            print('[%s] [FUROMA] hunting for belt token at dojo: gotten %s'%(datetime.datetime.now().replace(microsecond=0),crafts['token_of_the_cheese_belt_craft_item'] if 'token_of_the_cheese_belt_craft_item' in crafts else 0))
    else:
        if current_location != 'pinnacle_chamber': travel('pinnacle_chamber')
        buy('curds_and_whey_craft_item',20)
        buy('ionized_salt_craft_item',1)
        craft({'curds_and_whey_craft_item':20,'ionized_salt_craft_item':1,'master_claw_shard_craft_item':1,'master_belt_shard_craft_item':1,'master_fang_shard_craft_item':1})
                
    if target_bait:
        if target_bait and current_bait != target_bait: arm_bait(target_bait)
        if target_location and current_location != target_location: travel(target_location)
        if target_location != 'dojo': print('[%s] [FUROMA] hunting with %s at %s: %s left'%(datetime.datetime.now().replace(microsecond=0),target_bait.replace('_',' '),target_location.replace('_',' '),baits[target_bait]))
    elif loop_counter > 5: 
        print('looped too many times. quitting!')
        quit()
    else: furoma(loop_counter+1)

def burglar(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_location, target_weapon, target_bait = 'bazaar', best_weapons['Physical'], ''
    
    if 'bazaar' not in allowed_regions: return print('[BURGLAR] no access to bazaar. hunting normally')
    if current_location != target_location: travel(target_location)
    if 'brie_cheese' not in baits or baits['brie_cheese'] < 10: buy('brie_cheese',10)
    target_bait = 'gilded_cheese' if 'gilded_cheese' in baits else 'brie_cheese'
    
    if target_weapon or target_bait:
        if target_bait and current_bait != target_bait: arm_bait(target_bait)
        if target_weapon and current_weapon != target_weapon: arm_weapon(target_weapon)
        print('[%s] [BURGLAR] hunting with %s: %s left'%(datetime.datetime.now().replace(microsecond=0),target_bait.replace('_',' '),baits[target_bait]))
    elif loop_counter > 5: 
        print('looped too many times. quitting!')
        quit()
    else: template(loop_counter+1)

def gauntlet(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_location,target_bait,target_weapon = 'kings_gauntlet','',''
    
    if target_location not in allowed_regions: return print('[GAUNTLET] no access to gauntlet. hunting normally')
    if current_location != target_location: travel(target_location)
            
    if 'gauntlet_cheese_8' in baits: target_bait, target_weapon = 'gauntlet_cheese_8', best_weapons['Forgotten'] if 'Forgotten' in best_weapons else best_weapons['Physical']
    elif 'gauntlet_potion_8' in potions: 
        s,m = get_recipes(j,'gauntlet_potion_8')
        potion('gauntlet_potion_8',s if 's' in args.z and 'super_brie_cheese' in baits else m)
    elif 'gauntlet_cheese_7' in baits: target_bait, target_weapon = 'gauntlet_cheese_7', best_weapons['Hydro'] if 'Hydro' in best_weapons else best_weapons['Physical']
    elif 'gauntlet_potion_7' in potions: 
        if 'brie_cheese' not in baits or baits['brie_cheese'] < 2: buy('brie_cheese',2)
        s,m = get_recipes(j,'gauntlet_potion_7')
        potion('gauntlet_potion_7',s if 's' in args.z and 'super_brie_cheese' in baits else m)
    elif 'gauntlet_cheese_6' in baits: target_bait, target_weapon = 'gauntlet_cheese_6', best_weapons['Arcane'] if 'Arcane' in best_weapons else best_weapons['Physical']
    elif 'gauntlet_potion_6' in potions: 
        if 'brie_cheese' not in baits or baits['brie_cheese'] < 3: buy('brie_cheese',3)
        s,m = get_recipes(j,'gauntlet_potion_6')
        potion('gauntlet_potion_6',s if 's' in args.z and 'super_brie_cheese' in baits else m)
    elif 'gauntlet_cheese_5' in baits: target_bait, target_weapon = 'gauntlet_cheese_5', best_weapons['Shadow'] if 'Shadow' in best_weapons else best_weapons['Physical']
    elif 'gauntlet_potion_5' in potions: 
        if 'brie_cheese' not in baits or baits['brie_cheese'] < 4: buy('brie_cheese',4)
        s,m = get_recipes(j,'gauntlet_potion_5')
        potion('gauntlet_potion_5',s if 's' in args.z and 'super_brie_cheese' in baits else m)
    elif 'gauntlet_cheese_4' in baits: target_bait, target_weapon = 'gauntlet_cheese_4', best_weapons['Tactical'] if 'Tactical' in best_weapons else best_weapons['Physical']
    elif 'gauntlet_potion_4' in potions: 
        if 'brie_cheese' not in baits or baits['brie_cheese'] < 4: buy('brie_cheese',4)
        s,m = get_recipes(j,'gauntlet_potion_4')
        potion('gauntlet_potion_4',s if 's' in args.z and 'super_brie_cheese' in baits else m)
    elif 'gauntlet_cheese_3' in baits: target_bait, target_weapon = 'gauntlet_cheese_3', best_weapons['Tactical'] if 'Tactical' in best_weapons else best_weapons['Physical']
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
        print('[%s] [GAUNTLET] hunting at tier %s with %s. %s bait left'%(datetime.datetime.now().replace(microsecond=0),target_bait[-1] if target_bait[-1] in '8765432' else '1',target_weapon,baits[target_bait]))
    elif loop_counter > 5: 
        print('looped too many times. quitting!')
        quit()
    else: gauntlet(loop_counter+1)

def tribal(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_weapon, target_bait, target_location, target_item = '','','',''
    
    if 'nerg_plains' not in allowed_regions: return print('[TRIBAL] no access to tribal isles. hunting normally')
    if 'dragons_chest_convertible' in chests: r = requests.post('https://www.mousehuntgame.com/managers/ajax/users/useconvertible.php',{'item_type':'dragons_chest_convertible','uh':hash,'item_qty':1},headers=post_headers,cookies=cookies)
    done = 0
    
    if ('vengeful_vanilla_stilton_cheese' in baits or ('raisins_of_wrath' in crafts and 'pinch_of_annoyance_crafting_item' in crafts and 'bottled_up_rage_crafting_item' in crafts and 'vanilla_bean_crafting_item' in crafts) or 'vanilla_stilton_cheese' in baits or ('vanilla_bean_crafting_item' in crafts and crafts['vanilla_bean_crafting_item'] >= 15)) and 'c' not in args.z and 'h' not in args.z and 'balacks_cove' not in allowed_regions:
        if current_location != 'balacks_cove': travel('balacks_cove')
        if json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/gettrapcomponents.php',cookies=cookies).text)['user']['quests']['QuestBalacksCove']['tide']['level'] == 'low': 
            done = 1
            if 'vengeful_vanilla_stilton_cheese' in baits: target_location, target_bait, target_weapon = 'balacks_cove','vengeful_vanilla_stilton_cheese',best_weapons['Forgotten']
            elif 'raisins_of_wrath' in crafts and 'pinch_of_annoyance_crafting_item' in crafts and 'bottled_up_rage_crafting_item' in crafts and 'vanilla_bean_crafting_item' in crafts:                
                buy('curds_and_whey_craft_item',1)
                buy('coconut_milk_craft_item',1)
                buy('ionized_salt_craft_item',1)
                craft({'curds_and_whey_craft_item':1,'coconut_milk_craft_item':1,'ionized_salt_craft_item':1,'vanilla_bean_crafting_item':1,'raisins_of_wrath':1,'pinch_of_annoyance_crafting_item':1,'bottled_up_rage_crafting_item':1})
            elif 'vanilla_stilton_cheese' in baits: 
                target_bait, target_weapon, target_item = 'vanilla_stilton_cheese',best_weapons['Forgotten'],'pinch'
                print('[%s] [TRIBAL] hunting with vanilla stilton. raisins of wrath: %s, pinch of annoyance: %s, bottled-up rage: %s'%(datetime.datetime.now().replace(microsecond=0),crafts['raisins_of_wrath'] if 'raisins_of_wrath' in crafts else 0,crafts['pinch_of_annoyance_crafting_item'] if 'pinch_of_annoyance_crafting_item' in crafts else 0,crafts['bottled_up_rage_crafting_item'] if 'bottled_up_rage_crafting_item' in crafts else 0))
            else: 
                buy('curds_and_whey_craft_item',15)
                buy('coconut_milk_craft_item',15)
                buy('salt_craft_item',15)
                craft({'curds_and_whey_craft_item':15,'coconut_milk_craft_item':15,'salt_craft_item':15,'vanilla_bean_crafting_item':15})
    if done: pass
    elif 'inferno_havarti_cheese' in baits and 'Draconic' in best_weapons and 'c' not in args.z: target_location, target_bait, target_weapon, target_item = 'dracano','inferno_havarti_cheese',best_weapons['Draconic'],'vanilla_bean_crafting_item'
    elif 'inferno_pepper_craft_item' in crafts and crafts['inferno_pepper_craft_item'] >= 6 and 'fire_salt_craft_item' in crafts and crafts['fire_salt_craft_item'] >= 6:
        buy('curds_and_whey_craft_item',18)
        buy('coconut_milk_craft_item',16)
        craft({'curds_and_whey_craft_item':18,'coconut_milk_craft_item':16,'fire_salt_craft_item':6,'inferno_pepper_craft_item':6})
    elif ('fire_salt_craft_item' not in crafts or crafts['fire_salt_craft_item'] < 6) and 'c' not in args.z:
        if 'dragon_ember' in crafts: hammer('dragon_ember',1)
        elif 'spicy_havarti_cheese' in baits: target_location, target_bait, target_weapon, target_item = 'jungle_of_dread','spicy_havarti_cheese',best_weapons['Shadow'],'fire_salt_craft_item'
        elif 'spicy_red_pepper_craft_item' in crafts and crafts['spicy_red_pepper_craft_item'] >= 6: 
            if current_location != 'jungle_of_dread': travel('jungle_of_dread')
            buy('curds_and_whey_craft_item',18)
            buy('coconut_milk_craft_item',12)
            buy('salt_craft_item',6)
            craft({'curds_and_whey_craft_item':18,'coconut_milk_craft_item':12,'salt_craft_item':6,'spicy_red_pepper_craft_item':6})
        elif 'red_pepper_seed_craft_item' in crafts and crafts['red_pepper_seed_craft_item'] >= 2:
            if 'plant_pot_craft_item' not in crafts: 
                if current_location != 'jungle_of_dread': travel('jungle_of_dread')
                buy('plant_pot_craft_item',1)
            craft({'red_pepper_seed_craft_item':2,'plant_pot_craft_item':1})
            time.sleep(1)
            requests.post('https://www.mousehuntgame.com/managers/ajax/users/useconvertible.php',{'item_type':'red_pepper_plant_convertible','uh':hash,'item_qty':1},cookies=cookies,headers=post_headers)
        else: 
            if 'crunchy_cheese' in baits: target_location, target_bait, target_weapon, target_item = 'derr_dunes','crunchy_cheese',best_weapons['Physical'], 'red_pepper_seed_craft_item'
            elif 'delicious_stone_craft_item' in crafts and crafts['delicious_stone_craft_item'] >= 30: 
                if current_location != 'derr_dunes': travel('derr_dunes')
                buy('salt_craft_item',30)
                buy('coconut_milk_craft_item',20)
                buy('curds_and_whey_craft_item',10)
                craft({'curds_and_whey_craft_item':10,'coconut_milk_craft_item':20,'salt_craft_item':30,'delicious_stone_craft_item':30})
            else: target_location, target_bait, target_weapon, target_item = 'derr_dunes','gouda_cheese',best_weapons['Physical'], 'delicious_stone_craft_item'
    else:
        if 'blue_pepper_seed_craft_item' in crafts and 'red_pepper_seed_craft_item' in crafts and 'yellow_pepper_seed_craft_item' in crafts:
            if 'plant_pot_craft_item' not in crafts: 
                if current_location != 'dracano': travel('dracano')
                buy('plant_pot_craft_item',1)
            craft({'blue_pepper_seed_craft_item':1,'red_pepper_seed_craft_item':1,'yellow_pepper_seed_craft_item':1,'plant_pot_craft_item':1})
            time.sleep(1)
            requests.post('https://www.mousehuntgame.com/managers/ajax/users/useconvertible.php',{'item_type':'white_pepper_plant_convertible','uh':hash,'item_qty':1},cookies=cookies,headers=post_headers)
        elif 'red_pepper_seed_craft_item' not in crafts: 
            if 'crunchy_cheese' in baits: target_location, target_bait, target_weapon = 'derr_dunes','crunchy_cheese',best_weapons['Physical']
            elif 'delicious_stone_craft_item' in crafts and crafts['delicious_stone_craft_item'] >= 30: 
                if current_location != 'derr_dunes': travel('derr_dunes')
                buy('curds_and_whey_craft_item',10)
                buy('coconut_milk_craft_item',20)
                buy('salt_craft_item',30)
                craft({'curds_and_whey_craft_item':10,'coconut_milk_craft_item':20,'salt_craft_item':30,'delicious_stone_craft_item':30})
            else: target_location, target_bait, target_weapon, target_item = 'derr_dunes','gouda_cheese',best_weapons['Physical'],'delicious_stone_craft_item'
        elif 'yellow_pepper_seed_craft_item' not in crafts: 
            if 'gumbo_cheese' in baits: target_location, target_bait, target_weapon = 'nerg_plains','gumbo_cheese',best_weapons['Tactical']
            elif 'savoury_vegatables_craft_item' in crafts and crafts['savoury_vegatables_craft_item'] >= 30: 
                if current_location != 'nerg_plains': travel('nerg_plains')
                buy('curds_and_whey_craft_item',90)
                buy('coconut_milk_craft_item',15)
                buy('salt_craft_item',1)
                craft({'curds_and_whey_craft_item':90,'coconut_milk_craft_item':15,'salt_craft_item':1,'savoury_vegatables_craft_item':30})
            else: target_location, target_bait, target_weapon, target_item = 'nerg_plains','gouda_cheese',best_weapons['Tactical'], 'savoury_vegatables_craft_item'
        else: 
            if 'shell_cheese' in baits: target_location, target_bait, target_weapon = 'elub_shore','shell_cheese',best_weapons['Hydro']
            elif 'seashell_craft_item' in crafts and crafts['seashell_craft_item'] >= 30: 
                if current_location != 'elub_shore': travel('elub_shore')
                buy('curds_and_whey_craft_item',60)
                buy('coconut_milk_craft_item',10)
                buy('salt_craft_item',40)
                craft({'curds_and_whey_craft_item':60,'coconut_milk_craft_item':10,'salt_craft_item':40,'seashell_craft_item':30})
            else: target_location, target_bait, target_weapon, target_item = 'elub_shore','gouda_cheese',best_weapons['Hydro'], 'seashell_craft_item'

    if target_weapon or target_bait or target_location:
        if target_location and current_location != target_location: travel(target_location)
        if target_bait and current_bait != target_bait: arm_bait(target_bait)
        if target_weapon and current_weapon != target_weapon: arm_weapon(target_weapon)
        if not target_item: print('[%s] [TRIBAL] hunting at %s with %s: %s %s left'%(datetime.datetime.now().replace(microsecond=0),target_location.replace('_',' '),target_weapon.replace('_',' '),baits[target_bait],target_bait.replace('_',' ')))
        elif target_item != 'pinch': print('[%s] [TRIBAL] hunting for %s, gotten %s. %s %s left'%(datetime.datetime.now().replace(microsecond=0),target_item.replace('_craft_item','').replace('_',' '),crafts[target_item] if target_item in crafts else 0,baits[target_bait],target_bait.replace('_',' ')))
    elif loop_counter > 5: 
        print('looped too many times. quitting!')
        quit()
    else: tribal(loop_counter+1)
    
def digby(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_weapon, target_location, target_bait, target_base, target_trinket = '','','','',''
    
    if 'town_of_digby' not in allowed_regions: return print('[DIGBY] no access to digby. hunting normally')
    if 'limelight_cheese' in baits: 
        target_location, target_bait, target_weapon, target_base, target_trinket = 'town_of_digby', 'limelight_cheese', best_weapons['Physical'], best_base,'drilling_trinket'
        print('[%s] [DIGBY] hunting with limelight at digby: %s left'%(datetime.datetime.now().replace(microsecond=0),baits['limelight_cheese']))
    elif 'radioactive_sludge_craft_item' in crafts and crafts['radioactive_sludge_craft_item'] >= 3:
        travel('town_of_digby')
        buy('living_shard_crafting_item',3)
        buy('curds_and_whey_craft_item',30)
        craft({'curds_and_whey_craft_item':30,'living_shard_crafting_item':3,'radioactive_sludge_craft_item':3})
    elif 'radioactive_blue_cheese' in baits:
        target_location, target_bait, target_weapon, target_base, target_trinket = 'mountain', 'radioactive_blue_cheese', best_weapons['Physical'], 'explosive_base', None
        print('[%s] [DIGBY] getting sludge: have %s'%(datetime.datetime.now().replace(microsecond=0),crafts['radioactive_sludge_craft_item'] if 'radioactive_sludge_craft_item' in crafts else 0))
    elif 'radioactive_blue_cheese_potion' in potions: 
        s,m = get_recipes(j,'radioactive_blue_cheese_potion')
        potion('radioactive_blue_cheese_potion',m)
    elif 'greater_radioactive_blue_cheese_potion' in potions: 
        s,m = get_recipes(j,'greater_radioactive_blue_cheese_potion')
        potion('greater_radioactive_blue_cheese_potion',m)
    else: 
        target_location, target_bait, target_weapon, target_base, target_trinket = 'laboratory', 'brie_cheese', best_weapons['Physical'], best_base, None
        print('[%s] [DIGBY] hunting for radioactive potion'%(datetime.datetime.now().replace(microsecond=0)))
        
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
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_weapon, target_location, target_bait, target_base = '','','',''
    if 'brie_cheese' not in baits or baits['brie_cheese'] < 30: buy('brie_cheese',30)
    
    if 'pollution_outbreak' not in allowed_regions: return print('[TOXIC] no access to toxic spill. hunting normally')
    done = 0
    if 'super_radioactive_blue_cheese' in baits or 'magical_radioactive_blue_cheese' in baits:
        k = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/pages/page.php',{'uh':hash,'page_class':'Travel'},cookies=cookies).text)
        ranks = ['Hero','Knight','Lord/Lady','Baron/Baroness','Count/Countess','Duke/Duchess','Grand Duke/Grand Duchess','Archduke/Archduchess']
        current_rank = ranks.index(k['user']['title_name'])
        required_rank = ranks.index([p for p in [p for p in k['page']['tabs'][0]['regions'] if p['type']=='burroughs'][0]['environments'] if p['type']=='pollution_outbreak'][0]['title_name'])
        if required_rank > current_rank: pass
        else:
            if current_location != 'pollution_outbreak':
                travel('pollution_outbreak')
                current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
            j = j['user']['quests']['QuestPollutionOutbreak']
            done,target_location,target_weapon,target_base = 1,'pollution_outbreak',best_weapons['Hydro'],best_base
            mp,rs,rq,rp,cp = j['max_pollutinum'],j['refine_status'],j['refine_quantity'],j['refined_pollutinum'],j['items']['crude_pollutinum_stat_item']['quantity'] if 'crude_pollutinum_stat_item' in j['items'] else 0
            
            if (rs == 'default' and cp + rq > mp) or (rs == 'active' and cp < rq): 
                requests.post('https://www.mousehuntgame.com/managers/ajax/environment/pollution_outbreak.php',{'uh':hash,'action':'toggle_refine_mode'},headers=post_headers,cookies=cookies)
                rs = 'default' if rs == 'active' else 'active'
            
            if 'magical_radioactive_blue_cheese' in baits: target_bait = 'magical_radioactive_blue_cheese'
            elif 'super_radioactive_blue_cheese' in baits: target_bait = 'super_radioactive_blue_cheese'
            
            print('[%s] [TOXIC] hunting at spill with %s. bait left: %s, mode: %s, crude: %s, refined: %s. '%(datetime.datetime.now().replace(microsecond=0),target_bait.split('_')[0],baits[target_bait],'collecting' if rs == 'default' or rs == 'disabled' else 'refining',cp, rp))
                
    if done: pass
    elif 'super_radioactive_blue_potion' in potions and 'radioactive_blue_cheese' in baits and baits['radioactive_blue_cheese'] >= 6: 
        potion('super_radioactive_blue_potion',get_recipes(j,'super_radioactive_blue_potion')[1],qty=min(potions['super_radioactive_blue_potion'],baits['radioactive_blue_cheese']//6))
    elif 'radioactive_sludge_craft_item' in crafts and 'radioactive_curd_crafting_item' in crafts and crafts['radioactive_curd_crafting_item'] >= 2:
        num = min(crafts['radioactive_curd_crafting_item']//2,crafts['radioactive_sludge_craft_item'])
        if 'ionized_salt_craft_item' not in crafts or crafts['ionized_salt_craft_item'] < num: 
            if 'laboratory' != current_location: travel('laboratory')
            buy('ionized_salt_craft_item',num)
        craft({'ionized_salt_craft_item':1,'radioactive_sludge_craft_item':1,'radioactive_curd_crafting_item':2},qty=num)    
    elif 'radioactive_sludge_craft_item' in crafts and 'radioactive_blue_cheese' in baits and baits['radioactive_blue_cheese'] >= 2: hammer('radioactive_blue_cheese',min(crafts['radioactive_sludge_craft_item'],baits['radioactive_blue_cheese']//2)*2)
    elif 'super_radioactive_blue_potion' not in potions and 'radioactive_blue_cheese' in baits:
        target_location, target_bait, target_weapon, target_base = 'mountain', 'radioactive_blue_cheese', best_weapons['Physical'], 'explosive_base'
        print('[%s] [TOXIC] getting sludge: have %s'%(datetime.datetime.now().replace(microsecond=0),crafts['radioactive_sludge_craft_item'] if 'radioactive_sludge_craft_item' in crafts else 0))
    elif 'radioactive_blue_cheese_potion' in potions: potion('radioactive_blue_cheese_potion',get_recipes(j,'radioactive_blue_cheese_potion')[1])
    elif 'greater_radioactive_blue_cheese_potion' in potions: potion('greater_radioactive_blue_cheese_potion',get_recipes(j,'greater_radioactive_blue_cheese_potion')[1])
    else: 
        target_location, target_bait, target_weapon, target_base = 'laboratory', 'brie_cheese', best_weapons['Physical'], best_base
        print('[%s] [TOXIC] hunting for radioactive potion'%(datetime.datetime.now().replace(microsecond=0)))
        
    if target_bait:
        if target_location and target_location != current_location: travel(target_location)
        if target_bait and target_bait != current_bait: arm_bait(target_bait)
        if target_weapon and target_weapon != current_weapon: arm_weapon(target_weapon)
        if target_base and target_base != current_base: arm_base(target_base)
    elif loop_counter > 5: 
        print('looped too many times. quitting!')
        quit()
    else: toxic(loop_counter+1)

def iceberg():
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    
    if 'iceberg' not in allowed_regions: return print('[ICEBERG] no access to iceberg. hunting normally')
    if current_location != 'iceberg':
        travel('iceberg')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    progress = int(j['user']['quests']['QuestIceberg']['user_progress'])
    turns = j['user']['quests']['QuestIceberg']['turns_taken']
    
    num_trinket = 0
    if 'trinket_name' in j['user'] and current_trinket in ['sticky_trinket','wax_trinket']:
        num_trinket = int(j['user']['trinket_quantity'])
        if num_trinket <= 5: 
            buy('bag_%ss_convertible'%(current_trinket.replace('trinket','charm')),1)
            num_trinket += 5
    elif 'wax_trinket' in trinkets:
        current_trinket,num_trinket = 'wax_trinket',trinkets['wax_trinket']
        if num_trinket <= 5: 
            buy('bag_wax_charms_convertible',1)
            num_trinket += 5
        arm_charm(current_trinket)
    else:
        current_trinket,num_trinket = 'sticky_trinket',trinkets['sticky_trinket'] if 'sticky_trinket' in trinkets else 0
        if num_trinket <= 5: 
            buy('bag_sticky_charms_convertible',1)
            num_trinket += 5
        arm_charm(current_trinket)
    
    if 'gouda_cheese' not in baits or baits['gouda_cheese'] <= 10: buy('gouda_cheese',100)
    if current_bait != 'gouda_cheese': arm_bait('gouda_cheese')
    
    good_weapons = ['steam_laser_mk_iii_weapon','steam_laser_mk_ii_weapon','steam_laser_mk_i_weapon']
    for weapon in good_weapons: 
        if weapon in weapons: 
            target_weapon = weapon
            break
    else: 
        print('[%s] [ICEBERG] no steam laser weapon. aborting!'%(datetime.datetime.now().replace(microsecond=0)))
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
    print('[%s] [ICEBERG] progress: %s feet (%s), hunt #%s. %s left: %s'%(datetime.datetime.now().replace(microsecond=0),progress,segment,turns,current_trinket,num_trinket))

def zzt_parse(i): return 'not trying' if i < 0 else 'done' if i > 15 else 'got queen' if i > 14 else 'got %s rook%s'%(i-12,'s' if i-13 else '') if i > 12 else 'got %s bishop%s'%(i-10,'s' if i-11 else '') if i > 10 else 'got %s knight%s'%(i-8,'s' if i-9 else '') if i > 8 else 'got %s pawn%s'%(i,'' if i == 1 else 's')
def zzt():
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_bait, target_weapon, target_trinket, target_base = '','','',''
    
    if 'seasonal_garden' not in allowed_regions: return print('[ZUGZWANG] no access to zzt. hunting normally')
    if current_location not in ['seasonal_garden','zugzwang_tower']:
        travel('seasonal_garden')
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    amplifier, maxamp = int(j['user']['viewing_atts']['zzt_amplifier']), int(j['user']['viewing_atts']['zzt_max_amplifier'])
    if 'gouda_cheese' not in baits or baits['gouda_cheese'] <= 10: buy('gouda_cheese',100)
    
    if 'mystic_curd_crafting_item' in crafts and 'tech_cheese_mould_crafting_item' in crafts:
        buy('ionized_salt_craft_item',12)
        num_sb = baits['super_brie_cheese'] if 'super_brie_cheese' in baits and args.z and 's' in args.z else 0
        num_me = crafts['magic_essence_craft_item'] if 'magic_essence_craft_item' in crafts and args.z and 's' in args.z else 0
        if num_sb + num_me >= 6:
            requests.post('https://www.mousehuntgame.com/managers/ajax/users/usehammer.php',{'item_type':'super_brie_cheese','item_qty':6-num_me,'uh':hash},cookies=cookies,headers=post_headers)            
            craft({'tech_cheese_mould_crafting_item':1,'mystic_curd_crafting_item':1,'ionized_salt_craft_item':12,'magic_essence_craft_item':6})
        else: craft({'tech_cheese_mould_crafting_item':1,'mystic_curd_crafting_item':1,'ionized_salt_craft_item':12})
        
    if amplifier == maxamp or (current_location == 'zugzwang_tower' and amplifier):
        if current_location != 'zugzwang_tower': 
            travel('zugzwang_tower')
            current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
        tech_progress, mage_progress = int(j['user']['viewing_atts']['zzt_tech_progress']), int(j['user']['viewing_atts']['zzt_mage_progress'])
        target_base = max([c for c in j['components'] if c['classification']=='base'],key=lambda x:x['power'])['type'] if amplifier < 60 else 'wooden_base_with_target'
        
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

        print('[%s] [ZUGZWANG] hunting at tower. mystic progress: %s/16 (%s), technic progress: %s/16 (%s). amplifier: %s/%s'%(datetime.datetime.now().replace(microsecond=0),mage_progress,zzt_parse(mage_progress),tech_progress,zzt_parse(tech_progress),amplifier,maxamp))
    else: 
        if current_location != 'seasonal_garden': 
            travel('seasonal_garden')
            current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
        season = j['user']['viewing_atts']['season']
        
        target_base = max([c for c in j['components'] if c['classification']=='base'],key=lambda x:x['power'])['type']
        target_bait,target_trinket = 'gouda_cheese','amplifier_trinket' if 'amplifier_trinket' in trinkets else None
        num_trinket = trinkets[target_trinket] if target_trinket in trinkets else 0
        if season == 'sr': target_weapon = best_weapons['Tactical']
        elif season == 'sg': target_weapon = best_weapons['Physical']
        elif season == 'fl': target_weapon = best_weapons['Shadow']
        elif season == 'wr': target_weapon = best_weapons['Hydro']
        
        print('[%s] [ZUGZWANG] charging amplifier: %s/%s. amplifier charms: %s'%(datetime.datetime.now().replace(microsecond=0),amplifier,maxamp,num_trinket))
    
    if current_weapon != target_weapon: arm_weapon(target_weapon)
    if current_bait != target_bait: arm_bait(target_bait)
    if current_base != target_base: arm_base(best_base)
    if current_trinket != target_trinket: arm_charm(target_trinket if target_trinket else 'disarm')

def halloween(loop_counter=0):
    current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
    target_location = 'halloween_event_location'
    
    if target_location not in allowed_regions: return print('[HALLOWEEN] no access to halloween location. hunting normally')
    if 'alchemists_cookbook_base' in bases: best_base = 'alchemists_cookbook_base'
    target_weapon = 'boiling_cauldron_weapon' if 'boiling_cauldron_weapon' in weapons else best_weapon
    target_bait,target_trinket = '',''
    if current_location != target_location:
        travel(target_location)
        current_location,current_base,current_weapon,current_bait,current_trinket,baits,crafts,trinkets,potions,bases,weapons,chests,best_weapons,best_base,best_weapon,j = prologue()
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
        print('[%s] [HALLOWEEN] level %s, %s bait left%s. roots: %s. %s%s'%(datetime.datetime.now().replace(microsecond=0),level-1,baits[target_bait],'; obtained %s x tier %s ingredient'%(event_items['cauldron_tier_%s_ingredient_stat_item'%level],level) if level <= 4 else '',num_root,'cauldron 0: time %s, queue %s. '%(cauldron_0_time,cauldron_0_queue_len) if cauldron_0_time else '','cauldron 1: time %s, queue %s. '%(cauldron_1_time,cauldron_1_queue_len) if cauldron_1_time else ''))
    elif loop_counter > 5: 
        print('looped too many times. quitting!')
        quit()
    else: halloween(loop_counter+1)
        
##### HORN #####
def status_check(print_gold=False):
    global lrje,hash,allowed_regions
    r = requests.get('https://www.mousehuntgame.com/camp.php',cookies=cookies)
    if r.url == 'https://www.mousehuntgame.com/login.php':
        print('[%s] session expired. logging in again'%(datetime.datetime.now().replace(microsecond=0)))
        login()
        r = requests.get('https://www.mousehuntgame.com/camp.php',cookies=cookies)
    hash = re.findall('"unique_hash":"([^"]*)"',r.text)[0]
    if not horns%20: allowed_regions = regions()
    if 'Out of bait!' in r.text: 
        if cycle: 
            choose_cycle()
            r = requests.get('https://www.mousehuntgame.com/camp.php',cookies=cookies)
        if 'Out of bait!' in r.text: change_bait()
    if 'The King has sent you a special reward' in r.text: antibot(r.text)
    m = re.findall('"gold":([^,]*)',r.text)
    if m and print_gold: print('[%s] current gold: %s, current points: %s, bait left: %s; horns so far: %s'%(datetime.datetime.now().replace(microsecond=0),m[0],re.findall('"points":([^,]*)',r.text)[0],re.findall('"bait_quantity":([^,]*)',r.text)[0],horns))
    m = re.findall('lastReadJournalEntryId = ([^;]*);',r.text)
    if m: lrje = m[0]
    return int(re.findall('"next_activeturn_seconds":(\d*)',r.text)[0])

def wait(delay_mins,norandom=False):
    next_wait = delay_mins*60 + random.random()*randomness
    if norandom: next_wait = delay_mins*60
    m,s,ms = int(next_wait//60),int(next_wait%60),int((next_wait*1000)%1000)
    n = ('%s'%(datetime.datetime.now().replace(microsecond=0)+datetime.timedelta(minutes=m,seconds=s))).split(' ')[1]
    print('[%s] next horn in %s mins %s secs at %s'%(datetime.datetime.now().replace(microsecond=0),m,s,n))
    target_time = time.time()+next_wait
    if next_wait > 5:
        time.sleep(5)
        status_check(print_gold=True)
    if time.time() < target_time: time.sleep(target_time-time.time())

def horn():
    fail = 0
    while 1:     
        wait_time = status_check()
        if wait_time: 
            print('[%s] horn not ready'%(datetime.datetime.now().replace(microsecond=0)))
            wait(float((wait_time+2)/60),norandom=True)
        if cycle: choose_cycle()
        d = {"uh":hash,"last_read_journal_entry_id":lrje,"hg_is_ajax":1,"sn":"Hitgrab"}
        r = requests.post('https://www.mousehuntgame.com/managers/ajax/turns/activeturn.php',d,cookies=cookies,headers=post_headers)
        if '"success":1' in r.text: 
            j = json.loads(r.text)
            with open(args.L,'a') as g: g.write(f"{datetime.datetime.now().replace(microsecond=0)};{j['user']['username']};{j['user']['title_name']};{j['user']['weapon_name']};{j['user']['base_name']};{j['user']['trinket_name']};{j['user']['environment_name']};{j['user']['bait_name']};{j['user']['trap_power_type_name']};{j['user']['trap_power']};{j['user']['trap_power_bonus']};{j['user']['trap_luck']};{j['user']['trap_attraction_bonus']};{j['user']['trap_cheese_effect']};{j['user']['title_percent_accurate']};{j['journal_markup'][0]['render_data']['mouse_type']};{j['journal_markup'][0]['render_data']['css_class']};\"{re.sub('<[^>]*>','',j['journal_markup'][0]['render_data']['text'])}\"\n")
            for e in j['journal_markup']:
                try: 
                    t = e['render_data']['text']
                    for n in re.findall('<[^>]*>',t): t = t.replace(n,'')
                    s = t.index('!',10) if '!' in t[10:-2] else t.index('.')
                    if t[:s+1]: print('[%s] %s'%(datetime.datetime.now().replace(microsecond=0),t[:s+1].lstrip()))
                    if t[s+1:]:
                        t = t[s+1:]
                        s = t.index('.',t.index('oz.')+3) if 'oz.' in t else t.index('.')
                        if t[:s+1]: print('[%s] %s'%(datetime.datetime.now().replace(microsecond=0),t[:s+1].lstrip()))
                        if t[s+1:]: print('[%s] %s'%(datetime.datetime.now().replace(microsecond=0),t[s+1:].lstrip()))
                except: print('[%s] %s'%(datetime.datetime.now().replace(microsecond=0),t.lstrip()))
            return 1
        elif 'It\'s too soon to sound the horn again!' in r.text: 
            m = re.findall('I sounded my horn (.*) ago',r.text)[0]
            if 'minute' in m and 'second' in m: minutes,seconds = m.split(' ')[0],m.split(' ')[2]
            elif 'minute' in m: minutes,seconds = m.split(' ')[0],0
            else: minutes,seconds = 0,m.split(' ')[0]
            print('[%s] too soon to sound the horn! last sounded %s mins %s secs ago'%(datetime.datetime.now().replace(microsecond=0),minutes,seconds))
            wait(interval-int(minutes))
        else:
            fail += 1
            if fail >= max_fail:
                print('[%s] %s consecutive horn failures. aborting'%(datetime.datetime.now().replace(microsecond=0),fail))
                quit()
            print('[%s] failed to sound the horn. trying again in a bit...'%(datetime.datetime.now().replace(microsecond=0)))
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
        if args.O: 
            m,s= int(int(args.O)//60),int(int(args.O)%60)
            n = ('%s'%(datetime.datetime.now().replace(microsecond=0)+datetime.timedelta(minutes=m,seconds=s))).split(' ')[1]
            print('[%s] captcha not solved. sleeping %s mins %s secs till %s'%(datetime.datetime.now().replace(microsecond=0),m,s,n))
            time.sleep(int(args.O))
            text = requests.get('https://www.mousehuntgame.com/camp.php',cookies=cookies).text
            if 'The King has sent you a special reward' not in text: return print('[%s] captcha solved'%(datetime.datetime.now().replace(microsecond=0)))
        else:         
            url = re.findall('<img src="([^"]*)" alt="King\'s Reward">',text)[0]
            with open('kingsreward.png','wb') as f: f.write(requests.get(url).content)
            if not args.s: os.system('kingsreward.png')
            while 1:
                v = input('[%s] enter captcha value, type \'url\' to see image url, or press ENTER to view image...'%(datetime.datetime.now().replace(microsecond=0)))
                if v.lower() == 'url': print('[%s] %s'%(datetime.datetime.now().replace(microsecond=0),url))
                elif v == '': 
                    os.system('kingsreward.png')
                    print("\033[F",end='')
                elif len(v)==5 and v.isalnum(): break
                else: print('[%s] captcha code must be 5 alphanumeric characters'%(datetime.datetime.now().replace(microsecond=0)))
            os.system('del kingsreward.png')
            d = {'puzzle_answer':v,'uh':hash}
            r = requests.post('https://www.mousehuntgame.com/managers/ajax/users/solvePuzzle.php',d,cookies=cookies,headers=post_headers)
            if 'Reward claimed!' in r.text: return print('[%s] code correct'%(datetime.datetime.now().replace(microsecond=0)))
            elif 'Incorrect claim code, please try again' in r.text: print('[%s] incorrect code. code is now different'%(datetime.datetime.now().replace(microsecond=0)))
            else: print('[%s] something went wrong. check if code might have changed'%(datetime.datetime.now().replace(microsecond=0)))
            text = requests.get('https://www.mousehuntgame.com/camp.php',cookies=cookies).text

wait(max(float((status_check()+2)/60),float(args.w if args.w else 0)),norandom=True)
while 1:
    if random.random() >= miss_chance or horns==0: 
        horns += horn()
        wait(interval)
    else: 
        print('[%s] giving this one a miss'%(datetime.datetime.now().replace(microsecond=0)))
        wait(random.random()*interval)
        