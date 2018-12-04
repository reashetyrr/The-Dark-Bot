import models
import json
from models.Command import Command
from models.DB import DB


class Reindex(Command):
    def __init__(self, **kwargs):
        Command.__init__(self, **kwargs)

    async def execute(self):
        if not await self.run_test():
            return

        g = DB().fetch_one('SELECT * FROM servers WHERE id=?', (self.message.guild.id,))

        if not g:
            DB().execute('INSERT INTO servers(id, plugins) VALUES(?,?)', (self.message.guild.id, json.dumps(['plugin', 'commands'])))

        await self.message.channel.send('Starting reindexing process.')
        users = []
        for user in self.message.guild.members:
            if user.bot:
                continue

            u = models.User(user.id, user.avatar_url if user.avatar_url != '' else user.default_avatar_url, user.created_at, user.discriminator, user.mention, user.name, user.display_name, {}).save()
            users.append(u)

        return await self.message.channel.send('Succesfully completed reindexing process, saved %d users to database.' % len(users))
