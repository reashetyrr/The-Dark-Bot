from models.rpg.Enums import EnemyType, Races

class Enemy:
    def __init__(self, stats: dict, enemy_type: EnemyType, enemy_race: Races):
        super().__init__(stats)