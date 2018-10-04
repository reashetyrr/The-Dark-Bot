import json
from models.DB import DB


class Server(object):
    def __init__(self, user_id, plugins, status='new'):
        self.id = int(user_id)
        self.plugins = plugins if type(plugins) is dict else json.loads(plugins)
        self.status = status

    @classmethod
    def get_by_id(cls, server_id):
        result = DB().fetch_one('SELECT * FROM `servers` WHERE id=?', [int(server_id)])
        server_id, plugins = result
        return cls(server_id, plugins, status='existing')

    def save(self):
        query = 'INSERT OR REPLACE INTO servers(id, plugins) VALUES(?,?)' if self.status == 'new' else 'UPDATE servers SET plugins=? WHERE id=?'
        values = (self.id, json.dumps(self.plugins)) if self.status == 'new' else (json.dumps(self.plugins), self.id)
        return DB().execute(query, values)


if __name__ == '__main__':
    pass
