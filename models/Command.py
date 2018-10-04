import discord
import json
from models.DB import DB


class Command(object):
    def __init__(self, command: dict, author: discord.member, client: discord.client, message: discord.message, params: list):
        self.author = author
        self.client = client
        self.message = message
        self.params = params
        self.command = command
        self.guild_plugins = None

    async def run_test(self):
        res = await self.is_plugin_enabled()
        if res.get('message') and 'plugin not enabled' == res['message']:
            await self.message.channel.send('This plugin has not been enabled, please contact the server owner!')
            return False
        elif res.get('message'):
            return False
        if not self.can_execute():
            await self.message.channel.send('You do not have the permissions to execute command `%s`!' % self.command['command'])
            return False
        return True

    def can_execute(self):
        return (self.author.guild_permissions.administrator and self.command['type'] > 1) or self.command['type'] == 1

    async def is_plugin_enabled(self):
        guild = DB().fetch_one('SELECT * FROM servers WHERE id=?', (self.message.guild.id,))
        if not guild and self.command['command'] == 'tdb!reindex':
            return dict(status=200)
        elif not guild:
            await self.message.channel.send('The current server is not indexed, please ask an administrator to execute the reindex command.')
            return dict(status=403, message='plugin not indexed')
        g_id, g_plugins = guild
        self.guild_plugins = plugins = json.loads(g_plugins)
        if self.command['name'] in plugins:
            d_plugin = DB().fetch_one('SELECT * FROM plugins WHERE name=?', (self.command['name'],))
            d_id, d_name, d_information, d_command, d_usage, d_required_plugins, d_type = d_plugin
            if d_required_plugins:
                for p in json.loads(d_required_plugins):
                    if p not in plugins:
                        await self.message.channel.send('Missing plugin requirement: %s, please enable it with: tdb!plugin enable %s' % (p, p))
                        return dict(status=403, message='missing plugin requirement')
        else:
            return dict(status=403, message='plugin not enabled')
        return dict(status=200)


def is_command(message: str):
    command = DB().fetch_one('SELECT * FROM plugins WHERE command=?', (message,))
    try:
        c_id, c_name, c_information, c_command, c_usage, c_required_plugins, c_type = command
        command = dict(
            id=c_id,
            name=c_name,
            information=json.loads(c_information) if c_information else None,
            command=c_command,
            usage=c_usage,
            required_plugins=json.loads(c_required_plugins) if c_required_plugins else None,
            type=c_type
        )
    except TypeError:
        pass
    return command
