import json
from models.DB import DB


class ServerSettings(object):
    def __init__(self, server_id, settings, status='new'):
        self.id = int(server_id)
        self.settings = json.loads(settings) if type(settings) is str else settings
        self.status = status

    @classmethod
    def get_by_id(cls, server_id):
        result = DB().fetch_one('SELECT * FROM `server_settings` WHERE server_id=?', [int(server_id)])
        if result:
            server_id, server_settings = result
            return cls(server_id, server_settings, status='existing')
        return None

    def save(self):
        query = 'INSERT OR REPLACE INTO server_settings(server_id, settings) VALUES(?,?)' if self.status == 'new' else 'UPDATE server_settings SET settings=? WHERE server_id=?'
        values = (self.id, json.dumps(self.settings) if self.settings else None) if self.status == 'new' else (json.dumps(self.settings) if self.settings else None, self.id)
        return DB().execute(query, values)


if __name__ == '__main__':
    pass
