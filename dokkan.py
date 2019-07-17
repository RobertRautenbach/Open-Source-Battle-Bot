from colorama import init, Fore, Back, Style
import commands
import config
import sys

# Coloroma autoreset
init(autoreset=True)


while True:
    print(' ')
    print(Fore.CYAN + Style.BRIGHT + 'Select one of the following')
    print('---------------------------------')
    print(' ')
    # Database Check.
    while True:
        print('Check for updated database? (' + Fore.YELLOW + Style.BRIGHT + 'Yes: 1 ' + Style.RESET_ALL + 'or ' + Fore.YELLOW + Style.BRIGHT + 'No: 2' + Style.RESET_ALL + ')',end='')
        print()
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
        print('Perform daily logins on all accounts? (' + Fore.YELLOW + Style.BRIGHT + 'Yes: 1 ' + Style.RESET_ALL + 'or ' + Fore.YELLOW + Style.BRIGHT + 'No: 2' + Style.RESET_ALL + ')',end='')
        print()
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
        print('Which version? (' + Fore.YELLOW + Style.BRIGHT + 'Jp: 1 ' + Style.RESET_ALL + 'or ' + Fore.YELLOW + Style.BRIGHT + 'Global: 2' + Style.RESET_ALL + ')',end='')
        print()
        client = input(" ")
        if client.lower() == '1':
            config.client = 'japan'
            break
        elif client.lower() == '2':
            config.client = 'global'
            break
        else:
            continue


    # User Options
    print(' ')
    while True:
        print('---------------------------------')
        print(Fore.CYAN + Style.BRIGHT + 'New Account :' + Fore.YELLOW + Style.BRIGHT + ' 0')
        print(Fore.CYAN + Style.BRIGHT + 'Transfer Account :' + Fore.YELLOW + Style.BRIGHT + ' 1')
        print(Fore.CYAN + Style.BRIGHT + 'Load From Save :'  + Fore.YELLOW + Style.BRIGHT + ' 2')
        print('---------------------------------')
        print(' ')
        command = input('Enter your choice: ')
        if command == '0':
            print(' ')
            config.identifier = commands.signup()
            commands.save_account()
            config.access_token,config.secret = commands.signin(config.identifier)
            commands.tutorial()
            commands.daily_login()
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
        print(Fore.CYAN + Style.BRIGHT + "Type" + Fore.YELLOW + Style.BRIGHT + " 'help'" + Fore.CYAN + Style.BRIGHT + " to view all commands.")

        # Set up comma separated chain commands. Handled via stdin
        try:
            command = input()
        except:
            sys.stdin = sys.__stdin__
            command = input()

        if command == 'exit':
            break
        # Pass command to command executor and handle keyboard interrupts.
        try:
            commands.user_command_executor(command)
        except KeyboardInterrupt:
            print(Fore.CYAN + Style.BRIGHT + 'User interrupted process.')
        except Exception as e:
            print(Fore.RED + Style.BRIGHT + repr(e))



