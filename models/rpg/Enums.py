from enum import Enum


class Gender(Enum):
    MALE = 'male'
    FEMALE = 'female'


class EnemyType(Enum):
    MOB = 'mob'
    MINI_BOSS = 'mini boss'
    BOSS = 'boss'
    GOD = 'god'
    PLAYER = 'player'


class ItemType(Enum):
    WEAPON = 'weapon'
    ARMOUR = 'armour'
    SHIELD = 'shield'
    FOOD = 'food'
    COINS = 'coins'
    AMMUNITION = 'ammunition'
    POTION = 'potion'
    QUEST_ITEM = 'quest item'
    INGREDIENT = 'ingredient'
    VEHICLE = 'vehicle'
    EMPTY_SPACE = 'empty space'


class BuildingType(Enum):
    CASTLE = 'castle'
    BLACKSMITH = 'blacksmith'
    TRAINING_ROOM = 'training room'
    MARKETPLACE = 'marketplace'
    MINE = 'mine'
    FIELD = 'field'
    TREASURY = 'treasury'
    DOCK = 'dock'
    DUNGEON = 'dungeon'
    PUB = 'pub'
    TEMPLE = 'temple'
    WALL = 'wall'
    TOWER = 'tower'
    LAIR = 'lair'
    EMPTY_SPACE = 'empty space'


class Races(Enum):
    DEMON = 'demon'
    DARK_ELF = 'dark elf'
    HIGH_ELF = 'high elf'
    SNOW_ELF = 'snow elf'
    WOOD_ELF = 'wood elf'
    GOBLIN = 'goblin'
    GOD = 'god'
    HUMAN = 'human'
    IMP = 'imp'
    DWARF = 'dwarf'
    KHAJIT = 'khajit'
    ORC = 'orc'
    ARGONIAN = 'argonian'


class Gods(Enum):
    ZEUS = 'zeus'
    APHRODITE = 'aphrodite'
    NEMESIS = 'nemesis'
    ATHENA = 'athena'
    ARES = 'ares'
    CUPID = 'cupid'


class VehicleType(Enum):
    HORSE = 'horse'


class WeaponType(Enum):
    AXE = 'axe'
    BOW = 'bow'
    CROSSBOW = 'crossbow'
    CLUB = 'club'
    MACE = 'mace'
    FLAIL = 'flail'
    WARHAMMER = 'warhammer'
    MISC = 'misc'
    JAVELIN = 'javelin'
    SLING = 'sling'
    SPEAR = 'spear'
    STAFF = 'staff'
    SWORD = 'sword'


class ArmourType(Enum):
    HELMET = 'helmet'
    BODY = 'body'
    ARMS = 'arms'
    LEGS = 'legs'
    FEET = 'feet'


class ShieldType(Enum):
    BUCKLER = 'buckler'
    SMALL = 'small'
    LARGE = 'large'


class Material(Enum):
    WOOD = 'wood'
    BRONZE = 'bronze'
    ENCHANTED_BRONZE = 'enchanted bronze'
    IRON = 'iron'
    ENCHANTED_IRON = 'enchanted iron'
    BRONZE_DIAMOND_PLATED = 'diamond plated bronze'
    ENCHANTED_BRONZE_DIAMOND_PLATED = 'enchanted diamond plated bronze'
    IRON_DIAMOND_PLATED = 'diaamond plated iron'
    ENCHANTED_IRON_DIAMOND_PLATED = 'enchanted diamond plated iron'
    DIVINE_METAL = 'devine metal'


class Rarity(Enum):
    COMMON = 'common'
    RARE = 'rare'
    SUPER_RARE = 'super rare'
    ULTRA_RARE = 'ultra rare'
    LEGENDARY = 'legendary'
    GODLIKE = 'godlike'
