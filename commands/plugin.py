import discord
import config
import json
from models.DB import DB
from models.Command import Command


class Plugin(Command):
    """
        Special plugin command to enable or disable plugins in a guild
        this command is limited to owner for the time being, this to
        prevent possible vunerabilities in the commands or plugins
    """
    def __init__(self, **kwargs):
        Command.__init__(self, **kwargs)

    async def execute(self):
        if not await self.run_test():
            return

        params = self.params

        embed = discord.Embed(title='%s - Plugins' % self.message.guild.name, description='', color=config.embed_color,
                              colour=config.embed_color)
        if not params or len(params) == 0:
            embed.add_field(name='Information', value='\n'.join(self.command['information']))
            return await self.message.channel.send(embed=embed)
        if len(params) <= 1 and params[0] not in ['list', 'enabled']:
            embed.add_field(name='Usage', value=self.command['usage'])
            return await self.message.channel.send(embed=embed)

        action = params.pop(0)

        if 'enabled' == action:
            embed.add_field(name='Enabled plugins', value='\n'.join([plugin for plugin in self.guild_plugins if plugin != 'plugin']) if len(self.guild_plugins) > 1 else 'None')
        if 'list' == action:
            d_plugins = DB().fetch_all('SELECT * FROM plugins WHERE ?', (1,))
            plugins = []
            for p in d_plugins:
                d_id, d_name, d_information, d_command, d_usage, d_required_plugins, d_type = p
                plugins.append('%s: Required plugins: [%s]' % (d_name, ','.join(json.loads(d_required_plugins))if d_required_plugins else 'None'))
            embed.add_field(name='Plugin list', value='\n'.join(plugins))
        if 'enable' == action:
            s_plugin = params.pop(0)
            d_plugin = DB().fetch_one('SELECT * FROM plugins WHERE name=?', (s_plugin,))
            if s_plugin == 'moderation':
                await self.create_log_channel()
                embed = self.enable_plugin(d_plugin, s_plugin, embed)
            if not d_plugin:
                embed.add_field(name='Error', value='Plugin %s not found!' % s_plugin)
            else:
                embed = self.enable_plugin(d_plugin, s_plugin, embed)
        if 'disable' == action:
            s_plugin = params.pop(0)
            d_plugin = DB().fetch_one('SELECT * FROM plugins WHERE name=?', (s_plugin,))
            if not d_plugin:
                embed.add_field(name='Error', value='Plugin %s not found!' % s_plugin)
            else:
                self.guild_plugins.remove(s_plugin)
                DB().execute('UPDATE servers SET plugins=? WHERE id=?', (json.dumps(self.guild_plugins), self.message.guild.id))
                embed.add_field(name='Success', value='Succesfully disabled the %s plugin!' % s_plugin)
        return await self.message.channel.send(embed=embed)

    async def create_log_channel(self):
        guild = self.message.guild
        log_channel = discord.utils.find(lambda c: 'log' in c.name, guild.channels)

        if not log_channel:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(send_messages=False, mention_everyone=False)
            }
            return await guild.create_text_channel(name='》mod-log', overwrites=overwrites)

    def enable_plugin(self, d_plugin, s_plugin, embed):
        d_id, d_name, d_information, d_command, d_usage, d_required_plugins, d_type = d_plugin
        req_plugin = dict(
            id=d_id,
            name=d_name,
            information=d_information,
            command=d_command,
            usage=d_usage,
            required_plugins=json.loads(d_required_plugins) if d_required_plugins else None,
            type=d_type
        )
        if d_required_plugins:
            for key, plugin in enumerate(req_plugin['required_plugins']):
                if plugin not in self.guild_plugins:
                    self.guild_plugins.append(plugin)
        self.guild_plugins.append(s_plugin)
        DB().execute('UPDATE servers SET plugins=? WHERE id=?', (json.dumps(self.guild_plugins), self.message.guild.id))
        return embed.add_field(name='Success', value='Succesfully enabled the following plugin: \n%s' % (
                    '%s\nwith requirements(if not previously enabled): \n%s' % (
            s_plugin, '\n'.join(req_plugin['required_plugins']) if req_plugin['required_plugins'] else 'None')))
