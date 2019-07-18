import discord
from discord.ext import commands
from models.Server import Server
from models.User import User
from models.DB import DB
from datetime import datetime
from checks import is_plugin_activated
from cogs.levels import levels
import random
import json
import re
from models.rolemenu import Rolemenu
from models.rolemenu_emote import RolemenuEmote
import subprocess


async def on_message_delete(message: discord.Message):
    log_channel: discord.TextChannel = discord.utils.get(message.guild.channels, name='tdb-logs')
    guild: discord.Guild = message.guild
    if log_channel and is_plugin_activated(guild.id, 'logging'):
        log_embed = discord.Embed(color=discord.colour.Colour.dark_gold(), title=f'Message deletion')
        log_embed.add_field(name='Message:', value=f'{message.content}; by {message.author.mention} has been deleted in channel <#{message.channel.id}>')
        await log_channel.send(embed=log_embed)


# noinspection PyMethodMayBeStatic
class EventCog(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.ext.commands.Bot = bot

    async def bot_check(self, ctx):
        user: User = User.get_by_id(ctx.author.id)
        if user and user.banned:
            raise BannedException()
        return True

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return
        message_id = payload.message_id
        emoji = payload.emoji
        if emoji.id:
            emoji = json.dumps(dict(type=emoji.__class__.__name__, id=emoji.id))
        guild: discord.Guild = self.bot.get_guild(payload.guild_id)
        user: discord.Member = guild.get_member(payload.user_id)

        rolemenu = Rolemenu.get_by_message_id(message_id)
        if rolemenu and is_plugin_activated(guild.id, 'rolemenus'):
            role_name = RolemenuEmote.get_by_emoji(emoji, rolemenu.id)
            role: discord.Role = discord.utils.get(guild.roles, name=role_name.name)
            if role:
                await user.remove_roles(role)
            else:
                channel: discord.TextChannel = guild.get_channel(payload.channel_id)
                await channel.send(f'Found a broken rolemenu, the role "{role_name.name}" cannot be found, please contact an administrator')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return
        message_id = payload.message_id
        emoji = payload.emoji
        if emoji.id:
            emoji = json.dumps(dict(type=emoji.__class__.__name__, id=emoji.id))
        guild: discord.Guild = self.bot.get_guild(payload.guild_id)
        user: discord.Member = guild.get_member(payload.user_id)

        rolemenu = Rolemenu.get_by_message_id(message_id)
        if rolemenu and is_plugin_activated(guild.id, 'rolemenus'):
            role_name = RolemenuEmote.get_by_emoji(emoji, rolemenu.id)
            role = discord.utils.get(guild.roles, name=role_name.name)
            member: User = User.get_by_id(user_id=user.id)
            if role:
                await user.add_roles(role)
            else:
                channel: discord.TextChannel = guild.get_channel(payload.channel_id)
                await channel.send(f'Found a broken rolemenu, the role "{role_name.name}" cannot be found, please contact an administrator')

    @commands.Cog.listener()
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

    @commands.Cog.listener()
    async def on_member_update(self, old: discord.Member, current: discord.Member):
        if not is_plugin_activated(current.guild.id, 'stream') or current.bot:
            return

        found: bool = False
        stream: discord.Streaming = None
        for activity in current.activities:
            if activity.type == discord.ActivityType.streaming:
                found = True
                stream = activity

        if not found:
            return

        embed: discord.Embed = discord.Embed(title=f'Stream alert', color=discord.Color.green(), colour=discord.Color.green(), description=f'STREAM HYPEE!.')
        embed.set_thumbnail(url=current.avatar_url)

        guild: Server = Server.get_by_id(current.guild.id)
        gld: discord.Guild = current.guild
        stream_channel: discord.TextChannel = gld.get_channel(guild.custom_settings.get('stream_channel'))
        streaming_message = guild.custom_settings.get('stream_message', '{user} known on twitch as {twitch_name} has started streaming, check him/her out: {url}')
        embed.add_field(name=current.display_name, value=streaming_message.format(
            user=current.mention,
            twitch_name=stream.twitch_name,
            url=stream.url
        ))
        embed.set_footer(text=f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} CET')
        return await stream_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        def message_check(message: discord.Message):
            return member.id == message.author.id

        if member.name.lower() == 'ramzi':
            return await member.kick()

        guild = Server.get_by_id(member.guild.id)
        if guild.blacklisted:
            server: discord.Guild = member.guild
            owner: discord.Member = server.owner
            await owner.send(f'Your server {server.name} has been blacklisted, i shall therefore leave again.')
            return await member.guild.leave()
        guild.member_count += 1
        guild.save()

        user = User.get_by_id(member.id)

        if not user:
            user = User(user_id=member.id, avatar_url=member.avatar, created_at=member.created_at, discriminator=member.discriminator, mention=member.mention, name=member.name, display_name=member.display_name, plugins={}, last_xp=None, banned=False)
            user.save()

        if guild.custom_settings.get('welcome_channel'):
            main_channel: discord.TextChannel = discord.utils.get(member.guild.channels, id=guild.custom_settings['welcome_channel'])
        else:
            main_channel: discord.TextChannel = discord.utils.find(lambda c: 'general' in c.name.lower() or 'welcome' in c.name.lower(), member.guild.channels)
        if main_channel and is_plugin_activated(member.guild.id, 'welcome message'):
            embed: discord.Embed = discord.Embed(title=f'Event', color=discord.Color.green(), colour=discord.Color.green(), description=f'User has joined the guild.')
            embed.set_thumbnail(url=member.avatar_url)
            username: str = user.display_name
            mention: str = user.mention
            guild_name: str = guild.name
            embed.add_field(name=member.display_name, value=guild.custom_settings.get('welcome_message', '{mention} has joined {guild_name}').format(
                mention=mention,
                username=username,
                guild_name=guild_name
            ))
            embed.set_footer(text=f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} CET')
            await main_channel.send(embed=embed)

        if type(guild.on_join) is dict:
            if guild.on_join.get('add_roles'):
                roles = [discord.utils.get(member.guild.roles, id=role) for role in guild.on_join['add_roles']]
                await member.add_roles(*roles)

        # if is_plugin_activated(member.guild.id, 'security.raid'):
        #     msg: discord.Message = await self.bot.wait_for('message', check=message_check)
        #     with open(f'configs/messages.json', 'w+') as fp:
        #         first_messages: dict = json.loads(fp.read())
        #         if not first_messages.get(member.id):
        #             first_messages[member.id] = []
        #         first_messages[member.id].append(msg.clean_content)
        #         with open(f'configs/blacklist_messages.json', 'w+') as blfp:
        #             blacklisted_messages: list = json.loads(blfp.read())
        #             if list(first_messages.values()).count(msg.clean_content) >= 5:
        #                 ban_list: list = [key for key, value in first_messages.items() if value == msg.clean_content]
        #                 ban_list.append(member.id)
        #                 blacklisted_messages.append(msg.clean_content)
        #                 blfp.write(json.dumps(blacklisted_messages))
        #                 for m in ban_list:
        #                     if log_channel:
        #                         log_embed = discord.Embed(color=discord.colour.Colour.dark_red(), title=f'Raid ban')
        #                         log_embed.add_field(name=member.display_name, value=f'{member.mention} has been banned for raiding')
        #                         await log_channel.send(embed=log_embed)
        #                     await m.ban(f'You have been caught with by the raid protection.')
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

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        user: User = User.get_by_id(message.author.id)
        guild: discord.Guild = message.guild
        try:
            db_guild: Server = Server.get_by_id(guild.id)
            if db_guild.blacklisted:
                guild_owner: discord.Member = guild.owner
                try:
                    await guild_owner.send(f'Your server "{guild.name}" has been blacklisted, i have left your server')
                except:
                    pass
                return await guild.leave()
        except:
            pass # dm no guild found

        c: str = message.clean_content
        channel: discord.TextChannel = message.channel
        author: discord.Member = message.author
        if await self.bot.is_owner(author) and c.startswith('gen_invite'):
            guild_id = int(c.split(' ')[1])
            g: discord.Guild = self.bot.get_guild(guild_id)

            general_channel: discord.TextChannel = g.text_channels[0]
            invite: discord.Invite = await general_channel.create_invite(reason='', max_uses=1)

            await author.send(str(invite))
        if guild:
            s: Server = Server.get_by_id(guild.id)
            current_timestamp = datetime.now().timestamp()
            change_timestamp = False

            if author.bot:
                return False

            if not user:
                user = User(user_id=author.id, avatar_url=author.avatar, created_at=author.created_at, discriminator=author.discriminator, mention=author.mention, name=author.name, display_name=author.display_name, plugins={}, last_xp=None, banned=False)
                user.save()

            if is_plugin_activated(guild.id, 'security.filter.links'):
                if 'promote' not in channel.name.lower() and 'partner' not in channel.name.lower() and not c.startswith('>') and channel.id not in s.custom_settings.get('links_allowed', []):
                    uri = c
                    link_found = re.compile('.*https?://(.+)\s?').search(uri)
                    if link_found:
                        uri = link_found.group(1)

                        response = subprocess.Popen(f"ping -n 1 {uri}", stdout=subprocess.PIPE).communicate()[0]
                        # response = os.system(f"ping -n 1 {c}") # windows
                        # response = os.system("ping -c 1 " + c) # linux
                        if 'Reply' in response.decode('utf-8') or c.startswith('http://') or c.startswith('https://'):
                            reason = 'Posted an link in an channel which is not for that purpose'
                            DB().execute(query='INSERT INTO warnings(guild_id, user_id, reason) VALUES(%s,%s,%s)', params=(message.guild.id, author.id, reason))
                            warnings = DB().fetch_all(query='SELECT * FROM warnings WHERE guild_id=%s AND user_id=%s', params=(message.guild.id, author.id))

                            self.bot.dispatch('member_warned', author, reason, warnings)
                            # log_channel: discord.TextChannel = discord.utils.get(message.guild.channels, name='tdb-logs')

                            # if len(warnings) == 5:
                            #     await author.kick(reason='Received 5 warnings, therefore automatically kicked.')
                            #     embed = discord.Embed(title=f'User {author.display_name} kicked', description=f'User {author.display_name} received his 5th warning, therefore automagically kicked.', color=author.color)
                            #     if log_channel and is_plugin_activated(guild.id, 'logging'):
                            #         log_embed = discord.Embed(color=discord.colour.Colour.dark_red(), title=f'User warned')
                            #         log_embed.add_field(name='Event:', value=f'{author.mention}has automagically been kicked for receiving his/her fifth warning')
                            #         await log_channel.send(embed=log_embed)
                            #
                            # elif len(warnings) == 10:
                            #     await author.ban(reason='Received 10 warnings, therefore automatically banned.')
                            #     embed = discord.Embed(title=f'User {author.display_name} banned', description=f'User {author.display_name} received his 10th warning, therefore automagically banned.', color=author.color)
                            #     if log_channel and is_plugin_activated(guild.id, 'logging'):
                            #         log_embed = discord.Embed(color=discord.colour.Colour.dark_red(), title=f'User warned')
                            #         log_embed.add_field(name='Event:', value=f'{author.mention}has automagically been banned for receiving his/her tenth warning')
                            #         await log_channel.send(embed=log_embed)
                            #
                            # else:
                            embed = discord.Embed(title=f'User {author.display_name} warned', description=f'User {author.display_name} has been warned with reason: {reason}.', color=author.color)

                            await message.delete()
                            return await channel.send(embed=embed)

            # if is_plugin_activated(guild.id, 'security.spam'):
            #     if not user.plugins.get('last_five_messages'):
            #         user.plugins['last_five_messages'] = []
            #         user.save()
            #
            #     if not user.plugins.get('spam_counter'):
            #         user.plugins['spam_counter'] = 0
            #         user.save()
            #
            #     if 'spam' not in message.channel.name.lower() and user.plugins['last_five_messages'].count(c) > 3:
            #         await channel.purge(limit=100, check=lambda m: m.author == author)
            #         user.plugins['spam_counter'] += 1
            #
            #     if user.plugins['spam_counter'] >= 5:
            #         log_channel: discord.TextChannel = discord.utils.get(message.guild.channels, name='tdb-logs')
            #         if log_channel and is_plugin_activated(guild.id, 'logging'):
            #             log_embed = discord.Embed(color=discord.colour.Colour.dark_grey(), title=f'Security spam alert')
            #             log_embed.add_field(name=author.display_name, value=f'{author.mention} has been kicked for spamming in {channel.mention}')
            #             await log_channel.send(embed=log_embed)
            #         return await author.kick(reason=f'Spamming is not allowed!')
            #     user.plugins['last_five_messages'].append(c)
            #     user.save()

            if is_plugin_activated(guild.id, 'currency'):
                if not user.plugins.get('currency'):
                    user.plugins['currency'] = 0

                if (user.last_xp + 15) < current_timestamp:
                    change_timestamp = True
                    user.plugins['currency'] += random.randint(5, 25)
                    user.save()

            if is_plugin_activated(guild.id, 'levels'):
                if not user.plugins.get('level_experience'):
                    user.plugins['level_experience'] = 0
                if not user.plugins.get('prev_level'):
                    user.plugins['prev_level'] = 0

                if (user.last_xp + 10) < current_timestamp:
                    change_timestamp = True
                    user.plugins['level_experience'] += random.randint(1, 8)
                    current_level = 0
                    xp_required = 0
                    for level, xp in enumerate(levels):
                        xp_required += xp
                        if user.plugins['level_experience'] > xp_required:
                            current_level = level + 1
                    if current_level > user.plugins['prev_level']:
                        user.plugins['prev_level'] = current_level
                        reward_multiplier = random.randint(2, 8)
                        mention, level, guild_name, username, added_coins, total_coins, currency = user.mention, current_level, guild.name, author.display_name, 0, 0, s.currency_name

                        message_to_send: str = s.custom_settings.get('level_up_message', 'Congratulations {mention}, you have succesfully leveled up and are now level {level:,}')
                        # message_to_send = f'Congratulations {message.author.mention}, you have succesfully leveled up and are now level {current_level:,}'
                        if is_plugin_activated(guild.id, 'currency'):
                            added_coins = current_level * reward_multiplier
                            # message_to_send += f', You have been rewarded with {coins_to_receive:,}{currency_name}'
                            user.plugins['currency'] += added_coins
                            total_coins = user.plugins['currency']

                        lvl_msg = s.custom_settings.get('level_up_message')
                        if lvl_msg and lvl_msg != 'None':
                            await message.channel.send(message_to_send.format(
                                mention=mention,
                                level=level,
                                guild_name=guild_name,
                                username=username,
                                added_coins=added_coins,
                                total_coins=total_coins,
                                currency=currency if currency else 'Coins',
                            ))
                        while current_level > 0:
                            level_role: discord.Role = discord.utils.get(message.guild.roles, name=f'lvl {current_level}')
                            if level_role:
                                await message.author.add_roles(level_role)
                            current_level -= 1
                    user.save()
            if change_timestamp:
                user.last_xp = current_timestamp
                user.save()

            # if not c.startswith('>'):
            #     with open(f'messages/{datetime.now().date()}-h{datetime.now().hour}.txt', 'a+', encoding='utf-8') as fp:
            #         fp.write(f'{c}\n')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        ctx   : Context
        error : Exception"""

        # This prevents any commands with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, 'on_error'):
            return

        ignored = (commands.CommandNotFound, BannedException)

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


class BannedException(Exception):
    pass


def setup(bot):
    bot.add_cog(EventCog(bot))
