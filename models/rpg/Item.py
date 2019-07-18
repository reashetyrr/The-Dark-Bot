from typing import Union
from models.rpg.Enums import ItemType, Rarity, WeaponType


class Item:
    def __init__(self, item_id: int, level: int, item_type: ItemType, value: int, item_info: dict, rarity: Rarity, stats: dict = None, required_stats: dict = None, required_level: int = 0, weapon_type: WeaponType = None):
        self.id: int = item_id
        self.level: int = level
        self.item_type: ItemType = item_type
        self.value: int = value
        self.stats: dict = stats
        self.required_stats: dict = required_stats
        self.required_level: int = required_level
        self.weapon_type: WeaponType = weapon_type
        self.item_info: dict = item_info
        self.rarity: Rarity = rarity

    def set_item_info(self, info_type: str, value: Union[int, str]):
        self.item_type[info_type] = value
        return self

    def set_item_value(self, value: int):
        self.value = value
        return self

    def set_item_rarity(self, rarity: Rarity):
        self.rarity = rarity
        return