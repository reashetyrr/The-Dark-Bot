import datetime
import time
import json
from models.DB import DB


class User(object):
    def __init__(self, user_id, avatar_url, created_at, discriminator, mention, name, display_name, plugins, last_xp, banned, status='new'):
        if plugins == '' or plugins is None:
            plugins = dict()
        self.id: int = int(user_id)
        self.avatar_url: str = avatar_url
        self.created_at = time.mktime(created_at.timetuple()) if type(created_at) is datetime else created_at
        self.discriminator = discriminator
        self.mention: str = mention
        self.name: str = name
        self.display_name: str = display_name
        self.plugins: dict = plugins if type(plugins) is dict else json.loads(plugins)
        self.last_xp: int = last_xp if last_xp else 0
        self.status = status
        self.banned = banned == 1

    @classmethod
    def get_by_id(cls, user_id):
        result = DB().fetch_one('SELECT * FROM `users` WHERE id=%s', [user_id])
        if result:
            user_id, avatar_url, created_at, discriminator, mention, name, display_name, plugins, last_xp, banned = result
            return cls(user_id, avatar_url, created_at, discriminator, mention, name, display_name, plugins, last_xp, banned, status='existing')
        return None

    @classmethod
    def get_by_mention(cls, mention):
        result = DB().fetch_one('SELECT * FROM users WHERE mention=%s', [mention])
        if result:
            user_id, avatar_url, created_at, discriminator, mention, name, display_name, plugins, last_xp, banned = result
            return cls(user_id, avatar_url, created_at, discriminator, mention, name, display_name, plugins, last_xp, banned, status='existing')
        return None

    @classmethod
    def get_many_by_id(cls, ids, return_value=None):
        results = DB().fetch_many('SELECT * FROM users WHERE id=%s', ids)
        users = []
        for res in results:
            user_id, avatar_url, created_at, discriminator, mention, name, display_name, plugins, last_xp, banned = res
            if not return_value:
                users.append(cls(user_id, avatar_url, created_at, discriminator, mention, name, display_name, plugins, last_xp, banned, status='existing'))
            elif 'id' == return_value:
                users.append(user_id)
        return users

    @classmethod
    def get_all(cls):
        results = DB().fetch_all('SELECT * FROM users WHERE name IS NOT NULL', [])
        users = []
        # for res in results:
        #     user_id, avatar_url, created_at, discriminator, mention, name, display_name, plugins, last_xp = res
        #     users.append(cls(user_id, avatar_url, created_at, discriminator, mention, name, display_name, plugins, last_xp, status='existing'))
        return [cls(*m, status='existing') for m in results]

    def save(self):
        query = 'REPLACE INTO users(id, avatar_url, created_at, discriminator, mention, name, display_name, plugins, last_xp) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)' if self.status == 'new' else 'UPDATE users SET id=%s, avatar_url=%s, created_at=%s, discriminator=%s, mention=%s, name=%s, display_name=%s, plugins=%s, last_xp=%s, banned=%s WHERE mention=%s'
        values = (self.id, self.avatar_url, self.created_at, self.discriminator, self.mention, self.name, self.display_name, json.dumps(self.plugins), self.last_xp) if self.status == 'new' else (self.id, self.avatar_url, self.created_at, self.discriminator, self.mention, self.name, self.display_name, json.dumps(self.plugins), self.last_xp, self.banned, self.mention)
        return DB().execute(query, values)


if __name__ == '__main__':
    u = User.get_by_id('488669510555926539')
    pass
