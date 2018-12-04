import discord
import config
from models.DB import DB
from models.Command import Command


class Commands(Command):
    def __init__(self, **kwargs):
        Command.__init__(self, **kwargs)

    async def execute(self):
        if not await self.run_test():
            return

        commands = self.get_commands()

        embed = discord.Embed(title='%s - Help' % self.message.guild.name, description='', color=config.embed_color, colour=config.embed_color)
        embed.add_field(name='Available commands:', value='\n'.join(commands), inline=False)

        await self.message.channel.purge(limit=1)
        return await self.message.channel.send(embed=embed)

    def get_commands(self):
        res = DB().fetch_all('SELECT * FROM plugins WHERE ?', (1,))
        commands = []
        for c in res:
            plugin_id, plugin_name, plugin_information, plugin_command, plugin_usage, plugin_required_plugins, plugin_type, plugin_aliases = c
            if (self.author.guild_permissions.administrator and plugin_type > 1) or plugin_type == 1:
                if plugin_name not in ['commands', 'nickname']:
                    commands.append('%s: %s' % (plugin_name, plugin_command))
        return commands
