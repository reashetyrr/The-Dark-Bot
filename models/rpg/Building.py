from models.User import User



class Building:
    def __init__(self, level: int, owner: User = None, inventory: list = None, building_type: BuildingType = BuildingType.EMPTY_SPACE):
        self.building_type: BuildingType = building_type
        self.level: int = level
        self.owner: User = owner
        self.inventory: list = inventory
