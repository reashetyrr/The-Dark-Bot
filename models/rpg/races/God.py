from models.rpg.BaseRace import BaseRace


class God(BaseRace):
    def __init__(self, stats: dict):
        super().__init__(stats)