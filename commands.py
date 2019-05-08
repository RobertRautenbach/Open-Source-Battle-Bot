import base64
from colorama import init, Fore, Back, Style
import config
import decryptor
import io
import json
from orator import DatabaseManager, Model
import os
import packet
import PySimpleGUI as sg
from random import choice
from random import randint
import requests
from string import ascii_uppercase
import sys
import time
import webbrowser

# Coloroma autoreset
init(autoreset=True)

def complete_stage(stage_id, difficulty, kagi = None):
    # Completes a given stage stage name or ID has been supplied as a string
    # kagi must be correct kagi item ID if used

    # Check if user has supplied a stage name and searches DB for correct stage id
    if not stage_id.isnumeric():
        try:
            stage_id = str(config.Quests.where('name', 'like', '%' + stage_id
                                        + '%').first().id)
        except:
            print(Fore.RED \
                + 'Could not match event, try typing the name more accurately...')
            return 0

    #Retrieve correct stage name to print 
    try:
        print('Begin stage: ' + stage_id + ' ' \
                + config.Quests.find(int(stage_id)).name + ' | Difficulty: ' \
                + str(difficulty) + ' Deck: ' + str(config.deck))
    except:
        print(Fore.RED + 'Does this quest exist?')
        return 0
        


    # Begin timer for overall stage completion, rounded to second.
    timer_start = int(round(time.time(), 0))

    # Form First Request
    APIToken = ''.join(choice(ascii_uppercase) for i in range(63))
    friend = get_friend(stage_id, difficulty)

    if friend['is_cpu'] == False:
        if kagi != None:
            sign = json.dumps({'difficulty' : difficulty, 'eventkagi_item_id': kagi,'friend_id' : friend['id'], 'is_playing_script' : True, 'selected_team_num': config.deck})
        else:
            sign = json.dumps({'difficulty' : difficulty, 'friend_id' : friend['id'], 'is_playing_script' : True, 'selected_team_num': config.deck})
    else:
        if kagi != None:
            sign = json.dumps({'difficulty' : difficulty, 'eventkagi_item_id': kagi,'cpu_friend_id' : friend['id'], 'is_playing_script' : True, 'selected_team_num': config.deck})
        else:
            sign = json.dumps({'difficulty' : difficulty, 'cpu_friend_id' : friend['id'], 'is_playing_script' : True, 'selected_team_num': config.deck})


    enc_sign = packet.encrypt_sign(sign)

    # ## Send First Request

    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Authorization': packet.mac('POST', '/quests/' + stage_id
                                    + '/sugoroku_maps/start'),
        'Content-type': 'application/json',
        'X-Platform': config.platform,
        'X-AssetVersion': '////',
        'X-DatabaseVersion': '////',
        'X-ClientVersion': '////',
        }
    data = {'sign': enc_sign}

    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/quests/' + stage_id \
              + '/sugoroku_maps/start'
    else:
        url = 'http://ishin-production.aktsk.jp/quests/' + stage_id \
              + '/sugoroku_maps/start'

    r = requests.post(url, data=json.dumps(data), headers=headers)

    # Form second request
    # Time for request sent
    
    if 'sign' in r.json():
        dec_sign = packet.decrypt_sign(r.json()['sign'])
    elif 'error' in r.json():
        print(Fore.RED + str(r.json()['error']))
        # Check if error was due to lack of stamina
        if r.json()['error']['code'] == 'act_is_not_enough':
            # Check if allowed to refill stamina
            if config.allow_stamina_refill == True:
                refill_stamina()
                r = requests.post(url, data=json.dumps(data),
                              headers=headers)
            else:
                print(Fore.RED + 'Stamina refill not allowed.')
                return 0
        elif r.json()['error']['code'] == 'active_record/record_not_found':
            return 0
        elif r.json()['error']['code'] == 'invalid_area_conditions_potential_releasable':
            print(Fore.RED + 'You do not meet the coniditions to complete potential events')
            return 0
        else:
            print(Fore.RED + str(r.json()['error']))
            return 0
    else:
        print(Fore.RED + str(r.json()))
        return 0
    if 'sign' in r.json():
        dec_sign = packet.decrypt_sign(r.json()['sign'])
    #Retrieve possible tile steps from response
    steps = []
    for x in dec_sign['sugoroku']['events']:
        steps.append(x)

    finish_time = int(round(time.time(), 0)+2000)
    start_time = finish_time - randint(6200000, 8200000)
    damage = randint(500000, 1000000)

    # Hercule punching bag event damage
    if str(stage_id)[0:3] == '711':
        damage = randint(78000000, 79000000)

    sign = {
        'actual_steps': steps,
        'difficulty': difficulty,
        'elapsed_time': finish_time - start_time,
        'energy_ball_counts_in_boss_battle': [4,6,0,6,4,3,0,0,0,0,0,0,0, ],
        'has_player_been_taken_damage': False,
        'is_cheat_user': False,
        'is_cleared': True,
        'is_player_special_attack_only': False,
        'max_damage_to_boss': damage,
        'min_turn_in_boss_battle': 0,
        'quest_finished_at_ms': finish_time,
        'quest_started_at_ms': start_time,
        'steps': steps,
        'token': dec_sign['token'],
        }

    enc_sign = packet.encrypt_sign(json.dumps(sign))

    # Send second request

    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Authorization': packet.mac('POST', '/quests/' + stage_id
                                + '/sugoroku_maps/finish'),
        'Content-type': 'application/json',
        'X-Platform': config.platform,
        'X-AssetVersion': '////',
        'X-DatabaseVersion': '////',
        'X-ClientVersion': '////',
        }
    data = {'sign': enc_sign}
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/quests/' + stage_id \
              + '/sugoroku_maps/finish'
    else:
        url = 'http://ishin-production.aktsk.jp/quests/' + stage_id \
            + '/sugoroku_maps/finish'

    r = requests.post(url, data=json.dumps(data), headers=headers)
    dec_sign = packet.decrypt_sign(r.json()['sign'])

    # ## Print out Items from Database
    if 'items' in dec_sign:
        supportitems = []
        awakeningitems = []
        trainingitems = []
        potentialitems = []
        treasureitems = []
        carditems = []
        trainingfields = []
        stones = 0
        supportitemsset = set()
        awakeningitemsset = set()
        trainingitemsset = set()
        potentialitemsset = set()
        treasureitemsset = set()
        carditemsset = set()
        trainingfieldsset = set()
        print('Items:')
        print('-------------------------')
        if 'quest_clear_rewards' in dec_sign:
            for x in dec_sign['quest_clear_rewards']:
                if x['item_type'] == 'Point::Stone':
                    stones += x['amount']
        for x in dec_sign['items']:
            if x['item_type'] == 'SupportItem':

                # print('' + SupportItems.find(x['item_id']).name + ' x '+str(x['quantity']))

                for i in range(x['quantity']):
                    supportitems.append(x['item_id'])
                supportitemsset.add(x['item_id'])
            elif x['item_type'] == 'PotentialItem':

                # print('' + PotentialItems.find(x['item_id']).name + ' x '+str(x['quantity']))

                for i in range(x['quantity']):
                    potentialitems.append(x['item_id'])
                potentialitemsset.add(x['item_id'])
            elif x['item_type'] == 'TrainingItem':

                # print('' + TrainingItems.find(x['item_id']).name + ' x '+str(x['quantity']))

                for i in range(x['quantity']):
                    trainingitems.append(x['item_id'])
                trainingitemsset.add(x['item_id'])
            elif x['item_type'] == 'AwakeningItem':

                # print('' + AwakeningItems.find(x['item_id']).name + ' x '+str(x['quantity']))

                for i in range(x['quantity']):
                    awakeningitems.append(x['item_id'])
                awakeningitemsset.add(x['item_id'])
            elif x['item_type'] == 'TreasureItem':

                # print('' + TreasureItems.find(x['item_id']).name + ' x '+str(x['quantity']))

                for i in range(x['quantity']):
                    treasureitems.append(x['item_id'])
                treasureitemsset.add(x['item_id'])
            elif x['item_type'] == 'Card':

                # card = Cards.find(x['item_id'])

                carditems.append(x['item_id'])
                carditemsset.add(x['item_id'])
            elif x['item_type'] == 'Point::Stone':

#                print('' + card.name + '['+rarity+']'+ ' x '+str(x['quantity']))
                # print('' + TreasureItems.find(x['item_id']).name + ' x '+str(x['quantity']))

                stones += 1
            elif x['item_type'] == 'TrainingField':

                # card = Cards.find(x['item_id'])

                for i in range(x['quantity']):
                    trainingfields.append(x['item_id'])
                trainingfieldsset.add(x['item_id'])
            else:
                print(x['item_type'])
        for x in supportitemsset:
            print(Fore.CYAN + config.SupportItems.find(x).name + ' x' \
                + str(supportitems.count(x)))
        for x in awakeningitemsset:
            print(Fore.MAGENTA + config.AwakeningItems.find(x).name + ' x' \
                + str(awakeningitems.count(x)))
        for x in trainingitemsset:
            print(Fore.RED + config.TrainingItems.find(x).name + ' x' \
                + str(trainingitems.count(x)))
        for x in potentialitemsset:
            print(config.PotentialItems.find(x).name + ' x' \
                + str(potentialitems.count(x)))
        for x in treasureitemsset:
            print(Fore.GREEN + config.TreasureItems.find(x).name + ' x' \
                + str(treasureitems.count(x)))
        for x in trainingfieldsset:
            print(config.TrainingFields.find(x).name + ' x' \
                + str(trainingfields.count(x)))
        for x in carditemsset:
            print(config.Cards.find(x).name + ' x' + str(carditems.count(x)))
        print(Fore.YELLOW + Style.BRIGHT + 'Stones x' + str(stones))
    zeni = '{:,}'.format(dec_sign['zeni'])
    print('Zeni: ' + zeni)
    if 'gasha_point' in dec_sign:
        print('Friend Points: ' + str(dec_sign['gasha_point']))

    print('--------------------------')

    # Sell Cards

    i = 0
    card_list = []
    if 'user_items' in dec_sign:
        if 'cards' in dec_sign['user_items']:
            for x in dec_sign['user_items']['cards']:
                if config.Cards.find(x['card_id']).rarity == 0:
                    card_list.append(x['id'])
    
    if len(card_list)> 0:
        sell_cards(card_list)

    # ## Finish timing level

    timer_finish = int(round(time.time(), 0))
    timer_total = timer_finish - timer_start

    # #### COMPLETED STAGE

    print(Fore.GREEN + 'Completed stage: ' + str(stage_id) + ' in ' \
        + str(timer_total) + ' seconds')
    print('##############################################')


####################################################################
def get_friend(
    stage_id,
    difficulty,
    ):

    # Returns supporter for given stage_id & difficulty
    # Chooses cpu_supporter if possible

    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Authorization': packet.mac('GET', '/quests/' + stage_id
                                + '/supporters'),
        'Content-type': 'application/json',
        'X-Platform': 'config.platform',
        'X-AssetVersion': '////',
        'X-DatabaseVersion': '////',
        'X-ClientVersion': '////',
        }
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/quests/' + stage_id \
            + '/supporters'
    else:
        url = 'http://ishin-production.aktsk.jp/quests/' + stage_id \
            + '/supporters'
    
    r = requests.get(url, headers=headers)



    '''
    if 'supporters' not in r.json():
        print('Bandai has temp blocked connection... Attempting sign in...')
        response = SignIn(signup, AdId, UniqueId)
        RefreshClient()
        headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Authorization': GetMac('GET', '/quests/' + stage_id
                                + '/supporters', MacId, secret1),
        'Content-type': 'application/json',
        'X-Platform': config.platform,
        'X-AssetVersion': '////',
        'X-DatabaseVersion': '////',
        'X-ClientVersion': '////',
        }
        r = requests.get(url, headers=headers)
    '''
    #If CPU supporter available, choose it every time
    if 'cpu_supporters' in r.json():
        if int(difficulty) == 5:
            if 'super_hard3' in r.json()['cpu_supporters']:
                if len(r.json()['cpu_supporters']['super_hard3'
                       ]['cpu_friends']) > 0:
                    return {
                            'is_cpu' : True,
                            'id' : r.json()['cpu_supporters']['super_hard3']
                                           ['cpu_friends'][0]['id']
                            }
        if int(difficulty) == 4:
            if 'super_hard2' in r.json()['cpu_supporters']:
                if len(r.json()['cpu_supporters']['super_hard2'
                       ]['cpu_friends']) > 0:
                    return {
                            'is_cpu' : True,
                            'id' : r.json()['cpu_supporters']['super_hard2']
                                           ['cpu_friends'][0]['id']
                            }
        if int(difficulty) == 3:
            if 'super_hard1' in r.json()['cpu_supporters']:
                if len(r.json()['cpu_supporters']['super_hard1'
                       ]['cpu_friends']) > 0:
                    return {
                            'is_cpu' : True,
                            'id' : r.json()['cpu_supporters']['super_hard1']
                                           ['cpu_friends'][0]['id']
                            }
        if int(difficulty) == 2:
            if 'very_hard' in r.json()['cpu_supporters']:
                if len(r.json()['cpu_supporters']['very_hard'
                       ]['cpu_friends']) > 0:
                    return {
                            'is_cpu' : True,
                            'id' : r.json()['cpu_supporters']['very_hard']
                                           ['cpu_friends'][0]['id']
                            }
        if int(difficulty) == 1:
            if 'hard' in r.json()['cpu_supporters']:
                if len(r.json()['cpu_supporters']['hard']['cpu_friends'
                       ]) > 0:
                    return {
                            'is_cpu' : True,
                            'id' : r.json()['cpu_supporters']['hard']
                                           ['cpu_friends'][0]['id']
                            }
        if int(difficulty) == 0:
            if 'normal' in r.json()['cpu_supporters']:
                if len(r.json()['cpu_supporters']['normal'
                       ]['cpu_friends']) > 0:
                    return {
                            'is_cpu' : True,
                            'id' : r.json()['cpu_supporters']['normal']
                                           ['cpu_friends'][0]['id']
                            }

    return {
            'is_cpu' : False,
            'id' : r.json()['supporters'][0]['id']
           }
####################################################################
def refill_stamina():

    # ## Restore user stamina

    stones = get_user()['user']['stone']
    if stones < 1:
        print(Fore.RED + 'You have no stones left...')
        return 0
    if config.client == 'global':
        headers = {
            'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
            'Accept': '*/*',
            'Authorization': packet.mac('PUT', '/user/recover_act'),
            'Content-type': 'application/json',
            'X-Platform': config.platform,
            'X-AssetVersion': '////',
            'X-DatabaseVersion': '////',
            'X-ClientVersion': '////',
            }
        url = 'https://ishin-global.aktsk.com/user/recover_act'
    else:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
            'Accept': '*/*',
            'Authorization': packet.mac('PUT', '/user/recover_act_with_stone'),
            'Content-type': 'application/json',
            'X-Platform': config.platform,
            'X-AssetVersion': '////',
            'X-DatabaseVersion': '////',
            'X-ClientVersion': '////',
            }
        url = 'http://ishin-production.aktsk.jp/user/recover_act_with_stone'
    
    r = requests.put(url, headers=headers)
    print(Fore.GREEN + 'STAMINA RESTORED')
####################################################################
def get_user():

    # Returns user response from bandai

    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Authorization': packet.mac('GET', '/user'),
        'Content-type': 'application/json',
        'X-Platform': config.platform,
        'X-AssetVersion': '////',
        'X-DatabaseVersion': '////',
        'X-ClientVersion': '////',
        }
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/user'
    else:
        url = 'http://ishin-production.aktsk.jp/user'
    r = requests.get(url, headers=headers)
    return r.json()


####################################################################
def sell_cards(card_list):
    #Takes cards list and sells them in batches of 99

    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Authorization': packet.mac('POST', '/cards/sell'),
        'Content-type': 'application/json',
        'X-Platform': config.platform,
        'X-AssetVersion': '////',
        'X-DatabaseVersion': '////',
        'X-ClientVersion': '////',
        }
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/cards/sell'
    else:
        url = 'http://ishin-production.aktsk.jp/cards/sell'


    cards_to_sell = []
    i = 0
    for card in card_list:
        i += 1
        cards_to_sell.append(card)
        if i == 99:
            data = {'card_ids': cards_to_sell}
            r = requests.post(url, data=json.dumps(data), headers=headers)
            print('Sold Cards x' + str(len(cards_to_sell)))
            if 'error' in r.json():
                print(r.json()['error'])
                return 0
            i = 0
            cards_to_sell[:] = []
    if i != 0:
            data = {'card_ids': cards_to_sell}
            r = requests.post(url, data=json.dumps(data), headers=headers)
            print('Sold Cards x' + str(len(cards_to_sell)))
    #print(r.json())
    
####################################################################
def signup():

    # returns string identifier to be formatted and used by SignIn function
    config.AdId = packet.guid()['AdId']
    config.UniqueId = packet.guid()['UniqueId']
    user_acc = {
        'ad_id': config.AdId,
        'country': 'AU',
        'currency': 'AUD',
        'device': 'samsung',
        'device_model': 'SM-E7000',
        'os_version': '7.0',
        'platform': config.platform,
        'unique_id': config.UniqueId,
        }
    user_account = json.dumps({'user_account': user_acc})

    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Content-type': 'application/json',
        'X-Platform': config.platform,
        'X-ClientVersion': '////',
        }
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/auth/sign_up'
    else:
        url = 'http://ishin-production.aktsk.jp/auth/sign_up'
    r = requests.post(url, data=user_account, headers=headers)

    # ## It is now necessary to solve the captcha. Opens browser window
    # ## in order to solve it. Script waits for user input before continuing
    if 'captcha_url' not in r.json():
        print(Fore.RED+'Captcha could not be loaded...')
        return None

    url = r.json()['captcha_url']
    webbrowser.open(url, new=2)
    captcha_session_key = r.json()['captcha_session_key']
    print('Opening captcha in browser. Press'+ Fore.RED+' ENTER '+Style.RESET_ALL +'once you have solved it...')
    input()

    # ## Query sign up again passing the captcha session key.
    # ## Bandais servers check if captcha was solved relative to the session key

    data = {'captcha_session_key': captcha_session_key,
            'user_account': user_acc}
    
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/auth/sign_up'
    else:
        url = 'http://ishin-production.aktsk.jp/auth/sign_up'

    r = requests.post(url, data=json.dumps(data), headers=headers)

    # ##Return identifier for account, this changes upon transferring account
    try:
        return base64.b64decode(r.json()['identifier']).decode('utf-8')
    except:
        return None

####################################################################
####################################################################
def signin(identifier):
    # Takes account identifier and encodes it properly, sending BASIC Authorization
    # request to bandai.
    # Returns tuple

    # Format identifier to receive access_token and secret
    basic_pwacc = identifier.split(':')
    complete_string = basic_pwacc[1] + ':' + basic_pwacc[0]
    basic_accpw = 'Basic ' \
        + base64.b64encode(complete_string.encode('utf-8'
                           )).decode('utf-8')
    data = json.dumps({
                       'ad_id': packet.guid()['AdId'],
                       'unique_id': packet.guid()['UniqueId']
                      })

    # print(data)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Authorization': basic_accpw,
        'Content-type': 'application/json',
        'X-ClientVersion': '////',
        'X-Language': 'en',
        'X-UserCountry': 'AU',
        'X-UserCurrency': 'AUD',
        'X-Platform': config.platform,
        }
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/auth/sign_in'
    else:
        url = 'http://ishin-production.aktsk.jp/auth/sign_in'

    r = requests.post(url, data=data, headers=headers)

    if 'captcha_url' in r.json():
        print(r.json())
        url = r.json()['captcha_url']
        webbrowser.open(url, new=2)
        captcha_session_key = r.json()['captcha_session_key']
        print('Opening captcha in browser. Press'+ Fore.RED+' ENTER '+Style.RESET_ALL +'once you have solved it...')
        input()
        r = requests.post(url, data=data, headers=headers)

    print(Fore.RED + 'SIGN IN COMPLETE' + Style.RESET_ALL)

    try:
        return (r.json()['access_token'],r.json()['secret'])
    except:            
        return None

####################################################################
def get_transfer_code():
    # Returns transfer code in dictionary

    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Authorization': packet.mac('POST', '/auth/link_codes'),
        'Content-type': 'application/json',
        'X-Platform': config.platform,
        'X-AssetVersion': '////',
        'X-DatabaseVersion': '////',
        'X-ClientVersion': '////',
        }
    data = {'eternal': 1}
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/auth/link_codes'
    else:
        url = 'http://ishin-production.aktsk.jp/auth/link_codes'
    
    r = requests.post(url, data=json.dumps(data), headers=headers)
    try:
        print(r.json()['link_code'])
        return {'transfer_code' : r.json()['link_code']}
    except:
        return None
####################################################################
def tutorial():

    # ##Progress NULL TUTORIAL FINISH

    print(Fore.BLUE + 'Tutorial Progress: 1/8')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Authorization': packet.mac('PUT', '/tutorial/finish'),
        'Content-type': 'application/json',
        'X-Platform': config.platform,
        'X-AssetVersion': '////',
        'X-DatabaseVersion': '////',
        'X-ClientVersion': '////',
        }
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/tutorial/finish'
    else:
        url = 'http://ishin-production.aktsk.jp/tutorial/finish'
    r = requests.put(url, headers=headers)

    # ##Progress NULL Gasha

    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Authorization': packet.mac('POST', '/tutorial/gasha'),
        'Content-type': 'application/json',
        'X-Platform': config.platform,
        'X-AssetVersion': '////',
        'X-DatabaseVersion': '////',
        'X-ClientVersion': '////',
        }
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/tutorial/gasha'
    else:
        url = 'http://ishin-production.aktsk.jp/tutorial/gasha'
    r = requests.post(url, headers=headers)
    print(Fore.BLUE + 'Tutorial Progress: 2/8')

    # ##Progress to 999%

    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Authorization': packet.mac('PUT', '/tutorial'),
        'Content-type': 'application/json',
        'X-Platform': config.platform,
        'X-AssetVersion': '////',
        'X-DatabaseVersion': '////',
        'X-ClientVersion': '////',
        }
    progress = {'progress': '999'}
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/tutorial'
    else:
        url = 'http://ishin-production.aktsk.jp/tutorial'
    r = requests.put(url, data=json.dumps(progress), headers=headers)
    print(Fore.BLUE + 'Tutorial Progress: 3/8')

    # ##Change User name

    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Authorization': packet.mac('PUT', '/user'),
        'Content-type': 'application/json',
        'X-Platform': config.platform,
        'X-AssetVersion': '////',
        'X-DatabaseVersion': '////',
        'X-ClientVersion': '////',
        }
    user = {'user': {'name': 'Ninja'}}
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/user'
    else:
        url = 'http://ishin-production.aktsk.jp/user'
    r = requests.put(url, data=json.dumps(user), headers=headers)
    print(Fore.BLUE + 'Tutorial Progress: 4/8')

    # ##/missions/put_forward

    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Authorization': packet.mac('POST', '/missions/put_forward'),
        'Content-type': 'application/json',
        'X-Platform': config.platform,
        'X-AssetVersion': '////',
        'X-DatabaseVersion': '////',
        'X-ClientVersion': '////',
        }
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/missions/put_forward'
    else:
        url = 'http://ishin-production.aktsk.jp/missions/put_forward'
    r = requests.post(url, headers=headers)
    print(Fore.BLUE + 'Tutorial Progress: 5/8')

    # ##Apologies accept

    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Authorization': packet.mac('PUT', '/apologies/accept'),
        'Content-type': 'application/json',
        'X-Platform': config.platform,
        'X-AssetVersion': '////',
        'X-DatabaseVersion': '////',
        'X-ClientVersion': '////',
        }
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/apologies/accept'
    else:
        url = 'http://ishin-production.aktsk.jp/apologies/accept'
    r = requests.put(url, headers=headers)

    # ##On Demand

    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Authorization': packet.mac('PUT', '/user'),
        'Content-type': 'application/json',
        'X-Platform': config.platform,
        'X-AssetVersion': '////',
        'X-DatabaseVersion': '////',
        'X-ClientVersion': '////',
        }
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/user'
    else:
        url = 'http://ishin-production.aktsk.jp/user'
    data = {'user': {'is_ondemand': True}}
    r = requests.put(url, data=json.dumps(data), headers=headers)
    print(Fore.BLUE + 'Tutorial Progress: 6/8')

    # ##Hidden potential releasable

    print(Fore.BLUE + 'Tutorial Progress: 7/8')
    print(Fore.BLUE + 'Tutorial Progress: 8/8')
    print(Fore.RED + 'TUTORIAL COMPLETE')
####################################################################
def db_download():
    #
    jp_out_of_date = False
    glb_out_of_date = False
    #Check local DB versions
    while True:
        if os.path.isfile('help.txt'):
            f = open(os.path.join('help.txt'), 'r')
            local_version_glb = f.readline().rstrip()
            local_version_jp = f.readline().rstrip()
            f.close()
            break
        else:
            f = open(os.path.join('help.txt'), 'w')
            f.write('111\n')
            f.write('111\n')
            f.close()

    # Download each database.
    original_client = config.client

    # Set first db to download to global.
    config.client = 'global'
    config.identifier = signup()
    config.access_token,config.secret = signin(config.identifier)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Authorization': packet.mac('GET', '/client_assets/database'),
        'Content-type': 'application/json',
        'X-Platform': config.platform,
        'X-AssetVersion': '////',
        'X-DatabaseVersion': '////',
        'X-ClientVersion': '////',
        'X-Language': 'en',
        }
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/client_assets/database'
    else:
        url = 'http://ishin-production.aktsk.jp/client_assets/database'
    
    r = requests.get(url, allow_redirects=True,headers = headers)
    if local_version_glb != str(r.json()['version']):
        #print(Fore.RED + 'Downloading New '+ config.client.upper()+' Database Version...')
        glb_out_of_date = True
        glb_current = r.json()['version']
        

        print(Fore.RED + 'GLB DB out of date...')
        print(Fore.RED + 'Downloading...')
        url = r.json()['url']
        r = requests.get(url, allow_redirects=True)
        open('dataenc_glb.db', 'wb').write(r.content)


    # Set second db to download to jp.
    config.client = 'japan'
    config.identifier = signup()
    config.access_token,config.secret = signin(config.identifier)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Authorization': packet.mac('GET', '/client_assets/database'),
        'Content-type': 'application/json',
        'X-Platform': config.platform,
        'X-AssetVersion': '////',
        'X-DatabaseVersion': '////',
        'X-ClientVersion': '////',
        'X-Language': 'en',
        }
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/client_assets/database'
    else:
        url = 'http://ishin-production.aktsk.jp/client_assets/database'
    
    r = requests.get(url, allow_redirects=True,headers = headers)
    if local_version_jp != str(r.json()['version']):
        #print(Fore.RED + 'Downloading New '+ config.client.upper()+' Database Version...')
        jp_out_of_date = True
        jp_current = r.json()['version']
        
        print(Fore.RED + 'JP DB out of date...')
        print(Fore.RED + 'Downloading...')
        url = r.json()['url']
        r = requests.get(url, allow_redirects=True)
        open('dataenc_jp.db', 'wb').write(r.content)

    # Revert client to original
    config.client = original_client

    print(Fore.RED \
        + 'Decrypting Latest Databases... This can take a few minutes...')

    # ## Calling database decrypt script
    if glb_out_of_date:
        print('Decrypting Global Database')
        decryptor.main()
        with open('help.txt', 'r') as file:
            data = file.readlines()
            data[0] = str(glb_current) + '\n'
        with open('help.txt', 'w') as file:
            file.writelines(data)

    if jp_out_of_date:
        print('Decrypting JP Database')
        decryptor.main(p = '2db857e837e0a81706e86ea66e2d1633')
        with open('help.txt', 'r') as file:
            data = file.readlines()
            data[1] = str(jp_current) + '\n'
        with open('help.txt', 'w') as file:
            file.writelines(data)

    print(Fore.GREEN + 'Database update complete.')
####################################################################
def accept_missions():
    # Accept all remaining missions

    headers = {
               'User-Agent':'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
               'Accept':'*/*',
               'Authorization': packet.mac('GET', '/missions'),
               'Content-type' : 'application/json',
               'X-Platform' : config.platform,
               'X-AssetVersion' : '////',
               'X-DatabaseVersion' : '////',
               'X-ClientVersion' : '////'
               }
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/missions'
    else:
        url = 'http://ishin-production.aktsk.jp/missions'
    r = requests.get(url, headers = headers)
    missions = r.json()
    mission_list = []
    for mission in missions['missions']:
        if mission['completed_at']!= None and mission['accepted_reward_at'] == None:
            mission_list.append(mission['id'])

    headers = {
               'User-Agent':'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
               'Accept':'*/*',
               'Authorization': packet.mac('POST', '/missions/accept'),
               'Content-type' : 'application/json',
               'X-Platform' : config.platform,
               'X-AssetVersion' : '////',
               'X-DatabaseVersion' : '////',
               'X-ClientVersion' : '////'
               }
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/missions/accept'
    else:
        url = 'http://ishin-production.aktsk.jp/missions/accept'
    data = {"mission_ids":mission_list}
    r = requests.post(url, data = json.dumps(data),headers = headers)
    if 'error' not in r.json():
        print(Fore.GREEN+'Accepted missions')
####################################################################
def accept_gifts():

    # Gets Gift Ids

    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Authorization': packet.mac('GET', '/gifts'),
        'Content-type': 'application/json',
        'X-Platform': config.platform,
        'X-AssetVersion': '////',
        'X-DatabaseVersion': '////',
        'X-ClientVersion': '////',
        }
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/gifts'
    else:
        url = 'http://ishin-production.aktsk.jp/gifts'
    r = requests.get(url, headers=headers)
    
    gifts = []
    for x in r.json()['gifts']:
        gifts.append(x['id'])
    

    # AcceptGifts
    if len(gifts) == 0:
        print('No gifts to accept...')
        return 0
    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Authorization': packet.mac('POST', '/gifts/accept'),
        'Content-type': 'application/json',
        'X-Platform': config.platform,
        'X-AssetVersion': '////',
        'X-DatabaseVersion': '////',
        'X-ClientVersion': '////',
        }
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/gifts/accept'
    else:
        url = 'http://ishin-production.aktsk.jp/gifts/accept'

    chunks = [gifts[x:x+25] for x in range(0, len(gifts), 25)]
    for data in chunks:
        data = {'gift_ids': data}
        r = requests.post(url, data=json.dumps(data), headers=headers)
    if 'error' not in r.json():
        print(Fore.GREEN + 'Gifts Accepted...')
    else:
        print(r.json())

####################################################################
def change_team():
    ###Get user deck to change
    chosen_deck = int(input("Enter the deck number you would like to change: "))

    ###Get user cards
    print(Fore.BLUE + 'Fetching user cards...')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Authorization': packet.mac('GET', '/cards'),
        'Content-type': 'application/json',
        'X-Language': 'en',
        'X-Platform': config.platform,
        'X-AssetVersion': '////',
        'X-DatabaseVersion': '////',
        'X-ClientVersion': '////',
        }
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/cards'
    else:
        url = 'http://ishin-production.aktsk.jp/cards'
    r = requests.get(url, headers=headers)
    master_cards = r.json()['cards']
    print(Fore.GREEN + 'Done...')

    ###Sort user cards into a list of dictionaries with attributes
    print(Fore.BLUE + 'Fetching card attributes...')
    card_list = []
    for card in master_cards:
        ###Get card collection object from database 
        db_card = config.Cards.where('id','=',card['card_id']).first()

        ###Get card rarity
        if db_card.rarity == 0:
            rarity = 'N'
        elif db_card.rarity == 1:
            rarity = 'R'
        elif db_card.rarity == 2:
            rarity = 'SR'
        elif db_card.rarity == 3:
            rarity ='SSR'
        elif db_card.rarity == 4:
            rarity = 'UR'
        elif db_card.rarity == 5:
            rarity = 'LR'
        ###Get card Type
        if str(db_card.element)[-1] == '0':
            type ='[AGL] '
        elif str(db_card.element)[-1] == '1':
            type ='[TEQ] '
        elif str(db_card.element)[-1] == '2':
            type ='[INT] '
        elif str(db_card.element)[-1] == '3':
            type ='[STR] '
        elif str(db_card.element)[-1] == '4':
            type ='[PHY] '
        ###Get card categories list
        categories = []
        #Get category id's given card id
        card_card_categories = config.CardCardCategories.where(
                               'card_id','=',db_card.id).get()
                
        try:
            for category in card_card_categories:
                categories.append(config.CardCategories.find(
                                  category.card_category_id).name)
        except:
            None
        ###Get card link_skills list
        link_skills = []
        try:
            link_skills.append(config.LinkSkills.find(db_card.link_skill1_id).name)
        except:
            None
        try:
            link_skills.append(config.LinkSkills.find(db_card.link_skill2_id).name)
        except:
            None
        try:
            link_skills.append(config.LinkSkills.find(db_card.link_skill3_id).name)
        except:
            None
        try:
            link_skills.append(config.LinkSkills.find(db_card.link_skill4_id).name)
        except:
            None
        try:
            link_skills.append(config.LinkSkills.find(db_card.link_skill5_id).name)
        except:
            None
        try:
            link_skills.append(config.LinkSkills.find(db_card.link_skill6_id).name)
        except:
            None
        try:
            link_skills.append(config.LinkSkills.find(db_card.link_skill7_id).name)
        except:
            None

        dict = {
                'ID': db_card.id,
                'Rarity': rarity,
                'Name': db_card.name,
                'Type': type,
                'Cost': db_card.cost,
                'Hercule': db_card.is_selling_only,
                'HP': db_card.hp_init,
                'Categories':categories,
                'Links':link_skills,
                'UniqueID': card['id']
                }
        card_list.append(dict)
    print(Fore.GREEN + "Done...")

    ###Sort cards
    print(Fore.BLUE + "Sorting cards...")
    card_list = sorted(card_list, key=lambda k: k['Name'])
    card_list = sorted(card_list, key=lambda k: k['Rarity'])
    card_list = sorted(card_list, key=lambda k: k['Cost'])
    print(Fore.GREEN + "Done...")

    ###Define cards to display
    cards_to_display_dicts = []
    cards_to_display = []
    #Take cards in card_list that aren't hercule statues or kais?
    for char in card_list:
        if char['Hercule'] != 1 and char['HP'] > 5:
            cards_to_display_dicts.append(char)
            cards_to_display.append(char['Type'] + char['Rarity']+ ' ' +char['Name'] + ' | ' + str(char['ID']) + ' | '+ str(char['UniqueID']))

    ###Define links to display
    links_master = []
    for link in config.LinkSkills.all():
        links_master.append(link.name)
    
    links_to_display = sorted(links_master)

    ###Define categories to display
    categories_master = []
    for category in config.CardCategories.all():
        categories_master.append(category.name)
    
    categories_to_display = sorted(categories_master)

    ###Define window layout

    col1 = [[sg.Listbox(values=(cards_to_display),size = (30,20),key='CARDS')],
            [sg.Listbox(values=([]),size = (30,6),key = 'CARDS_CHOSEN')],
            [sg.Button(button_text = 'Choose Card',key='choose_card'),
             sg.Button(button_text='Confirm Team',key='confirm_team')]]

    col2 = [[sg.Listbox(values=(sorted(categories_to_display)),size = (25,20),key = 'CATEGORIES')],
            [sg.Listbox(values=([]),size = (25,6),key = 'CATEGORIES_CHOSEN')],
            [sg.Button(button_text ='Choose Categories',key='choose_categories'),
             sg.Button(button_text ='Clear Categories',key='clear_categories')]]

    col3 = [[sg.Listbox(values=(sorted(links_to_display)),size = (25,20),key='LINKS')],
            [sg.Listbox(values=([]),size = (25,6),key = 'LINKS_CHOSEN')],
            [sg.Button(button_text ='Choose Links',key='choose_links'),
             sg.Button(button_text ='Clear Links',key='clear_links')]]

    layout = [[sg.Column(col1),sg.Column(col2),sg.Column(col3)]]
    window = sg.Window('Deck Update',grab_anywhere=True,keep_on_top = True).Layout(layout)
    

    ###Begin window loop
    chosen_links = []
    chosen_categories = []

    ###
    chosen_cards_ids = []
    chosen_cards_unique_ids = []
    chosen_cards_names = []
    chosen_cards_to_display = []

    while len(chosen_cards_ids) < 6:
        event,values = window.Read()

        if event == None:
            return 0
        
        if event == 'choose_card':
            if len(values['CARDS']) < 1:
                continue
            #Get ID of chosen card to send to bandai
            chosen_line = values['CARDS'][0]
            char_name,char_id,char_unique_id = chosen_line.split(' | ')
            chosen_cards_ids.append(int(char_id))
            chosen_cards_unique_ids.append(int(char_unique_id))
            chosen_cards_names.append(config.Cards.find(char_id).name)

            #Chosen cards to display in lower box
            chosen_cards_to_display.append(chosen_line)

        if event == 'choose_categories':
            for category in values['CATEGORIES']:
                chosen_categories.append(category)
                categories_to_display.remove(category)

        if event == 'clear_categories':
            categories_to_display.extend(chosen_categories)
            chosen_categories[:] = []
            categories_to_display = sorted(categories_to_display)
            

        if event == 'choose_links':
            for link in values['LINKS']:
                chosen_links.append(link)
                links_to_display.remove(link)

        if event == 'clear_links':
            links_to_display.extend(chosen_links)
            chosen_links[:] = []
            links_to_display = sorted(links_to_display)
        
        if event == 'confirm_team':
            if len(chosen_cards_unique_ids) < 6:
                if len(chosen_cards_unique_ids) == 0:
                    print(Fore.RED+'No cards selected.')
                    return 0
                loop = 6 - len(chosen_cards_unique_ids)
                for i in range(int(loop)):
                    chosen_cards_unique_ids.append('0')
                break


        ###Re-populate cards to display, checking filter criteria
        cards_to_display[:] = []
        for char in cards_to_display_dicts:
            if char['Name'] in chosen_cards_names:
                continue

            if len(list(set(chosen_links) & set(char['Links']))) != len(chosen_links):
                #print("List intersection")
                continue

            if len(list(set(chosen_categories) & set(char['Categories']))) != len(chosen_categories):
                #print("Category intersectino")
                continue

            cards_to_display.append(char['Type'] + char['Rarity']+ ' ' +char['Name'] + ' | ' + str(char['ID']) + ' | '+ str(char['UniqueID']))


        ###Update window elements
        window.FindElement('CARDS').Update(values=cards_to_display)
        window.FindElement('CARDS_CHOSEN').Update(values=chosen_cards_to_display)
        window.FindElement('CATEGORIES').Update(values=categories_to_display)
        window.FindElement('CATEGORIES_CHOSEN').Update(values=chosen_categories)
        window.FindElement('LINKS').Update(values=links_to_display)
        window.FindElement('LINKS_CHOSEN').Update(values=chosen_links)

    window.Close()
    ###Send selected team to bandai
    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Authorization': packet.mac('POST', '/teams'),
        'Content-type': 'application/json',
        'X-Platform': config.platform,
        'X-AssetVersion': '////',
        'X-DatabaseVersion': '////',
        'X-ClientVersion': '////',
        }
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/teams'
    else:
        url = 'http://ishin-production.aktsk.jp/cards/teams'
    #print(chosen_cards_unique_ids)
    data = {'selected_team_num': 1, 'user_card_teams': [
        {'num': chosen_deck, 'user_card_ids': chosen_cards_unique_ids},
        ]}
    #print(data)
    r = requests.post(url, data = json.dumps(data),headers = headers)
    if 'error' in r.json():
        print(Fore.RED+str(r.json()))
    else:
        #print(r.json())
        print(chosen_cards_names)
        print(Fore.GREEN+"Deck updated!")

    return 0

####################################################################
def get_kagi_id(stage):
    # return kagi ID to use for a stage

    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Authorization': packet.mac('GET', '/eventkagi_items'),
        'Content-type': 'application/json',
        'X-Platform': config.platform,
        'X-AssetVersion': '////',
        'X-DatabaseVersion': '////',
        'X-ClientVersion': '////',
        }
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/eventkagi_items'
    else:
        url = 'http://ishin-production.aktsk.jp/eventkagi_items'
    r = requests.get(url, headers=headers)

    kagi_items = r.json()['eventkagi_items']
    area_id = config.Quests.find(stage).area_id
    area_category = config.Area.find(area_id).category
    areatabs = config.AreaTabs.all()
    for tab in areatabs:
        j = json.loads(tab.area_category_ids)
        if area_category in j['area_category_ids']:
            kagi_id = int(tab.id)
            print('Kagi ID: ' + str(tab.id))
            break
    for kagi in kagi_items:
        if kagi['eventkagi_item_id'] == kagi_id:
            if kagi['quantity'] > 0:
                print('kagi_id' + kagi_id)
                return kagi_id
            else:
                return None

    return None
####################################################################

def complete_unfinished_quest_stages():
    # ## Will eventually use this to streamline stuff
    # type: (object, object) -> object

    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Authorization': packet.mac('GET', '/user_areas'),
        'Content-type': 'application/json',
        'X-Language': 'en',
        'X-Platform': config.platform,
        'X-AssetVersion': '////',
        'X-DatabaseVersion': '////',
        'X-ClientVersion': '////',
        }
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/user_areas'
    else:
        url = 'http://ishin-production.aktsk.jp/user_areas'
    r = requests.get(url, headers=headers)

    maps = []
    for user in r.json()['user_areas']:
        for map in user['user_sugoroku_maps']:
            if map['cleared_count'] == 0 and map['sugoroku_map_id'] < 999999 and map['sugoroku_map_id'] > 100:
                maps.append(map)

    if len(maps) == 0:
        print("No quests to complete!")
        print('--------------------------------------------')
        return 0

    i = 0
    while i == 0:
        #print(maps)
        for map in maps:
            complete_stage(str(map['sugoroku_map_id'])[:-1], str(map['sugoroku_map_id'])[-1])

        headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Authorization': packet.mac('GET', '/user_areas'),
        'Content-type': 'application/json',
        'X-Language': 'en',
        'X-Platform': config.platform,
        'X-AssetVersion': '////',
        'X-DatabaseVersion': '////',
        'X-ClientVersion': '////',
        }
        r = requests.get(url, headers=headers)
        maps_check = []
        #print(r.json())
        for user in r.json()['user_areas']:
            for map in user['user_sugoroku_maps']:
                if map['cleared_count'] == 0 and map['sugoroku_map_id'] < 999999 and map['sugoroku_map_id'] > 100:
                    maps_check.append(map)
        if maps_check == maps:
            i = 1
        else:
            maps = maps_check
            refresh_client()
    return 1
####################################################################
def refresh_client():
    config.access_token,config.secret = signin(config.identifier)
    print(Fore.GREEN+'Refreshed Token')
####################################################################
def change_name():
    # Changes name associated with account
    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Authorization': packet.mac('PUT', '/user'),
        'Content-type': 'application/json',
        'X-Platform': config.platform,
        'X-AssetVersion': '////',
        'X-DatabaseVersion': '////',
        'X-ClientVersion': '////',
        }
    name = input('What would you like to change your name to?: ')
    user = {'user': {'name': name}}
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/user'
    else:
        url = 'http://ishin-production.aktsk.jp/user'
    r = requests.put(url, data=json.dumps(user), headers=headers)
    if 'error' in r.json():
        print(r.json())
    else:
        print("Name changed to: "+name)
####################################################################
def increase_capacity():

    # ## Increases account card capacity by 5 every time it is called

    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Authorization': packet.mac('POST', '/user/capacity/card'),
        'Content-type': 'application/json',
        'X-Platform': config.platform,
        'X-AssetVersion': '////',
        'X-DatabaseVersion': '////',
        'X-ClientVersion': '////',
        }
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/user/capacity/card'
    else:
        url = 'http://ishin-production.aktsk.jp/user/capacity/card'
    
    r = requests.post(url, headers=headers)
    if 'error' in r.json():
        print(Fore.RED + str(r.json()))
    else:
        print(Fore.GREEN + 'Card capacity +5')
####################################################################

def get_user_info():

    # ## Returns User dictionary and info

    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Authorization': packet.mac('GET', '/user'),
        'Content-type': 'application/json',
        'X-Platform': config.platform,
        'X-AssetVersion': '////',
        'X-DatabaseVersion': '////',
        'X-ClientVersion': '////',
        }
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/user'
    else:
        url = 'http://ishin-production.aktsk.jp/user'
    r = requests.get(url, headers=headers)
    user = r.json()

    print('Account OS: '+config.platform.upper())
    print('User ID: ' + str(user['user']['id']))
    print('Stones: ' + str(user['user']['stone']))
    print('Zeni: ' + str(user['user']['zeni']))
    print('Rank: ' + str(user['user']['rank']))
    print('Stamina: ' + str(user['user']['act']))
    print('Name: ' + str(user['user']['name']))
    print('Total Card Capacity: ' + str(user['user']['total_card_capacity']))
####################################################################
def complete_unfinished_events():
    # ## Will eventually use this to streamline stuff
    # type: (object, object) -> object
    ### Get current event IDs
    # ## Gets current events json which contains some useful data

    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Authorization': packet.mac('GET', '/events'),
        'Content-type': 'application/json',
        'X-Language': 'en',
        'X-Platform': config.platform,
        'X-AssetVersion': '////',
        'X-DatabaseVersion': '////',
        'X-ClientVersion': '////',
        }
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/events'
    else:
        url = 'http://ishin-production.aktsk.jp/events'
    r = requests.get(url, headers=headers)
    events = r.json()
    event_ids = []
    for event in events['events']:
        event_ids.append(event['id'])
    event_ids = sorted(event_ids)
    try:
        event_ids.remove(135)
    except:
        None

    ### Complete areas if they are in the current ID pool
    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Authorization': packet.mac('GET', '/user_areas'),
        'Content-type': 'application/json',
        'X-Language': 'en',
        'X-Platform': config.platform,
        'X-AssetVersion': '////',
        'X-DatabaseVersion': '////',
        'X-ClientVersion': '////',
        }
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/user_areas'
    else:
        url = 'http://ishin-production.aktsk.jp/user_areas'
    r = requests.get(url, headers=headers)
    areas = r.json()['user_areas']
    i = 1
    for area in areas:
        if area['area_id'] in event_ids:
            for stage in area['user_sugoroku_maps']:
                if stage['cleared_count'] == 0:
                    complete_stage(str(stage['sugoroku_map_id'])[:-1], str(stage['sugoroku_map_id'])[-1])
                    i+=1
        if i % 30 == 0:
            refresh_client()
####################################################################
def complete_clash():
    print('Fetching current clash...')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Authorization': packet.mac('GET', '/resources/home?rmbattles=true'),
        'X-Language': 'en',
        'Content-type': 'application/json',
        'X-Platform': config.platform,
        'X-AssetVersion': '////',
        'X-DatabaseVersion': '////',
        'X-ClientVersion': '////',
        }
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/resources/home?rmbattles=true'
    else:
        url = 'http://ishin-production.aktsk.jp/resources/home?rmbattles=true'
    r = requests.get(url, headers=headers)
    clash_id = r.json()['rmbattles']['id']

    #### dropout
    print('Resetting clash to beginning...')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Authorization': packet.mac('POST', '/rmbattles/'+str(clash_id)+'/stages/dropout'),
        'Content-type': 'application/json',
        'X-Platform': config.platform,
        'X-AssetVersion': '////',
        'X-DatabaseVersion': '////',
        'X-ClientVersion': '////',
        }
    sign = {
        'reason': "dropout"
    }
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/rmbattles/'+str(clash_id)+'/stages/dropout'
    else:
        url = 'http://ishin-production.aktsk.jp/rmbattles/'+str(clash_id)+'/stages/dropout'
    
    r = requests.post(url, data=json.dumps(sign), headers=headers)
    print('Reset complete...')

    print('Fetching list of stages from Bandai...')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Authorization': packet.mac('GET', '/rmbattles/'+str(clash_id)),
        'X-Language': 'en',
        'Content-type': 'application/json',
        'X-Platform': config.platform,
        'X-AssetVersion': '////',
        'X-DatabaseVersion': '////',
        'X-ClientVersion': '////',
        }
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/rmbattles/'+str(clash_id)
    else:
        url = 'http://ishin-production.aktsk.jp/rmbattles/'+str(clash_id)
    
    r = requests.get(url, headers=headers)

    available_stages = []
    for area in r.json()['level_stages'].values():
        for stage in area:
            available_stages.append(stage['id'])
    print('Stages obtained...')
    print('Asking Bandai for available cards...')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Authorization': packet.mac('GET', '/rmbattles/available_user_cards'),
        'X-Language': 'en',
        'Content-type': 'application/json',
        'X-Platform': config.platform,
        'X-AssetVersion': '////',
        'X-DatabaseVersion': '////',
        'X-ClientVersion': '////',
        }
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/rmbattles/available_user_cards'
    else:
        url = 'http://ishin-production.aktsk.jp/rmbattles/available_user_cards'
    
    r = requests.get(url, headers=headers)
    print('Cards received...')
    available_user_cards = []
    #print(r.json())
    for card in r.json():
        available_user_cards.append(card)
    available_user_cards= available_user_cards[:99]

    if len(available_user_cards) == 0:
        print(Fore.RED+"Not enough cards to complete Battlefield with!")
        return 0


    is_beginning = True
    #print(available_stages)
    print('Sending Bandai full team...')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Authorization': packet.mac('PUT', '/rmbattles/teams/1'),
        'X-Language': 'en',
        'Content-type': 'application/json',
        'X-Platform': config.platform,
        'X-AssetVersion': '////',
        'X-DatabaseVersion': '////',
        'X-ClientVersion': '////',
        }
    data = {'user_card_ids': available_user_cards}
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/rmbattles/teams/1'
    else:
        url = 'http://ishin-production.aktsk.jp/rmbattles/teams/1'
    
    r = requests.put(url, data=json.dumps(data), headers=headers)
    print('Sent!')
    print('')
    print('Commencing Ultimate Clash!')
    print('----------------------------')
    for stage in available_stages:
        leader = available_user_cards[0]
        members = available_user_cards[1]
        sub_leader = available_user_cards[2]

        sign = {
            'is_beginning': is_beginning,
            'user_card_ids':{
            'leader': leader,
            'members': members,
            'sub_leader': sub_leader
                }
            }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
            'Accept': '*/*',
            'Authorization': packet.mac('POST', '/rmbattles/'+str(clash_id)+'/stages/'+str(stage)+'/start'),
            'Content-type': 'application/json',
            'X-Platform': config.platform,
            'X-AssetVersion': '////',
            'X-DatabaseVersion': '////',
            'X-ClientVersion': '////',
            }
        if config.client == 'global':
            url = 'https://ishin-global.aktsk.com/rmbattles/'+str(clash_id)+'/stages/'+str(stage)+'/start'
        else:
            url = 'http://ishin-production.aktsk.jp/rmbattles/'+str(clash_id)+'/stages/'+str(stage)+'/start'
        
        r = requests.post(url, data=json.dumps(sign), headers=headers)
        print('Commencing Stage '+Fore.YELLOW+str(stage))

        is_beginning = False

        ###Second request
        finish_time = int(round(time.time(), 0)+2000)
        start_time = finish_time - randint(40000000, 50000000)
        if 'sign' in r.json():
            dec_sign = decrypt_sign(r.json()['sign'])
        enemy_hp = 0
        try:
            for enemy in dec_sign['enemies']:
                enemy_hp += enemy[0]['hp']
        except:
            print('nah')

        sign = {
            'damage' : enemy_hp,
            'finished_at_ms': finish_time,
            'finished_reason':'win',
            'is_cleared':True,
            'remaining_hp':0,
            'round':0,
            'started_at_ms':start_time,
            'token': dec_sign['token']
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
            'Accept': '*/*',
            'Authorization': packet.mac('POST', '/rmbattles/'+str(clash_id)+'/stages/finish'),
            'Content-type': 'application/json',
            'X-Platform': config.platform,
            'X-AssetVersion': '////',
            'X-DatabaseVersion': '////',
            'X-ClientVersion': '////',
            }
        if config.client == 'global':
            url = 'https://ishin-global.aktsk.com/rmbattles/'+str(clash_id)+'/stages/finish'
        else:
            url = 'http://ishin-production.aktsk.jp/rmbattles/'+str(clash_id)+'/stages/finish'
        
        r = requests.post(url, data=json.dumps(sign), headers=headers)
        print('Completed Stage '+Fore.YELLOW+str(stage))


        headers = {
            'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
            'Accept': '*/*',
            'Authorization': packet.mac('GET', '/rmbattles/teams/1'),
            'X-Language': 'en',
            'Content-type': 'application/json',
            'X-Platform': config.platform,
            'X-AssetVersion': '////',
            'X-DatabaseVersion': '////',
            'X-ClientVersion': '////',
            }
        if config.client == 'global':
            url = 'https://ishin-global.aktsk.com/rmbattles/teams/1'
        else:
            url = 'http://ishin-production.aktsk.jp/rmbattles/teams/1'
        
        r = requests.get(url, headers=headers)
        print('----------------------------')
        if 'sortiable_user_card_ids' not in r.json():
            return 0
        available_user_cards = r.json()['sortiable_user_card_ids']

####################################################################
def complete_area(area_id):
    # completes all stages and difficulties of a given area.

    quests = config.Quests.where('area_id', '=', area_id).get()
    total = 0
    for quest in quests:
        sugorokus = config.Sugoroku.where('quest_id', '=', quest.id).get()
        total += len(sugorokus)
    i = 1
    for quest in quests:
        sugorokus = config.Sugoroku.where('quest_id', '=', quest.id).get()
        difficulties = []
        for sugoroku in sugorokus:
            print('Completion of area: ' + str(i) + '/' + str(total))
            complete_stage(str(quest.id),sugoroku.difficulty)
            i += 1
####################################################################
def save_account():
    if not os.path.isdir("Saves"):
        try: 
            os.mkdir('Saves')
            os.mkdir('Saves/android')
            os.mkdir('Saves/ios')
        except:
            print(Fore.RED + 'Unable to create saves file')
            return 0

    valid_save = False
    while valid_save == False:
        save_name = input("What would you like to name the file?")
        while save_name.isalnum() == 0:
            print(Fore.RED+"Name not allowed!")
            save_name = input('What would you like to name this save?: ')
        if os.path.exists('Saves'+os.sep+config.platform+os.sep+save_name):
            print(Fore.RED + "File by that name already exists.")
        else:
            try:
                f = open(os.path.join('Saves'+os.sep+config.platform+os.sep+save_name), 'w')
                f.write(str(config.identifier) + '\n')
                f.write(str(config.AdId) + '\n')
                f.write(str(config.UniqueId) + '\n')
                f.write(str(config.platform) + '\n')
                f.write(str(config.client) + '\n')
                f.close()
                print('--------------------------------------------')
                print(Fore.BLUE + 'Written details to file: ' + save_name)
                print(Fore.RED + 'If ' + save_name + ' is deleted your account will be lost!')
                print('--------------------------------------------')
                break
            except Exception as e:
                print(e)
####################################################################
def load_account():

    while 1==1:
        platform = input("'a'|Android -- 'i'|iOS: ")
        if platform[0].lower() in ['a','i']:
            if platform[0].lower() == 'a':
                config.platform = 'android'
            else:
                config.platform = 'ios'
            break
        else:
            print(Fore.RED+'Could not identify correct platform to use.')

    while 1==1:
        save_name = input("What save would you like to load?: ")
        if os.path.isfile('Saves'+os.sep+config.platform+os.sep+save_name):
            try:
                f = open(os.path.join('Saves',config.platform, save_name), 'r')
                config.identifier = f.readline().rstrip()
                config.AdId = f.readline().rstrip()
                config.UniqueId = f.readline().rstrip()
                config.platform = f.readline().rstrip()
                client = f.readline().rstrip()
                if config.client == client:
                    break
                else:
                    print(Fore.RED+'Save does not match client version.')

            except Exception as e:
                print(e)
            
        else:
            print(Fore.RED + "Could not find "+save_name)
    refresh_client()
####################################################################

def daily_login():

    # ## Accepts Outstanding Login Bonuses
    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Authorization': packet.mac('GET', '/resources/home?apologies=true&banners=true&bonus_schedules=true&budokai=true&comeback_campaigns=true&gifts=true&login_bonuses=true&rmbattles=true'),
        'X-Language': 'en',
        'Content-type': 'application/json',
        'X-Platform': config.platform,
        'X-AssetVersion': '////',
        'X-DatabaseVersion': '////',
        'X-ClientVersion': '////',
        }
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/resources/home?apologies=true&banners=true&bonus_schedules=true&budokai=true&comeback_campaigns=true&gifts=true&login_bonuses=true&rmbattles=true'
    else:
        url = 'http://ishin-production.aktsk.jp/resources/home?apologies=true&banners=true&bonus_schedules=true&budokai=true&comeback_campaigns=true&gifts=true&login_bonuses=true&rmbattles=true'
    r = requests.get(url, headers=headers)
    if 'error' in r.json():
        print(r.json())

    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Authorization': packet.mac('POST', '/login_bonuses/accept'),
        'Content-type': 'application/json',
        'X-Platform': config.platform,
        'X-AssetVersion': '////',
        'X-DatabaseVersion': '////',
        'X-ClientVersion': '////',
        }
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/login_bonuses/accept'
    else:
        url = 'http://ishin-production.aktsk.jp/login_bonuses/accept'

    r = requests.post(url, headers=headers)
    if 'error' in r.json():
        print(r.json())
####################################################################
def dragonballs():
    is_got = 0
    ###Check for Dragonballs
    headers = {
                'User-Agent':'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
                'Accept':'*/*',
                'Authorization': packet.mac('GET', '/dragonball_sets'),
                'Content-type' : 'application/json',
                'X-Language':'en',
                'X-Platform' : config.platform,
                'X-AssetVersion' : '////',
                'X-DatabaseVersion' : '////',
                'X-ClientVersion' : '////'
              }
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/dragonball_sets'
    else:
        url = 'http://ishin-production.aktsk.jp/dragonball_sets'
    r = requests.get(url, headers = headers)
    if 'error' in r.json():
        print(Fore.RED+str(r.json()))
        return 0

    ####Determine which dragonball set is being used
    set = r.json()['dragonball_sets'][0]['id']

    ### Complete stages and count dragonballs
    for dragonball in r.json()['dragonball_sets']:
        for db in reversed(dragonball['dragonballs']):
            if db['is_got'] == True:
                is_got += 1
            elif db['is_got'] == False:
                is_got += 1
                complete_stage(str(db['quest_id']),db['difficulties'][0])

    ### If all dragonballs found then wish
    if is_got == 7:
        headers = {
                    'User-Agent':'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
                    'Accept':'*/*',
                    'Authorization': packet.mac('GET', '/dragonball_sets/'+str(set)+'/wishes'),
                    'Content-type' : 'application/json',
                    'X-Language':'en',
                    'X-Platform' : config.platform,
                    'X-AssetVersion' : '////',
                    'X-DatabaseVersion' : '////',
                    'X-ClientVersion' : '////'
                  }
        if config.client == 'global':
            url = 'https://ishin-global.aktsk.com/dragonball_sets/'+str(set)+'/wishes'
        else:
            url = 'http://ishin-production.aktsk.jp/dragonball_sets/'+str(set)+'/wishes'

        r = requests.get(url, headers = headers)
        if 'error' in r.json():
            print(Fore.RED+str(r.json()))
            return 0
        wish_ids = []
        for wish in r.json()['dragonball_wishes']:
            if wish['is_wishable']:
                print('#########################')
                print('Wish ID: ' + str(wish['id']))
                wish_ids.append(str(wish['id']))
                print(wish['title'])
                print(wish['description'])
                print('')

        print(Fore.YELLOW+'What wish would you like to ask shenron for? ID: ', end='')
        choice = input()
        while choice not in wish_ids:
            print("Shenron did not understand you! ID: ",end='')
            choice = input()
        wish_ids[:] = []
        headers = {
                'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
                'Accept': '*/*',
                'Authorization': packet.mac('POST', '/dragonball_sets/'+str(set)+'/wishes'),
                'Content-type': 'application/json',
                'X-Platform': config.platform,
                'X-AssetVersion': '////',
                'X-DatabaseVersion': '////',
                'X-ClientVersion': '////',
                }
        if config.client == 'global':
            url = 'https://ishin-global.aktsk.com/dragonball_sets/'+str(set)+'/wishes'
        else:
            url = 'http://ishin-production.aktsk.jp/dragonball_sets/'+str(set)+'/wishes'
        data = {'dragonball_wish_ids': [int(choice)]}
        r = requests.post(url, data=json.dumps(data), headers=headers)
        if 'error' in r.json():
            print(Fore.RED+str(r.json()))
        else:
            print(Fore.YELLOW+'Wish granted!')
            print('')

        dragonballs()

        return 0
####################################################################
def transfer_account():
    transfercode = input('Enter your transfer code: ')

    config.AdId = packet.guid()['AdId']
    config.UniqueId = packet.guid()['UniqueId']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
        'Accept': '*/*',
        'Content-type': 'application/json',
        'X-Platform': config.platform,
        'X-AssetVersion': '////',
        'X-DatabaseVersion': '////',
        'X-ClientVersion': '////',
        }
    data = {'eternal': True, 'old_user_id': '', 'user_account': {
        'device': 'samsung',
        'device_model': 'SM-E7000',
        'os_version': '7.0',
        'platform': config.platform,
        'unique_id': config.UniqueId,
        }}
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/auth/link_codes/' \
        + str(transfercode)
    else:
        url = 'http://ishin-production.aktsk.jp/auth/link_codes/' \
        + str(transfercode)
    print('URL: ' + url)
    r = requests.put(url, data=json.dumps(data), headers=headers)
    if 'error' in r.json():
        print(r.json())
    print(base64.b64decode(r.json()['identifiers']).decode('utf-8'))
    config.identifier = base64.b64decode(r.json()['identifiers']).decode('utf-8')

    save_account()
    refresh_client()
####################################################################
def user_command_executor(command):
    if ',' in command:
            command = command.replace(" ", "")
            command = command.replace(",", "\n")
            s = io.StringIO(command+'\n')
            sys.stdin = s
            command = input()

    if command == 'help':
        if os.path.exists('help.txt'):
            f = open(os.path.join('help.txt'), 'r')
            help_text = f.read()
            print(help_text)
        else:
            print(Fore.RED+'help.txt does not exist.')
    elif command == 'stage':
        stage = input('What stage would you like to complete?: ')
        difficulty = input('Enter the difficulty|(0:Easy, 1:Hard etc...): ')
        loop = input('Enter how many times to execute: ')
        for i in range(int(loop)):
            complete_stage(stage,difficulty)
    elif command == 'area':
        area = input('Enter the area to complete: ')
        loop  = input('How many times to complete the entire area: ')
        for i in range(int(loop)):
            complete_area(area)
    elif command == 'gift':
        accept_gifts()
        accept_missions()
    elif command == 'omegafarm':
        accept_gifts()
        accept_missions()
        complete_unfinished_quest_stages()
        complete_unfinished_events()
        complete_unfinished_zbattles()
        complete_clash()
    ## When this will get updated, we shall add :finishzbattle,30, + sell + sellhercule + baba(?)
    elif command == 'completequests':
        complete_unfinished_quest_stages()
    elif command == 'completeevents':
        complete_unfinished_events()
    elif command == 'completezbattles':
        complete_unfinished_zbattles()
    elif command == 'clash':
        complete_clash()
    elif command == 'dragonballs':
        dragonballs()
    elif command == 'info':
        get_user_info()
    elif command == 'team':
        change_team()
    elif command == 'transfer':
        get_transfer_code()
    elif command == 'capacity':
        increase_capacity()
    elif command == 'name':
        change_name()
    else:
        print('Command not found.')

####################################################################
def complete_unfinished_zbattles(kagi = False):
    headers = {
            'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
            'Accept': '*/*',
            'Authorization': packet.mac('GET', '/events'),
            'Content-type': 'application/json',
            'X-Language': 'en',
            'X-Platform': config.platform,
            'X-AssetVersion': '////',
            'X-DatabaseVersion': '////',
            'X-ClientVersion': '////',
            }
    if config.client == 'global':
        url = 'https://ishin-global.aktsk.com/events'
    else:
        url = 'http://ishin-production.aktsk.jp/events'
    r = requests.get(url, headers=headers)
    events = r.json()
    try:
        for event in events['z_battle_stages']:
            print(config.ZBattles.where('z_battle_stage_id','=',event['id']).first().enemy_name,end='')
            print(Fore.BLUE+' | ID: ' + str(event['id']))
            # Get Max cleared level
            headers = {
                'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
                'Accept': '*/*',
                'Authorization': packet.mac('GET', '/z_battles/'+str(event['id'])+'/rankings'),
                'Content-type': 'application/json',
                'X-Platform': config.platform,
                'X-AssetVersion': '////',
                'X-DatabaseVersion': '////',
                'X-ClientVersion': '////',
                }
            if config.client == 'global':
                url = 'https://ishin-global.aktsk.com/z_battles/'+str(event['id'])+'/rankings'
            else:
                url = 'http://ishin-production.aktsk.jp/z_battles/'+str(event['id'])+'/rankings'   
            r = requests.get(url, headers=headers)
            
            # Determine the current stage
            if len(r.json()['friends']) == 0:
                level = 1
            else:
                level = int(r.json()['friends'][0]['max_clear_level']) + 1
            
            # Stop at level 30 !! This may not work for all zbattle e.g kid gohan
            while level < 31:
                ##Get supporters
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
                    'Accept': '*/*',
                    'Authorization': packet.mac('GET', '/z_battles/'+str(event['id'])+'/supporters'),
                    'Content-type': 'application/json',
                    'X-Platform': config.platform,
                    'X-AssetVersion': '////',
                    'X-DatabaseVersion': '////',
                    'X-ClientVersion': '////',
                    }
                if config.client == 'global':
                    url = 'https://ishin-global.aktsk.com/z_battles/'+str(event['id'])+'/supporters'
                else:
                    url = 'http://ishin-production.aktsk.jp/z_battles/'+str(event['id'])+'/supporters'   
                r = requests.get(url, headers=headers)
                if 'supporters' in r.json():
                    supporter = r.json()['supporters'][0]['id']
                elif 'error' in r.json():
                    print(Fore.RED+r.json())
                    return 0
                else:
                    print(Fore.RED+'Problem with ZBattle')
                    print(r.raw())
                    return 0

                ###Send first request
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
                    'Accept': '*/*',
                    'Authorization': packet.mac('POST', '/z_battles/'+str(event['id'])+'/start'),
                    'Content-type': 'application/json',
                    'X-Platform': config.platform,
                    'X-AssetVersion': '////',
                    'X-DatabaseVersion': '////',
                    'X-ClientVersion': '////',
                    }


                if kagi == True:
                    sign = json.dumps({
                            'friend_id': supporter,
                            'level': level,
                            'selected_team_num': config.deck,
                            'eventkagi_item_id': 5
                            })
                else:
                    sign = json.dumps({
                            'friend_id': supporter,
                            'level': level,
                            'selected_team_num': config.deck,
                            })

                enc_sign = packet.encrypt_sign(sign)
                data = {'sign': enc_sign}
                if config.client == 'global':
                    url = 'https://ishin-global.aktsk.com/z_battles/'+str(event['id'])+'/start'
                else:
                    url = 'http://ishin-production.aktsk.jp/z_battles/'+str(event['id'])+'/start'
                r = requests.post(url, data=json.dumps(data), headers=headers)

                if 'sign' in r.json():
                    dec_sign = packet.decrypt_sign(r.json()['sign'])
                elif 'error' in r.json():
                    print(r.json())
                    return 0
                else:
                    print(Fore.RED+'Problem with ZBattle')
                    print(r.raw())
                    return 0

                finish_time = int(round(time.time(), 0)+2000)
                start_time = finish_time - randint(6200000, 8200000)

                data = {
                    'elapsed_time': finish_time - start_time,
                    'is_cleared': True,
                    'level': level,
                    's': 'rGAX18h84InCwFGbd/4zr1FvDNKfmo/TJ02pd6onclk=',
                    't': 'eyJzdW1tYXJ5Ijp7ImVuZW15X2F0dGFjayI6MTAwMzg2LCJlbmVteV9hdHRhY2tfY291bnQiOjUsImVuZW15X2hlYWxfY291bnRzIjpbMF0sImVuZW15X2hlYWxzIjpbMF0sImVuZW15X21heF9hdHRhY2siOjEwMDAwMCwiZW5lbXlfbWluX2F0dGFjayI6NTAwMDAsInBsYXllcl9hdHRhY2tfY291bnRzIjpbMTBdLCJwbGF5ZXJfYXR0YWNrcyI6WzMwNjYwNTJdLCJwbGF5ZXJfaGVhbCI6MCwicGxheWVyX2hlYWxfY291bnQiOjAsInBsYXllcl9tYXhfYXR0YWNrcyI6WzEyMzY4NTBdLCJwbGF5ZXJfbWluX2F0dGFja3MiOls0NzcxOThdLCJ0eXBlIjoic3VtbWFyeSJ9fQ==',
                    'token': dec_sign['token'],
                    'used_items': [],
                    'z_battle_finished_at_ms': finish_time,
                    'z_battle_started_at_ms': start_time,
                    }
                #enc_sign = encrypt_sign(sign)

                headers = {
                    'User-Agent': 'Android',
                    'Accept': '*/*',
                    'Authorization': packet.mac('POST', '/z_battles/'+str(event['id'])+'/finish'),
                    'Content-type': 'application/json',
                    'X-Platform': config.platform,
                    'X-AssetVersion': '////',
                    'X-DatabaseVersion': '////',
                    'X-ClientVersion': '////',
                    }
                if config.client == 'global':
                    url = 'https://ishin-global.aktsk.com/z_battles/'+str(event['id'])+'/finish'
                else:
                    url = 'http://ishin-production.aktsk.jp/z_battles/'+str(event['id'])+'/finish'   
                
                r = requests.post(url, data=json.dumps(data), headers=headers)
                r3 = packet.decrypt_sign(r.json()['sign'])
                # ## Print out Items from Database
                print('Level: '+str(level))
                if 'items' in r3:
                    supportitems = []
                    awakeningitems = []
                    trainingitems = []
                    potentialitems = []
                    treasureitems = []
                    carditems = []
                    trainingfields = []
                    stones = 0
                    supportitemsset = set()
                    awakeningitemsset = set()
                    trainingitemsset = set()
                    potentialitemsset = set()
                    treasureitemsset = set()
                    carditemsset = set()
                    trainingfieldsset = set()
                    print('Items:')
                    print('-------------------------')
                    if 'quest_clear_rewards' in r3:
                        for x in r3['quest_clear_rewards']:
                            if x['item_type'] == 'Point::Stone':
                                stones += x['amount']
                    for x in r3['items']:
                        if x['item_type'] == 'SupportItem':

                            # print('' + SupportItems.find(x['item_id']).name + ' x '+str(x['quantity']))

                            for i in range(x['quantity']):
                                supportitems.append(x['item_id'])
                            supportitemsset.add(x['item_id'])
                        elif x['item_type'] == 'PotentialItem':

                            # print('' + PotentialItems.find(x['item_id']).name + ' x '+str(x['quantity']))

                            for i in range(x['quantity']):
                                potentialitems.append(x['item_id'])
                            potentialitemsset.add(x['item_id'])
                        elif x['item_type'] == 'TrainingItem':

                            # print('' + TrainingItems.find(x['item_id']).name + ' x '+str(x['quantity']))

                            for i in range(x['quantity']):
                                trainingitems.append(x['item_id'])
                            trainingitemsset.add(x['item_id'])
                        elif x['item_type'] == 'AwakeningItem':

                            # print('' + AwakeningItems.find(x['item_id']).name + ' x '+str(x['quantity']))

                            for i in range(x['quantity']):
                                awakeningitems.append(x['item_id'])
                            awakeningitemsset.add(x['item_id'])
                        elif x['item_type'] == 'TreasureItem':

                            # print('' + TreasureItems.find(x['item_id']).name + ' x '+str(x['quantity']))

                            for i in range(x['quantity']):
                                treasureitems.append(x['item_id'])
                            treasureitemsset.add(x['item_id'])
                        elif x['item_type'] == 'Card':

                            # card = Cards.find(x['item_id'])

                            carditems.append(x['item_id'])
                            carditemsset.add(x['item_id'])
                        elif x['item_type'] == 'Point::Stone':

            #                print('' + card.name + '['+rarity+']'+ ' x '+str(x['quantity']))
                            # print('' + TreasureItems.find(x['item_id']).name + ' x '+str(x['quantity']))

                            stones += 1
                        elif x['item_type'] == 'TrainingField':

                            # card = Cards.find(x['item_id'])

                            for i in range(x['quantity']):
                                trainingfields.append(x['item_id'])
                            trainingfieldsset.add(x['item_id'])
                        else:
                            print(x['item_type'])
                    for x in supportitemsset:
                        print(Fore.CYAN + config.SupportItems.find(x).name + ' x' \
                            + str(supportitems.count(x)))
                    for x in awakeningitemsset:
                        print(Fore.MAGENTA + config.AwakeningItems.find(x).name + ' x' \
                            + str(awakeningitems.count(x)))
                    for x in trainingitemsset:
                        print(Fore.RED + config.TrainingItems.find(x).name + ' x' \
                            + str(trainingitems.count(x)))
                    for x in potentialitemsset:
                        print(config.PotentialItems.find(x).name + ' x' \
                            + str(potentialitems.count(x)))
                    for x in treasureitemsset:
                        print(Fore.GREEN + config.TreasureItems.find(x).name + ' x' \
                            + str(treasureitems.count(x)))
                    for x in trainingfieldsset:
                        print(config.TrainingFields.find(x).name + ' x' \
                            + str(trainingfields.count(x)))
                    for x in carditemsset:
                        print(config.Cards.find(x).name + ' x' + str(carditems.count(x)))
                    print(Fore.YELLOW + Style.BRIGHT + 'Stones x' + str(stones))

                if 'gasha_point' in r3:
                    print('Friend Points: ' + str(r3['gasha_point']))

                print('--------------------------')
                print('##############################################')
                level += 1
            refresh_client()

    except Exception as e:
        print(Fore.RED+str(e))
        print(Fore.RED+'Trouble finding new Z-Battle events')





