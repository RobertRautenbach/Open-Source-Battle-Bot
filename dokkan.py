import commands
import config

config.identifier = commands.signup()
commands.save_account()
commands.load_account()
config.access_token,config.secret = commands.signin(config.identifier)
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
commands.complete_unfinished_quest_stages()
commands.complete_clash()
commands.complete_unfinished_events()

