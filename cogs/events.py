import discord
import os
from discord.ext import commands
from models.Server import Server
from models.User import User
from models.DB import DB
from datetime import datetime
from checks import is_plugin_activated
from cogs.levels import levels
import random
from models.rolemenu import Rolemenu
from models.rolemenu_emote import RolemenuEmote
import subprocess


class EventCog:
    def __init__(self, bot):
        self.bot: discord.ext.commands.Bot = bot

    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return
        message_id = payload.message_id
        emoji = payload.emoji
        guild: discord.Guild = self.bot.get_guild(payload.guild_id)
        user: discord.Member = guild.get_member(payload.user_id)

        rolemenu = Rolemenu.get_by_message_id(message_id)
        if rolemenu and is_plugin_activated(guild.id, 'rolemenus'):
            role_name = RolemenuEmote.get_by_emoji(emoji, rolemenu.id)
            role = discord.utils.get(guild.roles, name=role_name.name)
            if role:
                await user.remove_roles(role)
            else:
                channel: discord.TextChannel = guild.get_channel(payload.channel_id)
                await channel.send(f'Found a broken rolemenu, the role "{role_name.name}" cannot be found, please contact an administrator')

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return
        message_id = payload.message_id
        emoji = payload.emoji
        guild: discord.Guild = self.bot.get_guild(payload.guild_id)
        user: discord.Member = guild.get_member(payload.user_id)

        rolemenu = Rolemenu.get_by_message_id(message_id)
        if rolemenu and is_plugin_activated(guild.id, 'rolemenus'):
            role_name = RolemenuEmote.get_by_emoji(emoji, rolemenu.id)
            role = discord.utils.get(guild.roles, name=role_name.name)
            if role:
                await user.add_roles(role)
            else:
                channel: discord.TextChannel = guild.get_channel(payload.channel_id)
                await channel.send(f'Found a broken rolemenu, the role "{role_name.name}" cannot be found, please contact an administrator')

    async def on_message_delete(self, message: discord.Message):
        log_channel: discord.TextChannel = discord.utils.get(message.guild.channels, name='tdb-logs')
        guild: discord.Guild = message.guild
        if log_channel and is_plugin_activated(guild.id, 'logging'):
            log_embed = discord.Embed(color=discord.colour.Colour.dark_gold(), title=f'Message deletion')
            log_embed.add_field(name='Message:', value=f'{message.content}; by {message.author.mention} has been deleted in channel <#{message.channel.id}>')
            await log_channel.send(embed=log_embed)

    async def on_member_remove(self, member: discord.Member):
        guild = Server.get_by_id(member.guild.id)
        guild.member_count -= 1
        guild.save()

        log_channel: discord.TextChannel = discord.utils.get(member.guild.channels, name='tdb-logs')
        if log_channel and is_plugin_activated(guild.id, 'logging'):
            log_embed = discord.Embed(color=discord.colour.Colour.dark_grey(), title=f'Server leave')
            log_embed.add_field(name=member.display_name, value=f'{member.mention} has left {guild.name}')
            await log_channel.send(embed=log_embed)

        main_channel: discord.TextChannel = discord.utils.get(member.guild.channels, name="general-chat")
        if main_channel:
            log_embed = discord.Embed(color=discord.colour.Colour.dark_grey(), title=f'Server leave')
            log_embed.add_field(name=member.display_name, value=f'{member.mention} has left {guild.name}')
            await main_channel.send(embed=log_embed)

    async def on_member_join(self, member: discord.Member):
        guild = Server.get_by_id(member.guild.id)
        if guild.blacklisted:
            server: discord.Guild = member.guild
            owner: discord.Member = server.owner
            await owner.send(f'Your server {server.name} has been blacklisted, i shall therefore leave again.')
            return await member.guild.leave()
        guild.member_count += 1
        guild.save()

        user = User.get_by_id(member.id)

        log_channel: discord.TextChannel = discord.utils.get(member.guild.channels, name='tdb-logs')
        if log_channel:
            log_embed = discord.Embed(color=discord.colour.Colour.green(), title=f'Server join')
            log_embed.add_field(name=member.display_name, value=f'{member.mention} has joined {guild.name}')
            await log_channel.send(embed=log_embed)

        main_channel: discord.TextChannel = discord.utils.get(member.guild.channels, name="general-chat")
        if main_channel:
            log_embed = discord.Embed(color=discord.colour.Colour.green(), title=f'Server join')
            log_embed.add_field(name=member.display_name, value=f'{member.mention} has joined {guild.name}')
            await main_channel.send(embed=log_embed)

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
        guild: discord.Guild = message.guild
        c: str = message.clean_content
        channel: discord.TextChannel = message.channel
        author: discord.Member = message.author

        if author.bot:
            return False

        if not user:
            user = User(user_id=author.id, avatar_url=author.avatar, created_at=author.created_at, discriminator=author.discriminator, mention=author.mention, name=author.name, display_name=author.display_name, plugins={}, last_xp=None)
            user.save()

        if is_plugin_activated(guild.id, 'security.filter.links'):
            if 'promote' not in channel.name.lower() and 'partner' not in channel.name.lower() and not c.startswith('>'):
                uri = c
                if c.startswith('http://'):
                    uri = c[7:]
                elif c.startswith('https://'):
                    uri = c[8:]

                response = subprocess.Popen(f"ping -n 1 {uri}", stdout=subprocess.PIPE).communicate()[0]
                # response = os.system(f"ping -n 1 {c}") # windows
                # response = os.system("ping -c 1 " + c) # linux
                if 'Reply' in response.decode('utf-8') or c.startswith('http://') or c.startswith('https://'):
                    reason = 'Posted an link in an channel which is not for that purpose'
                    DB().execute(query='INSERT INTO warnings(guild_id, user_id, reason) VALUES(?,?,?)', params=(message.guild.id, author.id, reason))
                    warnings = DB().fetch_all(query='SELECT * FROM warnings WHERE guild_id=? AND user_id=?', params=(message.guild.id, author.id))

                    log_channel: discord.TextChannel = discord.utils.get(message.guild.channels, name='tdb-logs')
                    if log_channel and is_plugin_activated(guild.id, 'logging'):
                        log_embed = discord.Embed(color=discord.colour.Colour.dark_red(), title=f'User warned')
                        log_embed.add_field(name='Event:', value=f'{author.mention} has automatically been warned for: {reason}')
                        await log_channel.send(embed=log_embed)

                    if len(warnings) == 5:
                        await author.kick(reason='Received 5 warnings, therefore automatically kicked.')
                        embed = discord.Embed(title=f'User {author.display_name} kicked', description=f'User {author.display_name} received his 5th warning, therefore automagically kicked.', color=author.color)
                        if log_channel and is_plugin_activated(guild.id, 'logging'):
                            log_embed = discord.Embed(color=discord.colour.Colour.dark_red(), title=f'User warned')
                            log_embed.add_field(name='Event:', value=f'{member.mention}has automagically been kicked for receiving his/her fifth warning')
                            await log_channel.send(embed=log_embed)

                    elif len(warnings) == 10:
                        await author.ban(reason='Received 10 warnings, therefore automatically banned.')
                        embed = discord.Embed(title=f'User {author.display_name} banned', description=f'User {author.display_name} received his 10th warning, therefore automagically banned.', color=author.color)
                        if log_channel and is_plugin_activated(guild.id, 'logging'):
                            log_embed = discord.Embed(color=discord.colour.Colour.dark_red(), title=f'User warned')
                            log_embed.add_field(name='Event:', value=f'{member.mention}has automagically been banned for receiving his/her tenth warning')
                            await log_channel.send(embed=log_embed)

                    else:
                        embed = discord.Embed(title=f'User {author.display_name} warned', description=f'User {author.display_name} has been warned with reason: {reason}.', color=author.color)

                    await message.delete()
                    return await channel.send(embed=embed)

        if is_plugin_activated(guild.id, 'security.spam'):
            if not user.plugins.get('last_five_messages'):
                user.plugins['last_five_messages'] = []
                user.save()

            if not user.plugins.get('spam_counter'):
                user.plugins['spam_counter'] = 0
                user.save()

            if 'spam' not in message.channel.name.lower() and user.plugins['last_five_messages'].count(c) > 3:
                await channel.purge(limit=100, check=lambda m: m.author == author)
                user.plugins['spam_counter'] += 1

            if user.plugins['spam_counter'] >= 5:
                log_channel: discord.TextChannel = discord.utils.get(message.guild.channels, name='tdb-logs')
                if log_channel and is_plugin_activated(guild.id, 'logging'):
                    log_embed = discord.Embed(color=discord.colour.Colour.dark_grey(), title=f'Security spam alert')
                    log_embed.add_field(name=author.display_name, value=f'{author.mention} has been kicked for spamming in {channel.mention}')
                    await log_channel.send(embed=log_embed)
                return await author.kick(reason=f'Spamming is not allowed!')
            user.plugins['last_five_messages'].append(c)
            user.save()

        if is_plugin_activated(guild.id, 'levels'):
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
                    while current_level > 0:
                        level_role: discord.Role = discord.utils.get(message.guild.roles, name=f'lvl {current_level}')
                        if level_role:
                            await message.author.add_roles(level_role)
                        current_level -= 1
                user.save()

        if not c.startswith('>'):
            with open(f'messages/{datetime.now().date()}-h{datetime.now().hour}.txt', 'a+', encoding='utf-8') as fp:
                fp.write(f'{c}\n')

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
