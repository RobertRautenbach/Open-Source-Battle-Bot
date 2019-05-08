import commands
import config
import sys

while True:
    db = input("Download new DB's? Y/N: ")
    if db.lower() == 'y':
        commands.db_download()
        break
    elif db.lower() == 'n':
        break
    else:
        continue

while True:
    client = input("JP or GLB? J/G: ")
    if client.lower() == 'j':
        config.client = 'japan'
        break
    elif client.lower() == 'g':
        config.client = 'global'
        break
    else:
        continue

while True:
    print('0:| New Account')
    print('1:| Transfer Account To The Bot')
    print('2:| Load A Save')
    command = input('Enter a choice ->: ')
    if command == '0':
        config.identifier = commands.signup()
        commands.save_account()
        config.access_token,config.secret = commands.signin(config.identifier)
        commands.tutorial()
        commands.daily_login()
        break
    elif command == '1':
        commands.transfer_account()
        commands.daily_login()
        break
    elif command == '2':
        commands.load_account()
        commands.daily_login()
        commands.accept_gifts()
        commands.accept_missions()
        break
    else:
        print("Command not understood")



while True:
    print("Type 'help' to view all commands.")

    # Set up comma separated chain commands. Handled via stdin
    try:
        command = input()
    except:
        sys.stdin = sys.__stdin__
        command = input()

    # Pass command to command executor and hand keyboard interrupts.
    try:
        commands.user_command_executor(command)
    except KeyboardInterrupt:
        print('User interrupted process.')
    except Exception as e:
        print(repr(e))



