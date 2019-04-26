import commands
import config

identifier = commands.signup()
config.access_token,config.secret = commands.signin(identifier)
commands.tutorial()
commands.complete_stage('1001','0')