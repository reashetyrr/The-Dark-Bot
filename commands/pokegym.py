import discord
import config
from models.DB import DB
from models.Command import Command
from models.User import User


class Pokegym(Command):
    def __init__(self, **kwargs):
        Command.__init__(self, **kwargs)

    async def execute(self):
        if not await self.run_test():
            return

        if self.author.guild_permissions.administrator and self.params[0] == 'setup':
            guild: discord.Guild = self.message.guild
            role = discord.utils.get(guild.roles, name='pokemon trainer')
            if not role:
                role = await guild.create_role(name='pokemon trainer')
            poke = await guild.create_category('Pokégyms', overwrites=discord.PermissionOverwrite())
        user = User.get_by_id(self.author.id)
        cmd = self.params.pop(0)

        if cmd == 'register' and not user.plugins.get('pokegym'):
            role = discord.utils.get(guild.roles, name='pokemon trainer')
            if not role:
                role = await guild.create_role(name='pokemon trainer')
            user.plugins['pokegym'] = dict(
                badges=[],
                team=[],
                role='trainer',
            )
            user.save()
            await self.author.add_roles(role)
            return await self.message.channel.send('Succesfully created your pokegym profile, use on the the following commands to setup your team: tdb!pokegym maketeam, tdb!pokegym mt, tdb!pokegym teambuild or tdb!pokegym tb')
        elif cmd == 'register' and user.plugins['pokegym']:
            return await self.message.channel.send('You have already registered.')

        if not user.plugins.get('pokegym'):
            return await self.message.channel.send('Please register your trainer acount first by using: tdb!pokegym register')

        if cmd in ('maketeam', 'mt', 'teambuild', 'tb'):
            return await self.message.channel.send('Coming soon')
