from models.DB import DB


def get_fields():
    return 'rolemenu_id, icon, name, id'


class RolemenuEmote:
    def __init__(self, rolemenu_id: int, icon: str, name: str, rolemenu_emote_id: int=None):
        self.id = rolemenu_emote_id
        self.rolemenu_id = rolemenu_id
        self.name = name
        self.icon = icon.decode('utf-8') if type(icon) is bytes else icon

    @classmethod
    def get_by_id(cls, rolemenu_emote_id: int):
        result = DB().fetch_one(f'SELECT {get_fields()} FROM `rolemenu_roles` WHERE id=%s', [rolemenu_emote_id])
        return cls(*result) if result else None

    @classmethod
    def get_all(cls):
        results = DB().fetch_all(f'SELECT {get_fields()} FROM `rolemenu_roles`')
        return [cls(*result) for result in results] if results else None

    @classmethod
    def get_by_rolemenu_id(cls, rolemenu_id: int):
        results = DB().fetch_all(f'SELECT {get_fields()} FROM `rolemenu_roles` WHERE rolemenu_id=%s', [rolemenu_id])
        return [cls(*result) for result in results] if results else None

    @classmethod
    def get_by_emoji(cls, emoji: str, rolemenu_id: int):
        result = DB().fetch_one(f'SELECT {get_fields()} FROM rolemenu_roles WHERE icon=%s and rolemenu_id=%s', [str(emoji), rolemenu_id])
        return cls(*result) if result else None

    def save(self):
        query = f'REPLACE INTO rolemenu_roles({get_fields()}) VALUES(%s,%s,%s,%s)'
        values = [
            self.rolemenu_id,
            self.icon,
            self.name,
            self.id
        ]
        inserted_id = DB().insert_return_id(query, values)
        self.id = inserted_id
        return self

    def delete(self):
        query = f'DELETE FROM rolemenu_roles WHERE id=%s'
        values = [self.id]
        DB().execute(query, values)
        return None


if __name__ == '__main__':
    emotes = RolemenuEmote.get_all()
    pass
