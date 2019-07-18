from models.rpg.Enums import Races, ItemType, Rarity, WeaponType


class Character:
    def __init__(self, race: Races, level: int, gear: dict, inventory: dict, stats: dict, experience: int):
        self.race: Races = race
        self.level: int = level
        self.gear: dict = gear
        self.inventory: dict = inventory
        self.stats: dict = stats
        self.experience: int = experience

