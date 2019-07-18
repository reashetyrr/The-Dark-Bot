from models.DB import DB
from datetime import date


def get_fields():
    return 'id,user_id,quote,year,guild_id'


class Quote:
    def __init__(self, quote_id: int = None, user_id: str = None, quote: str = None, year: int = None, guild_id: int = None):
        self.id = quote_id
        self.user_id = user_id
        self.quote = quote.decode('utf-8') if isinstance(quote, bytes) else quote
        self.year = year if year else date.year
        self.guild_id = guild_id

    @classmethod
    def get_by_id(cls, quote_id: int):
        result = DB().fetch_one(f'SELECT {get_fields()} FROM quotes WHERE id=%s', [quote_id])
        return cls(*result) if result else None

    @classmethod
    def get_random(cls, guild_id):
        result = DB().fetch_one(f'SELECT {get_fields()} FROM quotes WHERE guild_id=%s AND enabled=1 ORDER BY RAND() LIMIT 1', [guild_id])
        return cls(*result) if result else None

    @classmethod
    def get_by_user_id(cls, guild_id: int, user_id: int):
        results = DB().fetch_all(f'SELECT {get_fields()} FROM quotes WHERE guild_id=%s AND user_id=%s AND enabled=1', [guild_id, user_id])
        return [cls(*result) for result in results] if results else None

    def save(self):
        query = f'REPLACE INTO quotes({get_fields()}) VALUES(%s,%s,%s,%s, %s)'
        values = [
            self.id,
            self.user_id,
            self.quote,
            self.year,
            self.guild_id
        ]
        inserted_id = DB().insert_return_id(query, values)
        self.id = inserted_id
        return self

    def delete(self):
        query = f'DELETE FROM quotes WHERE id=%s'
        values = [self.id]
        DB().execute(query, values)
        return None
