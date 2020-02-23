from colorama import init, Fore, Back, Style
import commands
import config
import sys

# Coloroma autoreset
init(autoreset=True)

# before anything a request for new URL & API port is required. - k1mpl0s
def checkServers(ver):
    try:
        if ver == 'gb':
            url = 'https://ishin-global.aktsk.com/ping'
        else:
            url = 'https://ishin-production.aktsk.jp/ping'
        # we send an ancient version code that is valid.
        headers = {
            'X-Platform': 'android',
            'X-ClientVersion': '1.0.0',
            'X-Language': 'en',
            'X-UserID': '////'
        }
        r = requests.get(url, data=None, headers=headers)
        # store our requested data into a variable as json.
        store = r.json()
        if 'error' not in store:
            url = store['ping_info']['host']
            port = store['ping_info']['port_str']
            if ver == 'gb':
                config.gb_url = 'https://' + str(url)
                config.gb_port = str(port)
            else:
                config.jp_url = 'https://' + str(url)
                config.jp_port = str(port)
            return True
        else:
            print(Fore.RED + '[' + ver + ' server] ' + str(store['error']))
            return False
    except:
        print(Fore.RED + '[' + ver + ' server] can\'t connect.')
        return False
if checkServers('gb') and checkServers('jp'):
    print(Fore.GREEN + 'connected successfully.')
else:
    # we can't use the farmbot period if there's no URL to make requests to...
    print(Fore.RED + 'press ENTER to close...')
    input()
    exit()

while True:
    print(' ')
    print(Fore.CYAN + Style.BRIGHT + 'Select one of the following')
    print('---------------------------------')
    print(' ')
    # Database Check.
    while True:
        print(
            'Check for updated database? (' + Fore.YELLOW + Style.BRIGHT + 'Yes: 1 ' + Style.RESET_ALL + 'or ' + Fore.YELLOW + Style.BRIGHT + 'No: 2' + Style.RESET_ALL + ')',
            end='')
        db = input(' ')
        if db.lower() == '1':
            commands.db_download()
            break
        elif db.lower() == '2':
            break
        else:
            print('')
            continue

    # Daily Logins?
    print(' ')
    print(Fore.CYAN + Style.BRIGHT + 'Choose an option')
    print('---------------------------------')
    print(' ')
    while True:
        print(
            'Perform daily logins on all accounts? (' + Fore.YELLOW + Style.BRIGHT + 'Yes: 1 ' + Style.RESET_ALL + 'or ' + Fore.YELLOW + Style.BRIGHT + 'No: 2' + Style.RESET_ALL + ')',
            end='')
        db = input(' ')
        if db.lower() == '1':
            commands.bulk_daily_logins()
            break
        elif db.lower() == '2':
            break
        else:
            continue

    # Decide which client to use.
    print(' ')
    print(Fore.CYAN + Style.BRIGHT + 'Choose a version')
    print('---------------------------------')
    print(' ')
    while True:
        print(
            'Which version? (' + Fore.YELLOW + Style.BRIGHT + 'Jp: 1 ' + Style.RESET_ALL + 'or ' + Fore.YELLOW + Style.BRIGHT + 'Global: 2' + Style.RESET_ALL + ')',
            end='')
        client = input(" ")
        if client.lower() == '1':
            config.client = 'japan'
            break
        elif client.lower() == '2':
            config.client = 'global'
            break
        else:
            continue

    command = ''
    config.reroll_state = False

    while command != 'exit':
        # User Options
        print(' ')
        if command == 'reroll' or command == '':
            while True:
                if config.reroll_state:
                    command = '0'
                else:
                    print('---------------------------------')
                    print(Fore.CYAN + Style.BRIGHT + 'New Account :' + Fore.YELLOW + Style.BRIGHT + ' 0')
                    print(Fore.CYAN + Style.BRIGHT + 'Transfer Account :' + Fore.YELLOW + Style.BRIGHT + ' 1')
                    print(Fore.CYAN + Style.BRIGHT + 'Load From Save :' + Fore.YELLOW + Style.BRIGHT + ' 2')
                    print('---------------------------------')
                    command = input('Enter your choice: ')
                    config.reroll_state = False
                if command == '0':
                    print(' ')
                    config.identifier = commands.signup(config.reroll_state)
                    commands.save_account(config.reroll_state)
                    config.access_token, config.secret = commands.signin(config.identifier)
                    commands.tutorial()
                    commands.daily_login()
                    if config.reroll_state:
                        commands.accept_gifts()
                        commands.accept_missions()
                        print(' ')
                        print(' --------- Alright guys! We\'re back for another Dokkan Battle Video! ---------- ')
                        print(' ')
                        commands.user_command_executor('summon')
                    break
                elif command == '1':
                    print(' ')
                    commands.transfer_account()
                    commands.daily_login()
                    break
                elif command == '2':
                    print(' ')
                    commands.load_account()
                    commands.daily_login()
                    commands.accept_gifts()
                    commands.accept_missions()
                    break
                else:
                    print(Fore.RED + Style.BRIGHT + "Command not understood")

        # User commands.
        while True:
            print('---------------------------------')
            print(
                Fore.CYAN + Style.BRIGHT + "Type" + Fore.YELLOW + Style.BRIGHT + " 'help'" + Fore.CYAN + Style.BRIGHT + " to view all commands.")

            # Set up comma separated chain commands. Handled via stdin
            try:
                command = input()
            except:
                sys.stdin = sys.__stdin__
                command = input()

            if command == 'exit':
                config.reroll_state = False
                break
            elif command == 'reroll':
                config.reroll_state = True
                break

            # Pass command to command executor and handle keyboard interrupts.
            try:
                commands.user_command_executor(command)
            except KeyboardInterrupt:
                print(Fore.CYAN + Style.BRIGHT + 'User interrupted process.')
            except Exception as e:
                print(Fore.RED + Style.BRIGHT + repr(e))
