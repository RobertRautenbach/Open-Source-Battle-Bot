from orator import DatabaseManager, Model

gb_url = ''
gb_port = 0
jp_url = ''
jp_port = 0

'''
these can be updated automatically but it'd require an APK download.
it's better to manually update them along with the bot to prevent account bans from game-breaking changes.
noted here: https://twitter.com/dbzspace/status/1106316112638210050
we're not sure what the 2 hashes are of... - k1mpl0s
'''
version_code = '4.7.1-0cfca85464a68be2257af10e69257dfba116fa0f7315c6b930b4eec74f41a49f'
# 4.8.3-3998abb91156a951db70394807eb63d626d20c640c0c2f4611b0973499ce87ef
# ^ this is set if account is japan in load_account() - commands.py

AdId = None
UniqueId = None
identifier = None
access_token = None
secret = None
client = 'japan'
platform = 'android'
user_agent = 'Dalvik/2.1.0 (Linux; Android 7.0; SM-E7000)'
# CFNetwork/808.3 Darwin/16.3.0 (iPhone; CPU iPhone OS 13_0 like Mac OS X)
# ^ this is set if platform is iOS in load_account() - commands.py

### Reroll parameters
last_save_name = ''
reroll_state = False


deck = 1
allow_stamina_refill = True


### Database Config
jp_config = {'mysql': {'driver': 'sqlite', 'database': 'jp.db'}}
glb_config = {'mysql': {'driver': 'sqlite', 'database': 'glb.db'}}
db_glb = DatabaseManager(glb_config)
db_jp = DatabaseManager(jp_config)
Model.set_connection_resolver(db_glb)

class LeaderSkills(Model):

    __table__ = 'leader_skills'
    
class LinkSkills(Model):

    __table__ = 'link_skills'

class AreaTabs(Model):

    __table__ = 'area_tabs'

class CardSpecials(Model):

    __table__ = 'card_specials'

class Passives(Model):

    __table__ = 'passive_skill_sets'

class Supers(Model):

    __table__ = 'specials'

class ZBattles(Model):

    __table__ = 'z_battle_stage_views'

class CardCategories(Model):

    __table__ = 'card_categories'

class CardCardCategories(Model):

    __table__ = 'card_card_categories'

class TreasureItems(Model):

    __table__ = 'treasure_items'


class AwakeningItems(Model):

    __table__ = 'awakening_items'


class SupportItems(Model):

    __table__ = 'support_items'


class PotentialItems(Model):

    __table__ = 'potential_items'

class SpecialItems(Model):

    __table__ = 'special_items'


class TrainingItems(Model):

    __table__ = 'training_items'


class Cards(Model):

    __table__ = 'cards'


class Quests(Model):

    __table__ = 'quests'

class Ranks(Model):

    __table__ = 'rank_statuses'


class TrainingFields(Model):

    __table__ = 'training_fields'


class Sugoroku(Model):

    __table__ = 'sugoroku_maps'


class Area(Model):

    __table__ = 'areas'


class Medal(Model):

    __table__ = 'awakening_items'