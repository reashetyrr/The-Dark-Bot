from models.DB import DB
from models.rolemenu_emote import RolemenuEmote


def get_fields():
    return 'guild_id, name, message_id, id'


class Rolemenu:
    def __init__(self, guild_id: int, name: str, messsage_id: int=None, rolemenu_id: int=None):
        self.id = rolemenu_id
        self.guild_id = guild_id
        self.name = name
        self.messsage_id = messsage_id
        self.emotes = RolemenuEmote.get_by_rolemenu_id(rolemenu_id)

    @classmethod
    def get_by_id(cls, rolemenu_id: int):
        result = DB().fetch_one(f'SELECT {get_fields()} FROM `rolemenus` WHERE id=%s', [rolemenu_id])
        return cls(*result) if result else None

    @classmethod
    def get_by_message_id(cls, message_id: int):
        result = DB().fetch_one(f'SELECT {get_fields()} FROM rolemenus WHERE message_id=%s', [message_id])
        return cls(*result) if result else None

    @classmethod
    def get_all(cls):
        results = DB().fetch_all(f'SELECT {get_fields()} FROM `rolemenus`')
        rolemenus = [cls(*result) for result in results] if results else None
        return rolemenus

    @classmethod
    def get_all_by_guild(cls, guild_id: int):
        results = DB().fetch_all(f'SELECT {get_fields()} FROM rolemenus WHERE guild_id=%s', [guild_id])
        rolemenus = [cls(*result) for result in results] if results else None
        return rolemenus

    @classmethod
    def get_by_name_and_id(cls, name: str, guild_id: int):
        result = DB().fetch_one(f'SELECT {get_fields()} FROM rolemenus WHERE name=%s AND guild_id=%s', [name, guild_id])
        return cls(*result) if result else None

    @classmethod
    def get_by_id_and_guild(cls, menu_id: int, guild_id: int):
        result = DB().fetch_one(f'SELECT {get_fields()} FROM rolemenus WHERE id=%s AND guild_id=%s', [menu_id, guild_id])
        return cls(*result) if result else None

    def save(self):
        query = f'REPLACE INTO rolemenus({get_fields()}) VALUES(%s,%s,%s,%s)'
        values = [
            self.guild_id,
            self.name,
            self.messsage_id,
            self.id
        ]
        inserted_id = DB().insert_return_id(query, values)
        self.id = inserted_id
        return self

    def delete(self):
        query = f'DELETE FROM rolemenus WHERE id=%s'
        values = [self.id]
        DB().execute(query, values)
        return None


if __name__ == '__main__':
    rolemenu = Rolemenu.get_by_id(7)
    pass
