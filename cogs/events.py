import discord
from discord.ext import commands
from models.Server import Server
from models.User import User
from datetime import datetime
from checks import is_plugin_enabled
from cogs.levels import levels
import random


class EventCog:
    def __init__(self, bot):
        self.bot: discord.ext.commands.Bot = bot

    async def on_message_delete(self, message: discord.Message):
        log_channel: discord.TextChannel = discord.utils.get(message.guild.channels, name='tdb-logs')
        if log_channel:
            log_embed = discord.Embed(color=discord.colour.Colour.dark_gold(), title=f'Message deletion')
            log_embed.add_field(name='Message:', value=f'{message.content}; by {message.author.mention} has been deleted in channel <#{message.channel.id}>')
            await log_channel.send(embed=log_embed)

    async def on_member_remove(self, member: discord.Member):
        guild = Server.get_by_id(member.guild.id)
        guild.member_count -= 1
        guild.save()

        log_channel: discord.TextChannel = discord.utils.get(member.guild.channels, name='tdb-logs')
        if log_channel:
            log_embed = discord.Embed(color=discord.colour.Colour.dark_grey(), title=f'Server leave')
            log_embed.add_field(name=member.display_name, value=f'{member.mention} has left {guild.name}')
            await log_channel.send(embed=log_embed)

    async def on_member_join(self, member: discord.Member):
        guild = Server.get_by_id(member.guild.id)
        guild.member_count += 1
        guild.save()

        user = User.get_by_id(member.id)

        log_channel: discord.TextChannel = discord.utils.get(member.guild.channels, name='tdb-logs')
        if log_channel:
            log_embed = discord.Embed(color=discord.colour.Colour.green(), title=f'Server join')
            log_embed.add_field(name=member.display_name, value=f'{member.mention} has joined {guild.name}')
            await log_channel.send(embed=log_embed)

        if not user:
            user = User(user_id=member.id, avatar_url=member.avatar, created_at=member.created_at, discriminator=member.discriminator, mention=member.mention, name=member.name, display_name=member.display_name, plugins={}, last_xp=None)
            user.save()
        if type(guild.on_join) is dict:
            if guild.on_join.get('add_roles'):
                roles = [discord.utils.get(member.guild.roles, id=role) for role in guild.on_join['add_roles']]
                await member.add_roles(*roles)

            # if guild.on_join.get('validations') and guild.validations:
            #     message = f'To get full access to server: {ctx.guild.name} you must first go through some validations:'
            #     await member.send(message)
            #     import random
            #     for action, validation in enumerate(guild.validations):
            #         if action == 'gender' and validation.get('options'):
            #             option = random.choice(validation['options'])
            #             message = validation['message'] % option
            #         if action == 'age':
            #             message = validation
            #
            #         await member.send(message)
            #         message = await self.bot.wait_for('message', check=lambda user: user.id == member.id)
            #         channel = discord.utils.get(member.guild.channels, id=514068802917629973) # currently static for testing
            #         msg = f'Verification for {action} on user {member.display_name}: {message}'
            #         await channel.send(msg)

    async def on_message(self, message: discord.Message):
        user: User = User.get_by_id(message.author.id)
        author: discord.Member = message.author
        if not user:
            user = User(user_id=author.id, avatar_url=author.avatar, created_at=author.created_at, discriminator=author.discriminator, mention=author.mention, name=author.name, display_name=author.display_name, plugins={}, last_xp=None)
            user.save()
        if not is_plugin_enabled('levels') or message.author.bot:
            return False
        if not user.plugins.get('level_experience'):
            user.plugins['level_experience'] = 0
        if not user.plugins.get('prev_level'):
            user.plugins['prev_level'] = 0
        valid_when = datetime.utcfromtimestamp(user.plugins['level_experience'] + 12)
        current_time = datetime.now()

        if valid_when < current_time:
            user.last_xp = current_time.timestamp()
            user.plugins['level_experience'] += random.randint(1, 8)
            current_level = 0
            xp_required = 0
            for level, xp in enumerate(levels):
                xp_required += xp
                if user.plugins['level_experience'] > xp_required:
                    current_level = level + 1
            if current_level > user.plugins['prev_level']:
                user.plugins['prev_level'] = current_level
                await message.channel.send(f'Congratulations {message.author.mention}, you have succesfully leveled up and are now level {current_level}')
            user.save()

    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        ctx   : Context
        error : Exception"""

        # This prevents any commands with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, 'on_error'):
            return

        ignored = (commands.CommandNotFound,)

        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(error, 'original', error)

        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored):
            return

        if isinstance(error, commands.DisabledCommand):
            return await ctx.send(f'{ctx.command} has been disabled.')

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except:
                pass

        elif isinstance(error, commands.NotOwner):
            try:
                return await ctx.send(f'{ctx.command} requires you to be the owner.')
            except:
                pass

        elif isinstance(error, commands.MissingPermissions):
            try:
                return await ctx.send(f'{ctx.command} requires permissions you dont have.')
            except:
                pass

        elif isinstance(error, commands.CommandInvokeError):
            try:
                return await ctx.send(f'{error}')
            except:
                pass

        elif isinstance(error, commands.MissingRequiredArgument):
            try:
                return await ctx.send(f'Usage: >{ctx.command.signature}')
            except:
                pass

        elif isinstance(error, commands.CheckFailure):
            try:
                return await ctx.send(f'{error}')
            except:
                pass

        elif isinstance(error, commands.CommandOnCooldown):
            try:
                import re
                m, s = divmod(error.retry_after, 60)
                wait_untill = "%02dm:%02ds" % (m, s) if m > 0 else "%02ds" % s
                msg = re.sub('[0-9]+\.[0-9]{2}s', wait_untill, error.args[0])
                return await ctx.send(msg)
            except:
                pass

        else:
            return await ctx.send(f'{type(error).__name__}: {error}')

def setup(bot):
    bot.add_cog(EventCog(bot))
