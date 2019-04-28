import commands
import config


print('0:| New Account')
print('1:| Transfer Account To The Bot')
print('2:| Load A Save')
command = input('Enter a choice ->: ')
while True:
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
    command = input()
    try:
        commands.user_command_executor(command)
    except KeyboardInterrupt:
        print('User interrupted process.')
    except Exception as e:
        print(repr(e))




#commands.db_download()
#commands.get_kagi_id('310001')



