from models.rpg.Enums import Gender


class BaseRace:
    def __init__(self, stats: dict):
        self.stats: dict = stats
