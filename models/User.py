import datetime
import time
import json
from models.DB import DB


class User(object):
    def __init__(self, user_id, avatar_url, created_at, discriminator, mention, name, display_name, plugins, status='new'):
        self.id = int(user_id)
        self.avatar_url = avatar_url
        self.created_at = time.mktime(created_at.timetuple()) if type(created_at) is datetime else created_at
        self.discriminator = discriminator
        self.mention = mention
        self.name = name
        self.display_name = display_name
        self.plugins = plugins if type(plugins) is dict else json.loads(plugins)
        self.status = status

    @classmethod
    def get_by_id(cls, user_id):
        result = DB().fetch_one('SELECT * FROM `users` WHERE id=?', [int(user_id)])
        user_id, avatar_url, created_at, discriminator, mention, name, display_name, plugins = result
        return cls(user_id, avatar_url, created_at, discriminator, mention, name, display_name, plugins, status='existing')

    @classmethod
    def get_by_mention(cls, mention):
        result = DB().fetch_one('SELECT * FROM users WHERE mention=?', [mention])
        user_id, avatar_url, created_at, discriminator, mention, name, display_name, plugins = result
        return cls(user_id, avatar_url, created_at, discriminator, mention, name, display_name, plugins, status='existing')

    @classmethod
    def get_many_by_id(cls, ids, return_value=None):
        results = DB().fetch_many('SELECT * FROM users WHERE id=?', ids)
        users = []
        for res in results:
            user_id, avatar_url, created_at, discriminator, mention, name, display_name, plugins = res
            if not return_value:
                users.append(cls(user_id, avatar_url, created_at, discriminator, mention, name, display_name, plugins, status='existing'))
            elif 'id' == return_value:
                users.append(user_id)
        return users

    def save(self):
        query = 'INSERT OR REPLACE INTO users(id, avatar_url, created_at, discriminator, mention, name, display_name, plugins) VALUES(?,?,?,?,?,?,?,?)' if self.status == 'new' else 'UPDATE users SET avatar_url=?, created_at=?, discriminator=?, mention=?, name=?, display_name=?, plugins=? WHERE id=?'
        values = (self.id, self.avatar_url, self.created_at, self.discriminator, self.mention, self.name, self.display_name, json.dumps(self.plugins)) if self.status == 'new' else (self.avatar_url, self.created_at, self.discriminator, self.mention, self.name, self.display_name, json.dumps(self.plugins), self.id)
        return DB().execute(query, values)


if __name__ == '__main__':
    user = User('488669510555926539', 'https://cdn.discordapp.com/avatars/488669510555926539/45a1cb84d360d082f2e891268601855b.webp?size=1024', '2018-09-10 11:18:10.357000', '4351', '<@488669510555926539>', 'The Dark Bot', 'The Dark Bot', {})
    user.save()

    u = User.get_by_id('488669510555926539')
    pass
