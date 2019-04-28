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
        break
    elif command == '1':
        commands.transfer_account()
        break
    elif command == '2':
        commands.load_account()
        break
    else:
        print("Command not understood")

commands.user_command_executor('help')



commands.get_transfer_code()
commands.complete_unfinished_quest_stages()
commands.dragonballs()
commands.dragonballs()
commands.daily_login()
#commands.db_download()
commands.tutorial()
commands.complete_area(1)
commands.complete_stage('1001','0')
commands.accept_missions()
commands.accept_gifts()
#commands.change_team()
#commands.get_kagi_id('310001')
commands.increase_capacity()
#commands.change_name()
commands.get_user_info()
commands.get_transfer_code()

commands.complete_clash()
commands.complete_unfinished_events()

