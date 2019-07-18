from models.rpg.BaseRace import BaseRace


class Human(BaseRace):
    def __init__(self, **kwargs):
        if not kwargs.get('stats'):
            kwargs['stats'] = dict(
                vitality=11,
                endurance=12,
                strength=13,
                dexterity=13,
                resistance=11,
                intelligence=9
            )
        super().__init__(**kwargs)
