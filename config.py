from orator import DatabaseManager, Model

AdId = None
UniqueId = None
identifier = None
access_token = None
secret = None
client = 'japan'
platform = 'android'

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