# login
username = ''
password = ''
cookie = ''

########## CODE ##########

banner = '''
MM   MM  H    H   CCCC   OOOO   NN    N   SSSSS   OOOO   L      EEEEE
M M M M  H    H  C      O    O  N N   N  S       O    O  L      E
M  M  M  HHHHHH  C      O    O  N  N  N  SSSSS   O    O  L      EEEEE
M     M  H    H  C      O    O  N   N N       S  O    O  L      E
M     M  H    H   CCCC   OOOO   N    NN  SSSSS    OOOO   LLLLL  EEEEE
'''
print(banner)
print('[=] loading imports and function definitions')

import requests,json,re,os

########## LOGIN RELATED FUNCTIONS ##########
def login_creds():
    global cookie,hash,password,user,sn_user_id,cookies
    d = {'action':'loginHitGrab','username':username,'password':password}
    r = requests.post('https://www.mousehuntgame.com/managers/ajax/users/session.php',d,headers=post_headers)
    try: 
        cookie,hash,user,sn_user_id = r.cookies['HG_TOKEN'], json.loads(r.text)['user']['unique_hash'], json.loads(r.text)['user']['username'], json.loads(r.text)['user']['sn_user_id']
        cookies = {'HG_TOKEN':cookie}
    except: 
        print('[-] login failed')
        password = ''
       
def login_cookie():
    global hash,cookie,user,sn_user_id,cookies
    d = {'v':3,'client_id':'Cordova:iOS','client_version':'1.135.2','login_token':cookie}
    r = requests.post('https://www.mousehuntgame.com/api/action/passiveturn',d,headers=api_headers)
    if r.status_code == 200:
        j = json.loads(r.text)['user']
        hash,user,sn_user_id = j['uh'], j['name'], j['sn_user_id']
        cookies = {'HG_TOKEN':cookie}
        return json.loads(r.text)
    else:
        print('[-] cookie expired')
        cookie = ''
        return None

def try_login():
    if cookie: 
        print('[=] testing provided cookie value')
        login_cookie()
    if not hash and username and password: 
        print('[=] attempting to login with provided credentials')
        login_creds()
    if hash: print('[+] authentication successful. session cookie: %s'%(cookie))
     
     
########## PRE-AUTH FUNCTION ##########
def preauth():
    global username,password,cookie
    help_msg = '''
AVAILABLE COMMANDS:
user [username]\t\tenter username
pass [password]\t\tenter password
cookie [cookie]\t\tenter cookie
show\t\t\tshow credentials entered
login\t\t\tattempt to login with provided credentials
exit\t\t\texit mhconsole'''
    
    cmd = input('\nmh [not logged in] > ')
    cmd,args = cmd.split(' ')[0],' '.join(cmd.split(' ')[1:])
    
    if cmd == 'help': print(help_msg)
    elif not cmd: return 0
    elif cmd == 'user' or cmd == 'username':
        if args: 
            username = args
            print('username => %s'%username)
        else: print('command syntax: user [username]')
    elif cmd == 'pass' or cmd == 'password':
        if args: 
            password = args
            print('password => %s'%password)
        else: print('command syntax: pass [password]')
    elif cmd == 'cookie':
        if args: 
            cookie = args
            print('cookie => %s'%cookie)
        else: print('command syntax: cookie [value]')
    elif cmd == 'show': print('''username:\t%s\npassword:\t%s\ncookie:\t\t%s'''%(username,password,cookie))
    elif cmd == 'login' or cmd == 'run':
        if not cookie and not (username and password): print('[-] provide either cookie value or username + password')
        else: try_login()
    elif cmd == 'exit' or cmd == 'quit': exit_mhconsole()
    else: huh()

def huh(): print('command not recognised. type \'help\' to see available commands')    

def exit_mhconsole():
    print('[+] bye!\n')
    quit()


########## POST-AUTH FUNCTIONS ##########
def postauth():
    global hash,user,password,cookie
    help_msg = '''
========== GENERAL COMMANDS ==========
horn\t\t\tsound the horn
info\t\t\tshow account and trap info
unauth\t\t\tgo to preauth console without expiring session
logout\t\t\texpire the current session
exit\t\t\texit mhconsole

========== TRAVELLING ==========
move\t\t\tenumerate possible travel locations
move all\t\tenumerate all travel locations
move [name]\t\ttravel to location by name or s/n

========== TRAP ==========
arm\t\t\tshow available trap components
arm [class]\t\tshow subset of available items. classes: bait, base, weapon, charm
arm [type]\t\tarm strongest weapon of type (physical, tactical, ...)
arm [name]\t\tarm item by name or s/n
arm decharm\t\tremove charm

========== SHOP ==========
buy\t\t\tshow general store items
buy [shop]\t\tshow items in other shops. shops: cheese, trap, charm, all
buy [item] [qty]\tbuy an item by name or s/n

========== CRAFTING ==========
list\t\t\tshow crafting items
show\t\t\tshow items on crafting table
add [item] [qty]\tadd item to crafting table by name or s/n
del [item]\t\tremove item from crafting table by name or s/n
reset\t\t\tclear crafting table
run [#]\t\t\tcraft using table items # times, default 1
hammer\t\t\tlist items that can be hammered
hammer # [qty]\t\tuse hammer on item by s/n, qty times (default 1, 0 for max)
chest\t\t\tlist chests
chest # [qty]\t\topen chest by s/n, qty times (default 1, 0 for max)

========== POTIONS ==========
pot\t\t\tshow all potions
pot #\t\t\tshow recipes for potion by s/n
pot # [rec] [qty]\tuse recipe [rec], [qty] times, for potion # (default 1 for qty, 0 for max)

========== ANTIBOT ==========
kr\t\t\tcheck antibot status
kr url\t\t\tdisplay captcha url
kr show\t\t\tdownload and show captcha image
kr [code]\t\tsolve captcha
'''

    cmd = input('\nmh [%s] %s> '%(user,'(!)' if antibot else '')).strip()
    cmd,args = cmd.split(' ')[0],cmd.split(' ')[1:]
    if cmd == 'help': return print(help_msg)
    elif not cmd: return 0
    elif cmd == 'logout': return logout()
    elif cmd == 'unauth': 
        hash,user,password,cookie = '','','',''
        return print('[+] cookie removed from current console session')
    elif cmd == 'exit' or cmd == 'quit': exit_mhconsole()
    elif cmd in ['horn','info','arm','move','buy','list','add','del','reset','show','run','hammer','chest','pot','kr']: pass
    else: return huh()
    
    content = login_cookie()
    while not content: 
        hash,user = '',''
        try_login()
        if not hash: return print('[-] will have to login manually')
        content = login_cookie()
        print('')
        
    if cmd == 'horn': horn(content)
    elif cmd == 'info': info()
    elif cmd == 'move': move(args)
    elif cmd == 'arm': arm(args)
    elif cmd == 'buy': buy(args)
    elif cmd in ['list','add','del','reset','show','run']: craft(cmd,args)
    elif cmd == 'hammer': hammer(args)
    elif cmd == 'chest': chest(args)
    elif cmd == 'pot': pot(args)
    elif cmd == 'kr': kr(args)
    else: return huh()

def print_entry(t):
    try: 
        for m in re.findall('<[^>]*>',t): t = t.replace(m,'')
        s = t.index('!',20) if '!' in t[20:-2] else t.index('.',(t.index('oz.')+3) if 'oz.' in t else 0)
        if t[:s+1]: print('\t%s'%(t[:s+1].lstrip()))
        if t[s+1:]: print_entry(t[s+1:])
    except: print('\t%s'%(t.lstrip()))
        
def horn(content): 
    global horns
    lpt = content['user']['last_passiveturn_timestamp']
    m = content['user']['next_activeturn_seconds']
    if m: 
        n = ('%s'%(datetime.datetime.now().replace(microsecond=0)+datetime.timedelta(seconds=m))).split(' ')[1]
        return print('[-] too soon to sound. next horn in %s:%s at %s'%(m//60,m%60,n))
    else:
        horn_time = int(time.time())
        d = {'v':3,'client_id':'Cordova:iOS','client_version':'1.135.2','last_passiveturn_timestamp':lpt,'login_token':cookie}        
        r = json.loads(requests.post('https://www.mousehuntgame.com/api/action/turn/me',d,headers=api_headers).text)
        if r['success']: 
            print('[+] successfully sounded the horn. response:\n')
            d = {'v':3,'client_id':'Cordova:iOS','client_version':'1.135.2','offset':0,'limit':72,'return_user':'true','login_token':cookie}        
            r = json.loads(requests.post('https://www.mousehuntgame.com/api/get/journalentries/me',d,headers=api_headers).text)
            for entry in r['entries']:
                if entry['timestamp'] < horn_time: return
                print_entry(entry['text'])
        else: print('[-] failed to sound the horn')
    
def info():     
    global antibot
    content = requests.get('https://www.mousehuntgame.com/camp.php',cookies=cookies,headers=get_headers).text
    antibot = 'The King has sent you a special reward' in content
    
    next_horn = int(re.findall('"next_activeturn_seconds":(\d*)',content)[0])
    next_horn = '%s:%s'%(next_horn//60,next_horn%60) if next_horn else 'READY'
    url = 'https://www.mousehuntgame.com/images/puzzleimage.php?snuid=%s&hash=%s'%(sn_user_id,hash)
    print('HORN INFO\nnext horn:\t%s\nantibot:\t%s\n%s'%(next_horn,'ACTIVE' if antibot else 'inactive','KR url:\t\t%s\n'%url if antibot else ''))
    
    gold = re.findall('"gold":(\d*)',content)[0]
    points = re.findall('"points":(\d*)',content)[0]
    print('WEALTH INFO\ngold:\t\t%s\npoints:\t\t%s\n'%(gold,points))

    base = re.findall('"base_name":"([^"]*)"',content)[0]
    weapon = re.findall('"weapon_name":"([^"]*)"',content)[0]
    type = re.findall('"trap_power_type_name":"([^"]*)"',content)[0]
    bait = re.findall('"bait_name":"([^"]*)"',content)
    bait = bait[0] if bait else 'out of bait'
    baitq = re.findall('"bait_quantity":(\d*)',content)[0]
    power = re.findall('"trap_power":(\d*)',content)[0]
    luck = re.findall('"trap_luck":(\d*)',content)[0]
    freshness = re.findall('"trap_cheese_effect":"([^"]*)"',content)[0]
    print('TRAP INFO\nbase:\t\t%s\nweapon:\t\t%s\ntype:\t\t%s\nbait:\t\t%s\nquantity:\t%s\npower:\t\t%s\nluck:\t\t%s\nfreshness:\t%s'%(base,weapon,type,bait,baitq,power,luck,freshness),end='')
    try: 
        charm = re.findall('"trinket_name":"([^"]*)"',content)[0]
        charmq = re.findall('"trinket_quantity":(\d*)',content)[0]
        print('\ncharm:\t\t%s\ncharm quantity:\t%s\n'%(charm,charmq))
    except: print('\n')
    
    print('LOGIN INFO\ncookie:\t\t%s\nhash:\t\t%s\n'%(cookie,hash))
    
    d = {'uh':hash}
    j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/getmiceeffectiveness.php',d,cookies=cookies,headers=post_headers).text)
    print('LOCATION INFO\nlocation:\t%s'%(j['location']))
    j = j['effectiveness']
    for k in j: print('{0:<12}\t{1}'.format(j[k]['difficulty']+':',', '.join([m['name'] for m in j[k]['mice']])))
    
def move(args): 
    d = {'uh':hash,'page_class':'Travel'}
    j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/pages/page.php',d,cookies=cookies,headers=post_headers).text)
    j = j['page']['tabs'][0]['regions']
    col = {v['name']:[] for v in j}
    act = {}
    i = 1
    for v in j:
        for e in v['environments']: 
            active = e['description'] != 'You haven\'t unlocked this environment yet!'
            col[v['name']].append((i,e['type'],e['name'],active))
            if active and v['name'] not in act: act[v['name']] = []
            if active: act[v['name']].append((i,e['type'],e['name']))
            i += 1
    if not args:
        for n in act:
            print('========== %s =========='%n)
            print('NO.\tMH NAME\t\t\t\tCOMMON NAME')
            for e in act[n]: print('{0:<3}\t{1:<30}\t{2:<25}'.format(e[0],e[1],e[2]))
            print('')
    elif args[0]=='all':
        for n in col:
            print('========== %s =========='%n)
            print('NO.\tMH NAME\t\t\t\tCOMMON NAME\t\t\tACTIVE')
            for e in col[n]: print('{0:<3}\t{1:<30}\t{2:<25}\t{3}'.format(e[0],e[1],e[2],e[3]))
            print('')
    else:
        for e in [x for n in col for x in col[n]]:
            if '_'.join(args).lower() in [str(e[0]),e[1]]: 
                if e[3]: 
                    j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/changeenvironment.php',{'uh':hash,'destination':e[1]},headers=post_headers,cookies=cookies).text)
                    if j['success']: print('[+] travelled to %s'%(e[2].lower()))
                    else: print('[-] %s'%(j['result']))
                else: print('[-] no access to that location')
                return
        print('[-] unrecognised location')

def arm(args):
    j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/gettrapcomponents.php',cookies=cookies,headers=post_headers).text)['components']
    items = {}
    best_weapons = {}
    i = 0
    for c in ['base','weapon','bait','trinket']:
        items[c] = []
        subitems = [i for i in j if i['classification']==c]
        subitems.sort(key=lambda x:x['type'])
        for item in subitems: 
            if c == 'base': items[c].append((i,item['type'],item['name'],item['power'],item['cheese_effect']))
            elif c == 'weapon': 
                items[c].append((i,item['type'],item['name'],item['power_type_name'],item['power'],item['luck'] if 'luck' in item else '0',item['cheese_effect']))
                if item['power_type_name'].lower() not in best_weapons or best_weapons[item['power_type_name'].lower()][1] <= item['power']: best_weapons[item['power_type_name'].lower()] = (item['type'],item['power'])
            elif c == 'bait': items[c].append((i,item['type'],item['name'],item['quantity'] if 'quantity' in item else 0))
            elif c == 'trinket': items[c].append((i,item['type'],item['name'],item['quantity'] if 'quantity' in item else 0))
            i += 1
            
    cmd = '_'.join(args) if args else 'all'
    if cmd == 'help': return print(help_msg)
    if cmd == 'all' or cmd == 'base':
        print('NO.\tMH NAME\t\t\t\t\tCOMMON NAME\t\t\tPOWER\t\tEFFECT')
        for n in items['base']: print('{0:<3}\t{1:<35}\t{2:<30}\t{3:<8}\t{4}'.format(n[0],n[1],n[2],n[3],n[4]))
        print('')
    if cmd == 'all' or cmd == 'weapon' or cmd == 'trap':
        print('NO.\tMH NAME\t\t\t\t\tCOMMON NAME\t\t\tTYPE\t\tPOWER\t\tLUCK\t\tEFFECT')
        for n in items['weapon']: print('{0:<3}\t{1:<35}\t{2:<30}\t{3:<8}\t{4:<8}\t{5:<8}\t{6}'.format(n[0],n[1],n[2]
,n[3],n[4],n[5],n[6]))
        print('')
    if cmd == 'all' or cmd == 'bait':
        print('NO.\tMH NAME\t\t\t\t\tCOMMON NAME\t\t\tQTY')
        for n in items['bait']: print('{0:<3}\t{1:<35}\t{2:<30}\t{3}'.format(n[0],n[1],n[2],n[3]))
        print('')
    if cmd == 'all' or cmd == 'charm':
        print('NO.\tMH NAME\t\t\t\t\tCOMMON NAME\t\t\tQTY')
        for n in items['trinket']: print('{0:<3}\t{1:<35}\t{2:<30}\t{3}'.format(n[0],n[1],n[2],n[3]))
        print('')
    if cmd == 'decharm':
        d = {'uh':hash,'trinket':'disarm'}
        requests.post('https://www.mousehuntgame.com/managers/ajax/users/changetrap.php',d,headers=post_headers,cookies=cookies)
        print('[+] disarmed charm')
    if cmd not in ['all','bait','base','weapon','charm','decharm']:
        if cmd.lower() in best_weapons: 
            d = {'uh':hash,'weapon':best_weapons[cmd.lower()][0]}
            requests.post('https://www.mousehuntgame.com/managers/ajax/users/changetrap.php',d,headers=post_headers,cookies=cookies)
            return print('[+] armed %s'%(best_weapons[cmd.lower()][0]))
        for k in items:
            for n in items[k]:
                if cmd in [str(n[0]),n[1]] or cmd+'_cheese' == n[1] or cmd+'_base' == n[1] or cmd+'_weapon' == n[1] or cmd+'_trinket' == n[1]:
                    d = {'uh':hash,k:n[1]}
                    requests.post('https://www.mousehuntgame.com/managers/ajax/users/changetrap.php',d,headers=post_headers,cookies=cookies)
                    return print('[+] armed %s'%(n[2].lower()))
        print('[-] component not recognised')
    
def buy(args): 
    d = {'uh':hash,'page_class':'Shops'}
    j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/pages/page.php',d,cookies=cookies,headers=post_headers).text)['page']['tabs']
    items = {c['name']:[] for c in j[:-2]}
    i = 0
    for tab in j[:-2]:
        for item in tab['subtabs'][0]['items']: 
            items[tab['name']].append((i,item['item']['type'],item['shop_item_name'],item['gold_cost'],item['refund']))
            i += 1
            
    if not args:
        if 'General Store' in items:    
            print('NO.\tMH NAME\t\t\t\tCOMMON NAME\t\tCOST\t\tREFUND')
            for n in items['General Store']: print('{0:<3}\t{1:<25}\t{2:<20}\t{3:<8}\t{4}'.format(n[0],n[1],n[2],n[3],n[4]))
        else: print('[-] no general store in this location')
    elif args[0]=='cheese' or args[0]=='bait': 
        if 'Cheese Shop' in items:
            print('NO.\tMH NAME\t\t\t\tCOMMON NAME\t\tCOST\t\tREFUND')
            for n in items['Cheese Shop']: print('{0:<3}\t{1:<25}\t{2:<20}\t{3:<8}\t{4}'.format(n[0],n[1],n[2],n[3],n[4]))
        else: print('[-] no cheese shop in this location')
    elif args[0]=='trap': 
        if 'Trapsmith' in items:
            print('NO.\tMH NAME\t\t\t\tCOMMON NAME\t\tCOST\t\tREFUND')
            for n in items['Trapsmith']: print('{0:<3}\t{1:<25}\t{2:<20}\t{3:<8}\t{4}'.format(n[0],n[1],n[2],n[3],n[4]))
        else: print('[-] no trapsmith in this location')
    elif args[0]=='charm': 
        if 'Charm Shop' in items:
            print('NO.\tMH NAME\t\t\t\tCOMMON NAME\t\tCOST\t\tREFUND')
            for n in items['Charm Shop']: print('{0:<3}\t{1:<25}\t{2:<20}\t{3:<8}\t{4}'.format(n[0],n[1],n[2],n[3],n[4]))
        else: print('[-] no charm shop in this location')
    elif args[0]=='all': 
        print('NO.\tMH NAME\t\t\t\tCOMMON NAME\t\tCOST\t\tREFUND')
        for k in items:
            for n in items[k]: print('{0:<3}\t{1:<25}\t{2:<20}\t{3:<8}\t{4}'.format(n[0],n[1],n[2],n[3],n[4]))
    elif len(args) > 1:
        target_name = '_'.join(args[:-1]).lower()
        if target_name == 'curds': target_name = 'curds_and_whey'
        if target_name == 'milk': target_name = 'coconut_milk'        
        for n in [n for k in items for n in items[k]]:
            if target_name in [str(n[0]),n[1]] or (target_name + '_craft_item' == n[1]) or (target_name + '_crafting_item') == n[1] or (target_name + '_cheese') == n[1] or (target_name + '_trinket') == n[1]: 
                target_item = n[1]
                try: quant = int(args[-1])
                except: return print('quantity must be an integer')
                j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/purchases/itempurchase.php',{'uh':hash,'type':target_item,'quantity':quant,'buy':1},headers=post_headers,cookies=cookies).text)
                if j['success']: print('[+] bought %s %s'%(quant,n[2]))
                else: print('[-] %s'%j['error_message'])
                return 0
        print('item not found in stores')
    else: huh()

def craft(cmd,args): 
    global table
    items = get_craft()
            
    if cmd == 'list': 
        print('ITEMS IN INVENTORY')
        list_craft(items)
    elif cmd == 'show': 
        print('ITEMS ON CRAFTING TABLE')
        list_craft(table)
    elif cmd == 'add':
        if len(args) < 2: return print('[-] usage: add [item] [quantity]')
        try: target_item = list(items.keys())[int(args[0])]
        except:
            target_item = '_'.join(args[:-1]).lower()
            if target_item == 'curds': target_item = 'curds_and_whey'
            if target_item == 'milk': target_item = 'coconut_milk'
            if target_item in items.keys(): pass
            elif target_item + '_craft_item' in items.keys(): target_item += '_craft_item'
            elif target_item + '_crafting_item' in items.keys(): target_item += '_crafting_item'
            else: return print('[-] item not found in inventory')
        try: target_quant = int(args[-1])
        except: return print('[-] quantity must be an integer')
        if target_quant > int(items[target_item][1]): return print('[-] quantity exceeds amount in inventory')
        table[target_item] = (items[target_item][0],target_quant)
        print('[+] updated quantity of %s on crafting table to %s'%(items[target_item][0].lower(),target_quant))
    elif cmd == 'reset':
        table = {}
        print('[+] crafting table cleared')
    elif cmd == 'del':
        if not args: return print('[-] usage: del [item]')
        try: target_item = list(table.keys())[int(args[0])]
        except:            
            if args[0] in table.keys(): target_item = args[0]
            else: return print('[-] item not found on table')
        name = table[target_item][0].lower()
        table.pop(target_item)
        print('[+] %s removed from crafting table'%(name))
    elif cmd == 'run': 
        try: times = int(args[0])
        except: times = 1
        d = {'parts[%s]'%l:table[l][1] for l in table}
        d['craftQty'] = times
        d['uh'] = hash
        try: j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/crafting.php',d,cookies=cookies,headers=post_headers).text)
        except: return print('[-] something went wrong')
        if j['success'] == 1:
            t = j['messageData']['message_model']['messages'][0]['messageData']['content']['body']
            for n in re.findall('<[^>]*>',t): t = t.replace(n,'')
            print('[+] %s'%t)
        else: print('[-] %s'%j['jsDialog']['tokens']['content']['value'])
    elif cmd == 'back': return 0
    elif cmd == 'exit' or cmd == 'quit': exit_mhconsole()
    else: huh()
        
def get_craft(): 
    j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/gettrapcomponents.php',cookies=cookies,headers=post_headers).text)['components']
    items = sorted([c for c in j if c['classification'] == 'crafting_item'],key=lambda x:x['type'])
    return {l['type']:(l['name'],l['quantity']) for l in items}

def list_craft(items):
    print('NO.\tQTY\tMH NAME\t\t\t\t\t\tCOMMON NAME')
    for ind,n in enumerate(items): print('{0:<3}\t{1:<5}\t{2:<40}\t{3}'.format(ind,items[n][1],n,items[n][0]))

def hammer(args): 
    d = {'uh':hash,'page_class':'Inventory','page_arguments[tab]':'crafting','page_arguments[sub_tab]':'hammer'}
    j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/pages/page.php',d,cookies=cookies,headers=post_headers).text)
    hammerables = {item['type']:(item['quantity'],item['hammer_result_item_type']) for category in j['page']['tabs'][2]['subtabs'][2]['tags'] for item in category['items']}
    items = sorted(list(hammerables.keys()))
            
    if not args: 
        print('NO.\tQTY\tMH NAME\t\t\t\t\t\tHAMMER RESULT')
        for ind,n in enumerate(items): print('{0:<3}\t{1:<5}\t{2:<40}\t{3}'.format(ind,hammerables[n][0],n,hammerables[n][1]))
    elif len(args) > 2: print('[-] usage: hammer [s/n] [qty]')
    else:
        if len(args) == 2:
            try: 
                qty = int(args[-1])
                assert qty >= 0
            except: return print('[-] quantity must be a non-negative integer')
        else: qty = 1
        try: 
            target_item = int(args[0])
            assert target_item >= 0
        except: return print('[-] usage: s/n must be a non-negative integer')
        try: target_item = items[target_item]
        except: return print('[-] s/n not found')
        if not qty: qty = hammerables[target_item][0]
        if qty > hammerables[target_item][0]: return print('[-] quantity exceeds inventory')
        
        j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/usehammer.php',{'uh':hash,'item_type':target_item,'item_qty':qty},headers=post_headers,cookies=cookies).text)
        if j['success'] == 1:
            t = j['messageData']['message_model']['messages'][0]['messageData']['content']['body']
            for n in re.findall('<[^>]*>',t): t = t.replace(n,'')
            print('[+] %s'%t)
        else: print('[-] %s'%j['jsDialog']['tokens']['content']['value'])       
        
def chest(args): 
    j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/gettrapcomponents.php',cookies=cookies,headers=post_headers).text)
    chests = {l['type']:l['quantity'] for l in j['components'] if l['classification']=='convertible' and 'quantity' in l.keys()}
    items = sorted(list(chests.keys()))
            
    if not args: 
        print('NO.\tQTY\tMH NAME')
        for ind,n in enumerate(items): print('{0:<3}\t{1:<5}\t{2}'.format(ind,chests[n],n))
    elif len(args) > 2: print('[-] usage: chest [s/n] [qty]')
    else:
        if len(args) == 2:
            try: 
                qty = int(args[-1])
                assert qty >= 0
            except: return print('[-] quantity must be a non-negative integer')
        else: qty = 1
        try: 
            target_item = int(args[0])
            assert target_item >= 0
        except: return print('[-] usage: s/n must be a non-negative integer')
        try: target_item = items[target_item]
        except: return print('[-] s/n not found')
        if not qty: qty = chests[target_item]
        if qty > chests[target_item]: return print('[-] quantity exceeds inventory')
        
        chest_time = int(time.time())
        j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/useconvertible.php',{'uh':hash,'item_type':target_item,'item_qty':qty},headers=post_headers,cookies=cookies).text)
        if j['success'] == 1: 
            d = {'v':3,'client_id':'Cordova:iOS','client_version':'1.135.2','offset':0,'limit':72,'return_user':'true','login_token':cookie}        
            r = json.loads(requests.post('https://www.mousehuntgame.com/api/get/journalentries/me',d,headers=api_headers).text)
            for entry in r['entries']:
                if entry['timestamp'] < chest_time: return
                print(entry['text'])
        else: print('[-] failed')
        
def pot(args):
    j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/gettrapcomponents.php',cookies=cookies,headers=post_headers).text)
    potions = {l['type']:l['quantity'] for l in j['components'] if l['classification']=='potion' and 'quantity' in l.keys()}
    baits = {l['type']: l['quantity'] for l in j['components'] if l['classification']=='bait' and 'quantity' in l.keys()}
    items = sorted(list(potions.keys()))
    
    if not args: 
        print('NO.\tQTY\tPOTION')
        for ind,n in enumerate(items): print('{0:<3}\t{1:<5}\t{2}'.format(ind,potions[n],n))
        return
    
    if len(args) > 3: return print('[-] usage: pot [s/n] [rec] [qty]')
    try: 
        target_item = int(args[0])
        assert target_item >= 0
    except: return print('[-] usage: s/n must be a non-negative integer')
    try: target_item = items[target_item]
    except: return print('[-] s/n not found')
    p = {r['recipe_index']:(r['consumed_item_name'],r['consumed_item_type'],r['consumed_item_cost'],r['produced_item_name'],r['produced_item_type'],r['produced_item_yield']) for r in [l for l in j['components'] if l['classification']=='potion' if l['type']==target_item][0]['recipe_list']}
    
    if len(args) == 1:
        print('===== RECIPES FOR %s ====='%target_item.replace('_',' ').upper())
        print('NO.\tCONSUMED ITEM\t\t\tQTY\tPRODUCED ITEM\t\t\tQTY')
        for i in range(len(p.keys())): print('{0:<3}\t{1:<30}\t{2}\t{3:<30}\t{4}'.format(i,p[i][0],p[i][2],p[i][3],p[i][5]))
        return
        
    try: 
        rec = int(args[1])
        assert rec >= 0
    except: return print('[-] recipe s/n must be a non-negative integer')
    if rec not in p: return print('[-] recipe not found')
        
    if len(args) == 3:
        try: 
            qty = int(args[-1])
            assert qty >= 0
        except: return print('[-] quantity must be a non-negative integer')
    else: qty = 1
    if not qty: qty = potions[target_item]
    if qty > potions[target_item]: return print('[-] quantity exceeds number of potions in inventory')
    if p[rec][1] not in baits or baits[p[rec][1]] < qty*p[rec][2]: return print('[-] insufficient %s: need %s, have %s'%(p[rec][0].lower(),qty*p[rec][2],baits[p[rec][1]] if p[rec][1] in baits else 0))
    
    j = json.loads(requests.post('https://www.mousehuntgame.com/managers/ajax/users/usepotion.php',{'potion':target_item,'num_potions':qty,'recipe_index':rec,'uh':hash},headers=post_headers,cookies=cookies).text)
    if j['success'] == 1:
        t = j['messageData']['message_model']['messages'][0]['messageData']['content']['title'] + ' ' + j['messageData']['message_model']['messages'][0]['messageData']['content']['body']
        for n in re.findall('<[^>]*>',t): t = t.replace(n,'')
        print('[+] %s'%t)
    else: print('[-] %s'%j['messageData']['popup']['messages'][0]['messageData']['body'])
    
def kr(args):
    global antibot
    if not args or not antibot or args[0] not in ['show','url']: antibot = 'The King has sent you a special reward' in requests.get('https://www.mousehuntgame.com/camp.php',cookies=cookies,headers=get_headers).text
    
    if not antibot: return print('[=] antibot inactive')
    elif not args: return print('[!] antibot active')
    elif len(args) > 1: return huh()
    
    url = 'https://www.mousehuntgame.com/images/puzzleimage.php?snuid=%s&hash=%s'%(sn_user_id,hash)
    if args[0] == 'url': return print('[=] captcha url: %s'%url)
    elif args[0] == 'show':        
        with open('kingsreward.png','wb') as f: f.write(requests.get(url).content)
        subprocess.run(['kingsreward.png'],shell=True,stderr=subprocess.DEVNULL)
    elif len(args[0])!=5 or not args[0].isalnum(): return print('[-] code must be 5 alphanumeric characters')
    else:
        subprocess.run(['del','kingsreward.png'],shell=True,stderr=subprocess.DEVNULL)
        d = {'puzzle_answer':args[0],'uh':hash}
        r = requests.post('https://www.mousehuntgame.com/managers/ajax/users/solvePuzzle.php',d,cookies=cookies,headers=post_headers)
        if 'Reward claimed!' in r.text: 
            antibot = False
            return print('[+] code correct')
        elif 'Incorrect claim code, please try again' in r.text: print('[-] incorrect code. code is now different')
        else: print('[-] something went wrong. check if code might have changed')

def logout(): 
    global hash,cookie
    d = {'uh':hash,'action':'logout'}
    requests.post('https://www.mousehuntgame.com/managers/ajax/users/session.php',d,headers=post_headers,cookies=cookies)
    hash,user,cookie = '','',''
    print('[+] cookie expired')


useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0'
post_headers = {'Accept': 'application/json, text/javascript, */*; q=0.01', 'Accept-Language': 'en-GB,en;q=0.5', 'Connection': 'keep-alive', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Sec-Fetch-Dest': 'empty', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-origin', 'TE': 'trailers', 'User-Agent': useragent}
get_headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8', 'Accept-Language': 'en-GB,en;q=0.5', 'Connection': 'keep-alive', 'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'none', 'Sec-Fetch-User': '1', 'TE': 'trailers', 'Upgrade-Insecure-Requests': '1', 'User-Agent': useragent}
api_headers = {'Accept': 'application/json, text/javascript, */*; q=0.01', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Origin': 'file://', 'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}
user,hash,sn_user_id,antibot = '','','',False
table,cookies = {},{}

try: cookie = cookie
except: cookie = ''
try: username,password = username,password
except: username,password = '',''

if cookie or (username and password): try_login()
while 1:
    if not hash: preauth()
    else: postauth()
