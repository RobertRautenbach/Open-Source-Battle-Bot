from colorama import init, Fore, Back, Style
import config
import json
from orator import DatabaseManager, Model
import packet
from random import choice
from random import randint
import requests
from string import ascii_uppercase
import time


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
    
    print('Begin stage: ' + stage_id + ' ' \
            + config.Quests.find(int(stage_id)).name + ' | Difficulty: ' \
            + str(difficulty) + ' Deck: ' + str(config.deck))
    
    print(Fore.RED + 'Does this quest exist?')
        


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
        else:
            print(Fore.RED + str(r.json()['error']))
    else:
        print(Fore.RED + str(r.json()))
        return 0

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
        'User-Agent': 'Android',
        'Accept': '*/*',
        'Authorization': GetMac('GET', '/quests/' + stage_id
                                + '/supporters', MacId, secret1),
        'Content-type': 'application/json',
        'X-Platform': osx,
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
            data = {'card_ids': cards}
            r = requests.post(url, data=json.dumps(data), headers=headers)
            if 'error' in r.json():
                print(r.json()['error'])
                return 0
            i = 0
            cards_to_sell[:] = []
        
    print('Sold Cards x' + str(len(card_list)))
####################################################################