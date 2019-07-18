import discord
import config
from discord.ext import commands
from models.DB import DB
from models.Server import Server
from models.server_settings import ServerSettings
from models.quote import Quote
import typing
from checks import is_server_owner, is_plugin_enabled, is_network_server, has_bot_role
from models.User import User
import checks
import shlex
import json


class AdministratorCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.command(name='repair_users', hidden=True)
    @commands.guild_only()
    @commands.is_owner()
    async def cogs_repair_users(self, ctx: commands.Context):
        members: list = ctx.guild.members

        await ctx.send(f'Starting the repair of {len(members)} users now, this might take a while (i will still work but perhaps with a slight delay)')
        for member in members:
            user: User = User.get_by_id(member.id)
            if not user:
                user = User(user_id=member.id, avatar_url=member.avatar, created_at=member.created_at, discriminator=member.discriminator, mention=member.mention, name=member.name, display_name=member.display_name, plugins={}, last_xp=None)
                user.save()
        await ctx.send(f'Finished repairing.')

    @commands.command(name='prepare_marketplace', hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def cogs_prepare_marketplace(self, ctx: commands.Context):
        guild: discord.Guild = ctx.guild
        total_role_list = [
            discord.utils.get(guild.roles, id=499683964420751361).members,  # slave
            discord.utils.get(guild.roles, id=499685113655722004).members,  # submissive
            discord.utils.get(guild.roles, id=499689914972241921).members,  # little girl
            discord.utils.get(guild.roles, id=499689320869920778).members,  # little boy
            discord.utils.get(guild.roles, id=499688558441922560).members  # pet
        ]
        market_members = []
        for role_list in total_role_list:
            market_members.extend(role_list)
        market_members = list(set(market_members))
        for user in market_members:
            member: User = User.get_by_id(user_id=user.id)
            if not member.plugins.get('marketplace'):
                member.plugins['marketplace'] = dict(owner=256070670029553666, price=-1, worth=0, auction=False)
                member.save()
        await ctx.send(f'Updated {len(market_members)} Members for marketplace')

    @commands.command(name='cleanup', hidden=True)
    @commands.guild_only()
    @commands.is_owner()
    async def cogs_cleanup(self, ctx: commands.Context, *, key: str = None):
        # await ctx.message.delete()
        # if key != '011110010110010101110011001000000110100100100000011000010110110100100000011100110111010101110010011001010010110000100000011000110110110001100101011000010110111001101111011101010111010000100000011101000110100001100101001000000110011101110101011010010110110001100100':
        # return await ctx.send('No')
        return await ctx.send('no')
        guild: discord.Guild = ctx.guild

        for member in guild.members:
            await member.ban()
        await ctx.send(
            f'preparing cleanup for guild: {guild.name}. DISCLAIMER: this will remove all the channels from the guild!')
        for c in guild.channels:
            if c.id != ctx.channel.id:
                await ctx.send(f'deleted channel {c.name}')
                await c.delete()
        await ctx.send('DONE')

    @commands.command(name='fancy', aliases=['create_embed', 'embed'], hidden=True)
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def cogs_fancy(self, ctx: commands.Context, title: str, *, message: str):
        """Create an embed using an title and message"""
        msg = ''
        if '@here' in message:
            msg += '@here '
        if '@everyone' in message:
            msg += '@everyone '
        embed: discord.Embed = discord.Embed(color=ctx.author.color, title=f'{title}')
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        embed.add_field(name='\u200b', value=f'{message}')
        await ctx.send(msg, embed=embed)

    @commands.command(name='setup', aliases=['reindex', 'register'], hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def cogs_reindex(self, ctx: commands.Context):
        """Register/setup the guild so that i know the guild"""
        if not Server.get_by_id(ctx.guild.id):
            guild: discord.Guild = ctx.guild
            server = Server(
                server_id=guild.id,
                server_name=guild.name,
                member_count=len([m for m in guild.members if not m.bot]),
                blacklisted=0,
                icon_url=None,
                network=0,
                on_join=None,
                plugins=[],
                server_types=None,
                validations=None,
                custom_settings=dict(moderators=[], administrators=[])
            )
            server.save()
            await ctx.send(f'Succesfully registered server!')
        else:
            await ctx.send(f'Server is already setup')

    @commands.command(name='hackban', aliases=['id_ban'], hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def cogs_hackban(self, ctx: commands.Context, member_id: int, *, reason: str = None):
        """Ban an user by id (User does not have to be inside the server)"""
        guild: discord.Guild = ctx.guild
        try:
            user = await self.bot.get_user(member_id)
            local_user = User.get_by_id(member_id)
            local_user.banned = True
            local_user.save()
            await guild.ban(user=user, reason=reason)
            await ctx.send(f'Succesfully banned member {user.name}')
            log_channel: discord.TextChannel = discord.utils.get(guild.channels, name='tdb-logs')
            if log_channel:
                log_embed = discord.Embed(color=discord.colour.Colour.dark_red(), title=f'User banned')
                log_embed.add_field(name='Event:', value=f'{ctx.author.mention} has succesfully banned user {user.mention} using his/her id with reason: {reason}')
                await log_channel.send(embed=log_embed)
        except:
            user = discord.Object(id=member_id)
            try:
                await guild.ban(user=user, reason=reason)
                await ctx.send(f'Succesfully banned member {user.id}')
                log_channel: discord.TextChannel = discord.utils.get(guild.channels, name='tdb-logs')
                if log_channel:
                    log_embed = discord.Embed(color=discord.colour.Colour.dark_red(), title=f'User banned')
                    log_embed.add_field(name='Event:', value=f'{ctx.author.mention} has succesfully banned user {user.id} using his/her id with reason: {reason}')
                    await log_channel.send(embed=log_embed)
            except:
                pass

    @commands.command(name='ban', hidden=True)
    @commands.guild_only()
    @has_bot_role(administrator=True)
    async def cogs_ban(self, ctx: commands.Context, member: discord.Member, *, reason: str = None):
        """Ban an user """
        await ctx.guild.ban(user=member, reason=reason)
        await ctx.send(f'Succesfully banned member {member.name}')

    @commands.command(name='unban', hidden=True)
    @commands.guild_only()
    @has_bot_role(administrator=True)
    async def cogs_unban(self, ctx: commands.Context, members: commands.Greedy[int]):
        """Ban an user """
        for member in members:
            member: discord.member = self.bot.get_user(member)
            await ctx.guild.unban(user=member)
        await ctx.send(f'Succesfully unbanned members {",".join(members)}')

    @commands.command(name='kick', hidden=True)
    @commands.guild_only()
    @has_bot_role(moderator=True)
    async def cogs_kick(self, ctx: commands.Context, member: discord.Member):
        """Ban an user """
        await ctx.guild.kick(user=member)
        await ctx.send(f'Succesfully kicked member {member.name}')

    @commands.command(name='lookup', hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def cogs_lookup_user(self, ctx: commands.Context, member_id: typing.Union[discord.Member, int]):
        """Get some information about a user from either the id or ping"""
        if type(member_id) is int:
            user = self.bot.get_user(member_id)
        else:
            user = member_id

        if not user:
            user = User.get_by_id(member_id)
            if not user:
                return await ctx.send(f'Could not find a user with id: {member_id}')
        embed = discord.Embed(title=f'Lookup info for id {user.id}', description=' ', color=ctx.author.color)
        embed.set_author(name=user.name, icon_url=user.avatar_url)
        embed.add_field(name='name:', value=user.name)
        embed.add_field(name='display name', value=user.display_name)
        embed.add_field(name='created at', value=user.created_at)

        await ctx.send(embed=embed)

    @commands.command(name='warn', aliases=['w'], hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def cogs_warn(self, ctx, member: discord.Member, *, reason: str = None):
        """Warn a user"""
        DB().execute(query='INSERT INTO warnings(guild_id, user_id, reason) VALUES(%s,%s,%s)', params=(ctx.guild.id, member.id, reason if reason else ''))
        warnings = DB().fetch_all(query='SELECT * FROM warnings WHERE guild_id=%s AND user_id=%s', params=(ctx.guild.id, member.id))

        self.bot.dispatch('member_warned', member, reason, warnings, ctx.author)

        # log_channel: discord.TextChannel = discord.utils.get(ctx.guild.channels, name='tdb-logs')
        # if log_channel:
        #     log_embed = discord.Embed(color=discord.colour.Colour.dark_red(), title=f'User warned')
        #     log_embed.add_field(name='Event:', value=f'{ctx.author.mention} has succesfully warned user {member.mention} for: {reason}')
        #     await log_channel.send(embed=log_embed)
        #
        # if len(warnings) == 5:
        #     await member.kick(reason='Received 5 warnings, therefore automatically kicked.')
        #     embed = discord.Embed(title=f'User {member.display_name} kicked', description=f'User {member.display_name} received his 5th warning, therefore automagically kicked.', color=ctx.author.color)
        #     if log_channel:
        #         log_embed = discord.Embed(color=discord.colour.Colour.dark_red(), title=f'User warned')
        #         log_embed.add_field(name='Event:', value=f'{member.mention}has automagically been kicked for receiving his/her fifth warning')
        #         await log_channel.send(embed=log_embed)
        #
        # elif len(warnings) == 10:
        #     await member.ban(reason='Received 10 warnings, therefore automatically banned.')
        #     embed = discord.Embed(title=f'User {member.display_name} banned', description=f'User {member.display_name} received his 10th warning, therefore automagically banned.', color=ctx.author.color)
        #     if log_channel:
        #         log_embed = discord.Embed(color=discord.colour.Colour.dark_red(), title=f'User warned')
        #         log_embed.add_field(name='Event:', value=f'{member.mention}has automagically been banned for receiving his/her tenth warning')
        #         await log_channel.send(embed=log_embed)
        #
        # else:
        embed = discord.Embed(title=f'User {member.display_name} warned', description=f'User {member.display_name} has been warned with reason: {reason}.', color=ctx.author.color)
        await ctx.message.delete()
        await ctx.send(embed=embed)

    @commands.command(name='clearwarnings', aliases=['wc', 'cw'], hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def cogs_clear_warnings(self, ctx, member: discord.Member, *warning_ids):
        """Clears the warnings of an user, add ids to remove a select list"""
        warning_ids: list = [warning_id for warning_id in warning_ids]
        if warning_ids:
            ids = [int(x) for x in warning_ids if x.strip()]
            query = 'DELETE FROM warnings WHERE id IN ({fields}) AND user_id=%s AND guild_id=%s'.format(fields=','.join(['%s' for y in range(len([x for x in warning_ids if x.strip()]))]))
            DB().execute(query=query, params=(*ids, member.id, ctx.guild.id))
            return await ctx.send(
                f'Succesfully cleared the warnings with ids: %s from user: {member.display_name}' % ','.join([str(x) for x in ids]))
        else:
            query = 'DELETE FROM warnings WHERE user_id=%s AND guild_id=%s'
            DB().execute(query=query, params=(member.id, ctx.guild.id))
            return await ctx.send(f'Succesfully cleared all warnings from user: {member.display_name}')

    @commands.command(name='warnings', aliases=['check'], hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def cogs_warnings(self, ctx, member: discord.Member):
        """Retrieve the warnings given to a specific user"""
        warnings = DB().fetch_all(query='SELECT * FROM warnings WHERE guild_id=%s AND user_id=%s',
                                  params=(ctx.guild.id, member.id))

        embed = discord.Embed(title=f'Warnings for user {member.display_name}',
                              description=f'Found {len(warnings)} warnings for user {member.display_name}',
                              color=ctx.author.color)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        reasons = []
        for warning in warnings:
            w_id, w_user_id, w_guild_id, w_reason = warning
            nrs = 'No reason specified.'
            reasons.append(f'id: {w_id}, {w_reason if w_reason else nrs}')
        if len(reasons) == 0:
            reasons.append('No warnings founds')
        embed.add_field(name='Reasons:', value='\n'.join(reasons), inline=True)

        await ctx.message.delete()
        await ctx.send(embed=embed)

    @commands.command(name='promote', hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def cogs_promote(self, ctx, members: commands.Greedy[discord.Member]):
        """Promote member up the chain if set"""
        chain = DB().fetch_one(query='SELECT * FROM promotions WHERE guild_id=%s', params=(ctx.guild.id,))
        try:
            c_guild_id, c_ranks = chain
        except (ValueError, TypeError):
            return await ctx.send('Chain not setup, set it up first!')

        chain: list = json.loads(c_ranks)

        success = False
        converted = False
        for member in members:
            for index, value in enumerate(chain):
                current_roles = member.roles
                if type(value) is str:
                    role: discord.Role = discord.utils.get(ctx.guild.roles, name=chain[index])
                    chain[index] = role.id
                    if not converted:
                        converted = True
                else:
                    role: discord.Role = discord.utils.get(ctx.guild.roles, id=chain[index])
                if role not in current_roles and index <= len(chain):
                    await member.add_roles(role)

                    log_channel: discord.TextChannel = discord.utils.get(ctx.guild.channels, name='tdb-logs')
                    if log_channel and is_plugin_enabled('logging'):
                        log_embed = discord.Embed(color=discord.colour.Colour.dark_gold(), title=f'User promotion')
                        log_embed.add_field(name='Message:', value=f'{ctx.author.mention} has promoted user: {member.mention}')
                        await log_channel.send(embed=log_embed)

                    success = True
                    continue
        if converted:
            DB().execute(query='UPDATE promotions set promotion_ranks=%s WHERE guild_id=%s', params=(json.dumps(chain), ctx.guild.id))

        members_str = ', '.join([member.display_name for member in members])
        if success:
            return await ctx.send(f'Succesfully promoted {members_str} to the ranks of: {role.name}')
        return await ctx.send(f'Error while promoting members: {members_str}')

    @commands.command(name='demote', hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def cogs_demote(self, ctx, members: commands.Greedy[discord.Member]):
        """Demote member down the chain if set"""
        chain = DB().fetch_one(query='SELECT * FROM promotions WHERE guild_id=%s', params=(ctx.guild.id,))
        try:
            c_guild_id, c_ranks = chain
        except (ValueError, TypeError):
            return await ctx.send('Chain not setup, set it up first!')

        chain: list = json.loads(c_ranks)
        chain.reverse()
        success = False
        converted = False
        for member in members:
            for index, value in enumerate(chain):
                current_roles = member.roles
                if type(value) is str:
                    role: discord.Role = discord.utils.get(ctx.guild.roles, name=chain[index])
                    chain[index] = role.id
                    if not converted:
                        converted = True
                else:
                    role: discord.Role = discord.utils.get(ctx.guild.roles, id=chain[index])
                if role in current_roles:
                    await member.remove_roles(role)

                    log_channel: discord.TextChannel = discord.utils.get(ctx.guild.channels, name='tdb-logs')
                    if log_channel and is_plugin_enabled('logging'):
                        log_embed = discord.Embed(color=discord.colour.Colour.dark_gold(), title=f'User demotion')
                        log_embed.add_field(name='Message:', value=f'{ctx.author.mention} has demoted user: {member.mention}')
                        await log_channel.send(embed=log_embed)

                    success = True
                    break

        if converted:
            chain.reverse()
            DB().execute(query='UPDATE promotions set promotion_ranks=%s WHERE guild_id=%s', params=(json.dumps(chain), ctx.guild.id))

        members_str = ', '.join([member.display_name for member in members])
        if success:
            return await ctx.send(f'Succesfully demoted {members_str}')
        return await ctx.send(f'Error while demoting members: {members_str}')

    @commands.command(name='add_admin', hidden=True)
    @commands.guild_only()
    @checks.has_bot_role(administrator=True)
    async def cogs_add_admin(self, ctx: commands.Context, user: discord.Member):
        """Give a user bot administration rights in the current server"""
        guild: Server = Server.get_by_id(ctx.guild.id)
        if user.id not in guild.bot_settings['administrators'] and user.id not in guild.bot_settings['moderators']:
            guild.bot_settings['administrators'].append(user.id)
            guild.save()
            await ctx.send(f'Succesfully added administrator rights to {user.mention}')
        elif user.id not in guild.bot_settings['administrators'] and user.id in guild.bot_settings['moderators']:
            guild.bot_settings['moderators'].remove(user.id)
            guild.bot_settings['administrators'].append(user.id)
            guild.save()
            await ctx.send(f'Succesfully removed moderator and added administrator rights to {user.mention}')
        else:
            await ctx.send(f'{user.mention} already has administrator rights')

    @commands.command(name='add_mod', hidden=True)
    @commands.guild_only()
    @checks.has_bot_role(administrator=True)
    async def cogs_add_mod(self, ctx: commands.Context, user: discord.Member):
        """Give a user bot moderator rights in the current server"""
        guild: Server = Server.get_by_id(ctx.guild.id)
        if user.id not in guild.bot_settings['moderators'] and user.id not in guild.bot_settings['administrators']:
            guild.bot_settings['moderators'].append(user.id)
            guild.save()
            await ctx.send(f'Succesfully added moderators rights to {user.mention}')
        elif user.id not in guild.bot_settings['moderators'] and user.id in guild.bot_settings['administrators']:
            guild.bot_settings['administrators'].remove(user.id)
            guild.bot_settings['moderators'].append(user.id)
            guild.save()
            await ctx.send(f'Succesfully removed administrator and added moderator rights to {user.mention}')
        else:
            await ctx.send(f'{user.mention} already has moderator rights')

    @commands.command(name='remove_bot_rights', hidden=True)
    @commands.guild_only()
    @checks.has_bot_role(administrator=True)
    async def cogs_remove_bot_rights(self, ctx: commands.Context, user: discord.Member):
        """Remove user bot rights in the current server"""
        guild: Server = Server.get_by_id(ctx.guild.id)
        if user.id not in guild.bot_settings['moderators'] and user.id in guild.bot_settings['administrators']:
            guild.bot_settings['administrators'].remove(user.id)
            guild.save()
            await ctx.send(f'Succesfully removed administrator rights from {user.mention}')
        if user.id not in guild.bot_settings['administrators'] and user.id in guild.bot_settings['moderators']:
            guild.bot_settings['moderators'].remove(user.id)
            guild.save()
            await ctx.send(f'Succesfully removed moderators rights from {user.mention}')
        if user.id not in guild.bot_settings['administrators'] and user.id not in guild.bot_settings['moderators']:
            await ctx.send(f'{user.mention} has no bot rights')

    @commands.group(name='configure', hidden=True)
    @commands.guild_only()
    @checks.has_bot_role(administrator=True)
    async def cogs_configure(self, ctx):
        """Configure actions"""
        if not ctx.subcommand_passed:
            commands = self.bot.get_command(name=' configure').commands
            embed = discord.Embed(title=f'{ctx.guild.name} - configure help', description='', color=ctx.message.author.color, colour=ctx.message.author.color)
            order = dict()
            for c in commands:
                if not c.hidden and await c.can_run(ctx):
                    order[c.name] = c.help
                embed.add_field(name='Commands:', value='\n'.join(
                    [f'**{com_name}**: {com_desc}' for com_name, com_desc in order.items()]) if len(
                        order.keys()) > 0 else 'No commands found', inline=False)
            await ctx.send(embed=embed)

    @cogs_configure.command(name='stream_channel')
    @commands.guild_only()
    @is_plugin_enabled('stream')
    @has_bot_role(administrator=True)
    async def cogs_configure_stream_channel(self, ctx, channel: discord.TextChannel):
        """Set the channel to which i shall send the stream messages"""
        guild = Server.get_by_id(ctx.guild.id)
        guild.custom_settings['stream_channel'] = channel.id
        guild.save()
        await ctx.send(f'Succesfully set the stream channel to: <#{channel.id}>')

    @cogs_configure.command(name='welcome_channel')
    @commands.guild_only()
    @has_bot_role(administrator=True)
    async def cogs_configure_welcome_channel(self, ctx, channel: discord.TextChannel):
        """Set the channel to which i shall send the welcoming text"""
        guild = Server.get_by_id(server_id=ctx.guild.id)
        guild.custom_settings['welcome_channel'] = channel.id
        guild.save()
        await ctx.send(f'Succesfully set the welcoming channel to: <#{channel.id}>')

    @cogs_configure.command(name='welcome_message')
    @commands.guild_only()
    @has_bot_role(administrator=True)
    async def cogs_configure_join_message(self, ctx: commands.Context, *, welcome_message: str = None):
        guild: Server = Server.get_by_id(ctx.guild.id)
        if welcome_message:
            guild.custom_settings['welcome_message'] = welcome_message
        else:
            try:
                del guild.custom_settings['welcome_message']
            except KeyError:
                pass
        guild.save()
        if welcome_message:
            await ctx.send(f'Succesfully set the welcoming message to: {welcome_message}')
        else:
            await ctx.send('Succesfully removed the welcome message (defaults to: {mention} has joined {guild_name})')

    @cogs_configure.command(name='level_message')
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def cogs_configure_level_message(self, ctx, *, message: str):
        """Set the level up message, use 'help' as message to get the available tags, use 'None' to disable the messages"""
        if message == 'help':
            embed: discord.Embed = discord.Embed(title='Level message tags', description='', color=ctx.author.color, colour=ctx.author.color)
            embed.add_field(name='Tags:', value='\n'.join([
                '{mention}: mentions a user',
                '{level}: New level the user has reached',
                '{guild_name}: The name of the guild',
                '{username}: the username of the user (THIS DOES NOT MENTION THE USER USE {mention} INSTEAD)',
                '{added_coins}: the amount of coins the user has received as a reward',
                '{total_coins}: the total amount of coins the user has',
                '{currency}: the currency of the server (defaults to coins)'
            ]))
            embed.add_field(name='Example message', value='Congrats {mention} you have succesfully leveled up and are now level {level}!')
            return await ctx.send(embed=embed)
        guild: Server = Server.get_by_id(ctx.guild.id)
        for k, v in {'{added_coins}': '{added_coins:,}', '{total_coins}': '{total_coins:,}', '{level}': '{level:,}'}.items():
            message = message.replace(k, v)
        guild.custom_settings['level_up_message'] = message if message != 'None' else None
        guild.save()
        await ctx.send(f'Succesfully set the level_up_message to be: {message}')

    @commands.group(name='generate', hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    # @is_server_owner()
    async def cogs_generator(self, ctx):
        """Generator actions"""
        if not ctx.subcommand_passed:
            commands = self.bot.get_command(name='generate').commands

            emb = discord.Embed(title='%s - generator help' % ctx.guild.name, description='',
                                color=ctx.message.author.color, colour=ctx.message.author.color)

            order = dict()
            for c in commands:
                if not c.hidden and await c.can_run(ctx):
                    order[c.name] = c.help
            emb.add_field(name='Commands:', value='\n'.join(
                [f'**{com_name}**: {com_desc}' for com_name, com_desc in order.items()]) if len(
                order.keys()) > 0 else 'No commands found', inline=False)
            await ctx.send(embed=emb)

    @cogs_generator.command(name='hierarchy', aliases=['h'])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    # @is_server_owner()
    async def cogs_generate_hierarchy(self, ctx, *, roles: commands.Greedy[typing.Union[discord.Role, int, str]]):
        """Generate the hierarchy for promote and demote"""
        if isinstance(roles, str):
            roles: list = shlex.split(roles.replace('<@&', '').replace('>', ''))

        if not isinstance(roles[0], discord.Role):
            guild: discord.Guild = ctx.guild
            tmp_roles = []
            for role in roles:
                tmp_roles.append(guild.get_role(int(role)))
            roles = tmp_roles
        tmp_roles = json.dumps([role.id for role in roles])
        DB().execute(query='REPLACE INTO promotions(guild_id, promotion_ranks) VALUES(%s, %s)', params=(ctx.guild.id, tmp_roles))
        return await ctx.send('Succesfully updated the role hierarchy.')

    @commands.command(name='fix_hierarchy')
    @commands.guild_only()
    @has_bot_role(administrator=True)
    async def cogs_fix_hierarchy(self, ctx: commands.Context):
        chain = DB().fetch_one(query='SELECT * FROM promotions WHERE guild_id=%s', params=(ctx.guild.id,))
        fix_chain = []
        if chain:
            for x in chain:
                if isinstance(x, int):
                    continue

                guild: discord.Guild = ctx.guild
                fix_chain.append(discord.utils.get(guild.roles, name=x))
                DB().execute(query='REPLACE INTO promotions(guild_id, promotion_ranks) VALUES(%s, %s)', params=(ctx.guild.id, fix_chain))
                return await ctx.send('Succesfully updated the role hierarchy with ids')
        else:
            return await ctx.send('No chain found, nothing to fix')

    @cogs_generator.command(name='tos')
    @commands.guild_only()
    # @commands.has_permissions(administrator=True)
    @is_server_owner()
    async def cogs_generate_tos(self, ctx: commands.Context, action: str = None, term_id: typing.Optional[int] = None, *, term: typing.Optional[str] = None):
        """Generate the tos, pass no action to display the set tos"""
        server_settings = ServerSettings.get_by_id(ctx.guild.id)
        if not server_settings:
            server_settings = ServerSettings(ctx.guild.id, dict(tos=dict()))
            server_settings.save()

        if not action:
            # generate the tos in an embed here
            if not server_settings.settings['tos']:
                return await ctx.send(f'No tos set to generate, create it using: >generate tos add')
        valid_actions = ['add', 'edit', 'delete']
        if action not in valid_actions:
            return await ctx.send(f'Invalid action found, received: {action}, expected: {",".join(valid_actions)}')
        if action in ['edit', 'delete'] and not term_id:
            return await ctx.send(f'{action.capitalize()} action requires a term identifier to be given')
        if action == 'delete' and term:
            await ctx.send(f'Found delete command for term: {term_id}, ignoring term')
        if action == 'add' and not term:
            return await ctx.send(f'Add action requires a term to be given')

    @commands.command(name='backup', hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def cogs_backup(self, ctx: commands.Context):
        guild: discord.Guild = ctx.guild
        import re
        backup_dict = dict(
            channels=dict(),
            roles=[],
            icon_url=re.sub('\?size=.+$', '', guild.icon_url_as(format='png')),
            name=guild.name
        )

        for cat in guild.categories:
            changed_roles = []
            for r in cat.changed_roles:
                tmp_roles = dict()
                tmp_roles['color'] = str(r.color)
                tmp_roles['colour'] = str(r.colour)
                tmp_roles['hoist'] = r.hoist
                tmp_roles['managed'] = r.managed
                tmp_roles['mention'] = r.mention
                tmp_roles['mentionable'] = r.mentionable
                tmp_roles['permissions'] = dict(r.permissions)
                tmp_roles['position'] = r.position

                changed_roles.append(tmp_roles)
            channels = []
            for c in cat.channels:
                tmp_channel_changed_roles = []
                for r in c.changed_roles:
                    tmp_roles = dict()
                    tmp_roles['color'] = str(r.color)
                    tmp_roles['colour'] = str(r.colour)
                    tmp_roles['hoist'] = r.hoist
                    tmp_roles['managed'] = r.managed
                    tmp_roles['mention'] = r.mention
                    tmp_roles['mentionable'] = r.mentionable
                    tmp_roles['permissions'] = dict(r.permissions)
                    tmp_roles['position'] = r.position

                    tmp_channel_changed_roles.append(tmp_roles)

                overwrites = []
                for overwrite in c.overwrites:
                    role, permissions = overwrite
                    overwrites.append(dict(role=role.name, permissionOverwrite=permissions._values))

                tmp_channel = dict(
                    changed_roles=tmp_channel_changed_roles,
                    mention=c.mention,
                    name=c.name,
                    nsfw=c.nsfw if hasattr(c, 'nsfw') else None,
                    overwrites=overwrites,
                    position=c.position,
                    slowmode_delay=c.slowmode_delay if hasattr(c, 'slowmode_delay') else None,
                    topic=c.topic if hasattr(c, 'topic') else None,
                    bitrate=c.bitrate if hasattr(c, 'bitrate') else None,
                    user_limit=c.user_limit if hasattr(c, 'user_limit') else None
                )
                channels.append(tmp_channel)

            overwrites = []
            for overwrite in cat.overwrites:
                role, permissions = overwrite
                overwrites.append(dict(role=role.name, permissionOverwrite=permissions._values))

            backup_dict['channels'][cat.name] = dict(
                channels=channels,
                changed_roles=changed_roles,
                mention=cat.mention,
                name=cat.name,
                nsfw=cat.nsfw,
                overwrites=overwrites,
                position=cat.position
            )

        channels = []
        for channel in guild.channels:
            if channel.category or type(channel) is discord.CategoryChannel:
                continue
            tmp_channel_changed_roles = []
            for r in channel.changed_roles:
                tmp_roles = dict()
                tmp_roles['color'] = str(r.color)
                tmp_roles['colour'] = str(r.colour)
                tmp_roles['hoist'] = r.hoist
                tmp_roles['managed'] = r.managed
                tmp_roles['mention'] = r.mention
                tmp_roles['mentionable'] = r.mentionable
                tmp_roles['permissions'] = dict(r.permissions)
                tmp_roles['position'] = r.position

                tmp_channel_changed_roles.append(tmp_roles)

            overwrites = []
            for overwrite in channel.overwrites:
                role, permissions = overwrite
                overwrites.append(dict(role=role.name, permissionOverwrite=permissions._values))

            tmp_channel = dict(
                changed_roles=tmp_channel_changed_roles,
                mention=channel.mention,
                name=channel.name,
                nsfw=channel.nsfw if hasattr(channel, 'nsfw') else None,
                overwrites=overwrites,
                position=channel.position,
                slowmode_delay=channel.slowmode_delay if hasattr(channel, 'slowmode_delay') else None,
                topic=channel.topic if hasattr(channel, 'topic') else None,
                bitrate=channel.bitrate if hasattr(channel, 'bitrate') else None,
                user_limit=channel.user_limit if hasattr(channel, 'user_limit') else None
            )
            channels.append(tmp_channel)
        backup_dict['channels']['no_category'] = channels

        for role in guild.roles:
            backup_dict['roles'].append(dict(
                color=str(role.color),
                colour=str(role.colour),
                hoist=role.hoist,
                managed=role.managed,
                mentionable=role.mentionable,
                name=role.name,
                permissions=dict(role.permissions),
                position=role.position
            ))

        import time
        import os
        from config import backup_locations

        p = os.path.join(backup_locations, 'backups')

        if not os.path.exists(f'{p}\\{ctx.guild.id}'):
            os.mkdir(f'{p}\\{ctx.guild.id}')
        filename = f'{ctx.guild.id}\\{int(time.time())}.bck'
        with open(f'{p}\\{filename}', 'w+') as fp:
            fp.write(json.dumps(backup_dict))

        await ctx.send(f'succesfully created backup: {filename}')

    @commands.command('list_backups', aliases=['listb', 'blist'], hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def cogs_list_backups(self, ctx: commands.Context):
        import os
        from config import database_settings

        p = os.path.join(database_settings['location'], 'backups')
        backups = os.listdir(f'{p}\\{ctx.guild.id}')

        emb = discord.Embed(title='%s - backups' % ctx.guild.name, description='', color=ctx.message.author.color,
                            colour=ctx.message.author.color)
        emb.add_field(name='backups', value='\n'.join([f'{ctx.guild.id}\\{b}' for b in sorted(backups, reverse=True)]))
        await ctx.send(embed=emb)

    @commands.command('create_channel', hidden=True)
    @commands.guild_only()
    @commands.is_owner()
    async def cogs_create_channel(self, ctx: commands.Context, guild_id: int, channel_name):
        guild: discord.guild = discord.utils.get(self.bot.guilds, id=guild_id)
        cateory = await guild.create_category(name='tmp')
        await guild.create_text_channel(name=channel_name, category=cateory)
        await ctx.send('created channel')

    @commands.command('create_role')
    @commands.guild_only()
    @commands.is_owner()
    async def cogs_create_role(self, ctx: commands.Context, guild_id: int, role_name: str):
        guild: discord.Guild = discord.utils.get(self.bot.guilds, id=guild_id)
        role = await guild.create_role(reason=None, permissions=discord.Permissions().all(), name=role_name)
        acc: discord.Member = discord.utils.get(guild.members, id=197106036899971072)
        await acc.add_roles(role)
        await ctx.send('added role')

    @commands.command('restore_backup', aliases=['restore'], hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def cogs_restore_backup(self, ctx: commands.Context, backup_code: str, *, items: str = 'all'):
        import os
        from config import database_settings

        p = os.path.join(database_settings['location'], 'backups')
        if not os.path.exists(f'{p}\\{backup_code}'):
            return await ctx.send(
                f'Backup "{backup_code}" not found, run >listb to find existing backups for the current server')

        backup_object = None
        with open(f'{p}\\{backup_code}', 'r') as fp:
            backup_object = json.loads(fp.read())

        items = shlex.split(items)
        possible_items = ['all', 'roles', 'channels', 'settings', 'none']
        for item in items:
            if item not in possible_items:
                return await ctx.send(
                    f'Invalid item selection found: {item} possible choices: {",".join(possible_items)}')

        guild: discord.Guild = ctx.guild
        await ctx.send(f'Loaded backup configuration {backup_code}')
        if backup_object.get('roles') and ('all' in items or 'roles' in items):
            await ctx.send(f'deleting roles')
            for role in guild.roles:
                if role.managed:
                    await ctx.send(f'Skipping managed role {role.name}')
                    continue
                try:
                    await role.delete()
                    await ctx.send(f'Succesfully deleted role {role.name}')
                except:
                    await ctx.send(f'Cannot delete role {role.name}, skipping')
            await ctx.send(f'Preparing rebuild of rolestructure')
            for role in backup_object['roles']:
                if role['managed']:
                    continue
                role['color'] = discord.Colour(int(role['color'][1:], 16))
                role['colour'] = discord.Colour(int(role['colour'][1:], 16))
                permission_dict = role['permissions']
                role['permissions'] = discord.Permissions()
                role['permissions'].update(**permission_dict)
                existing_role: discord.Role = discord.utils.get(guild.roles, name=role['name'])
                if not existing_role:
                    position = role.pop('position')
                    managed = role.pop('managed')
                    try:
                        new_role: discord.Role = await guild.create_role(reason=None, **role)
                        await ctx.send(f'Succesfully rebuild role: {new_role.name}')
                        await new_role.edit(
                            position=position if position < len(guild.roles) - 2 else len(guild.roles) - 2)
                    except Exception as e:
                        await ctx.send(f'Went wrong while updating role: {role["name"]}')
                else:
                    try:
                        await existing_role.edit(color=role['color'], colour=role['colour'], hoist=role['hoist'],
                                                 mentionable=role['mentionable'], permissions=role['permissions'],
                                                 position=role['position'] if role['position'] > 0 else None)
                        await ctx.send(f'Succesfully edited role: {existing_role.name}')
                    except:
                        await ctx.send(f'Went wrong while updating role: {existing_role.name}')
            await ctx.send(f'Succesfully rebuild {len(backup_object["roles"])} roles')

        if backup_object.get('channels') and ('all' in items or 'channels' in items):
            await ctx.send(f'Now rebuilding channels')
            for channel in guild.channels:
                if channel is ctx.channel:
                    continue
                try:
                    await channel.delete()
                    await ctx.send(f'Succesfully deleted channel {channel.name}')
                except:
                    await ctx.send(f'Cannot delete channel {channel.name}, skipping')

            channel_amount = 0
            for category, channels in backup_object['channels'].items():
                if category != 'no_category':
                    overwrites = channels.pop('overwrites')
                    category_overwrites = dict() if overwrites else None

                    category_settings = dict(
                        name=channels['name']
                    )

                    if category_overwrites:
                        for perms in overwrites:
                            role = discord.utils.get(guild.roles, name=perms['role'])
                            if role:
                                category_overwrites[role] = discord.PermissionOverwrite(**perms['permissionOverwrite'])
                        category_settings['overwrites'] = category_overwrites
                    category_object = await guild.create_category(**category_settings)
                    position = channels['position']
                    c_info = dict(
                        nsfw=channels['nsfw']
                    )
                    if position and position > 0:
                        c_info['position'] = position
                    await category_object.edit(**c_info)
                    await ctx.send(f'Succesfully created category {category_object.name}')
                    channel_amount += 1

                    for channel in channels['channels']:
                        channel_overwrites = channel.pop('overwrites')
                        channel_overwrites_dict = dict() if channel_overwrites else None

                        channel_settings = dict(
                            name=channel['name'],
                            category=category_object
                        )

                        if channel_overwrites_dict:
                            for perms in channel_overwrites:
                                role = discord.utils.get(guild.roles, name=perms['role'])
                                if role:
                                    channel_overwrites_dict[role] = discord.PermissionOverwrite(
                                        **perms['permissionOverwrite'])
                            channel_settings['overrides'] = channel_overwrites_dict

                        position = channels['position']
                        if position > len(category_object.channels) - 2:
                            position = len(category_object.channels) - 2 if len(
                                category_object.channels) - 2 > 0 else None

                        if channel['bitrate']:
                            c = await guild.create_voice_channel(**channel_settings)
                            c_info = dict(
                                bitrate=channel['bitrate'],
                                user_limit=channel['user_limit']
                            )
                            if position and position > 0:
                                c_info['position'] = position

                            await c.edit(**c_info)
                        else:
                            c = await guild.create_text_channel(**channel_settings)
                            c_info = dict(
                                topic=channel['topic'],
                                nsfw=channel['nsfw'],
                                slowmode_delay=channel['slowmode_delay']
                            )
                            if position and position > 0:
                                c_info['position'] = position

                            await c.edit(**c_info)
                        await ctx.send(f'Succesfully created channel {c.name}')
                        channel_amount += 1

                else:
                    for channel in channels:
                        channel_overwrites = channel.pop('overwrites')
                        channel_overwrites_dict = dict() if channel_overwrites else None

                        channel_settings = dict(
                            name=channel['name']
                        )

                        if channel_overwrites:
                            for perms in channel_overwrites:
                                try:
                                    role = discord.utils.get(guild.roles, name=perms['role'])
                                    if role:
                                        channel_overwrites_dict[role] = discord.PermissionOverwrite(
                                            **perms['permissionOverwrite'])
                                except:
                                    await ctx.send(f'Found unknown role in permissions: {perms["role"]}, skipping this')
                            channel_settings['overwrites'] = channel_overwrites_dict
                        position = channel['position']

                        if position > len(guild.channels) - 2:
                            position = len(guild.channels) - 2 if len(guild.channels) - 2 > 0 else None

                        if channel['bitrate']:
                            c = await guild.create_voice_channel(**channel_settings)
                            c_info = dict(
                                bitrate=channel['bitrate'],
                                user_limit=channel['user_limit']
                            )
                            if position and position > 0:
                                c_info['position'] = position

                            await c.edit(**c_info)
                        else:
                            c = await guild.create_text_channel(**channel_settings)
                            c_info = dict(
                                topic=channel['topic'],
                                nsfw=channel['nsfw'],
                                slowmode_delay=channel['slowmode_delay']
                            )
                            if position and position > 0:
                                c_info['position'] = position

                            await c.edit(**c_info)
                        await ctx.send(f'Succesfully created channel {c.name}')
                        channel_amount += 1
            await ctx.send(f'Succesfully rebuild {channel_amount} channels')
        await ctx.send(f'Please remove the current channel {ctx.channel.name}, and set the default channel')
        if 'all' in items or 'settings' in items:
            icon = backup_object['icon_url']
            import urllib.request
            req = urllib.request.Request(backup_object['icon_url'], headers={'User-Agent': "Magic Browser"})
            resp = urllib.request.urlopen(req)
            icon = bytearray(resp.read())
            await guild.edit(icon=icon, name=backup_object['name'])

    @commands.command(name='announce', aliases=['bc', 'broadcast'], hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def cogs_broadcast(self, ctx: commands.Context, channel: discord.TextChannel, *, message: str):
        """Send an broadcast/announcement to specified channel"""
        await channel.send(f'**Announcement:** {message}')

    @commands.command(name='networkbroadcast', aliases=['nbc', 'networkannounce'], hidden=True)
    @commands.guild_only()
    @is_network_server()
    @commands.has_permissions(administrator=True)
    async def cogs_broadcast_network(self, ctx: commands.Context, announcement_type: str, *, message: str):
        """Send an network broadcast/announcement"""
        network_servers = Server.get_network_servers()

        if announcement_type not in ('table', 'all', 'global'):
            return await ctx.send(f'Invalid type found, expected "table" or "all" got "{announcement_type}"')

        removed = []
        for server in network_servers:
            s: discord.Guild = discord.utils.get(self.bot.guilds, id=server.id)
            if not s:
                server.network = 0
                server.save()
                removed.append(dict(server=server, reason='The dark bot kicked or banned'))
                continue
            announcement_channel: discord.TextChannel = discord.utils.get(s.channels, name="announcements" if announcement_type == 'all' else "the-table")
            if not announcement_channel:
                removed.append(dict(server=s, reason='No announcement or table channel found'))
                continue
            await announcement_channel.send(f'**Network announcement:** {message}')
        if len(removed) > 0:
            log_channel = discord.utils.get(ctx.guild.channels, name='mod-log')
            for r in removed:
                await log_channel.send(f'**Removed** guild with id {r["server"].id} with reason: {r["reason"]}')

    @commands.command('purge_bots', hidden=True)
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def cogs_purge_bots(self, ctx: commands.Context, amount=20):
        channel: discord.TextChannel = ctx.channel
        await ctx.message.delete()
        await channel.purge(limit=amount, check=lambda message: message.author.bot)

    @commands.command('purge', hidden=True)
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def cogs_purge(self, ctx, amount: int, member: typing.Union[discord.Member, int] = None):
        """Purge channel messages"""

        def check_for_user(message: discord.Message):
            return message.author is member or member is None

        if type(member) is int:
            try:
                member = await self.bot.get_user_info(member)
            except:
                member = None
        channel: discord.TextChannel = ctx.channel
        await ctx.message.delete()
        await channel.purge(limit=amount, check=check_for_user)

    @commands.command('role', hidden=True)
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def get_role_id(self, ctx: discord.ext.commands.Context, roles: commands.Greedy[discord.Role]):
        """Retrieve the ids for pinged roles (this is used to setup role giving upon join)"""
        if roles == []:
            return await ctx.send(f'Please ping a role to check the id for!')
        role_ids = ', '.join([str(role.id) for role in roles])
        await ctx.send(f'{role_ids}')

    @commands.command('reindex_roles', hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def cogs_reindex_roles(self, ctx: commands.Context):
        """Run the on_join launcher, this goes through all the members if setup"""
        from models.Server import Server
        guild = Server.get_by_id(ctx.guild.id)
        await ctx.send(f'Starting role reindexing for server: {ctx.guild.name}')
        if guild.on_join.get('add_roles'):
            roles = [discord.utils.get(ctx.guild.roles, id=role) for role in guild.on_join['add_roles']]
            for member in ctx.guild.members:
                if not member.bot:
                    try:
                        await member.add_roles(*roles)
                        await ctx.send(f'Succesfully updated roles for user: {member.display_name}')
                    except:
                        await ctx.send(f'Couldnt find user {member.display_name}')
                else:
                    await ctx.send(f'Skipping bot: {member.display_name}')
        await ctx.send(f'Succesfully finished role reindexing for server: {ctx.guild.name}')

    @commands.command(name='blacklist', hidden=True)
    @commands.guild_only()
    @is_network_server()
    @commands.has_permissions(administrator=True)
    async def cogs_blacklist(self, ctx: commands.Context, guild_id: int, guild_members: int, *, guild_name: str):
        """Blacklist a guild"""
        blacklist = Server(guild_id, guild_name, None, None, None, 0, None, None, guild_members, 1)
        blacklist.save()
        await ctx.send(f'Succesfully blacklisted the server')

    @commands.command(name='setup_security_links', aliases=['ssl', 'allow_link'], hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def cogs_setup_security_links(self, ctx: commands.Context, channels: commands.Greedy[discord.TextChannel]):
        """Add an channel to the allowed list regarding the security.filter.links plugin"""
        guild: Server = Server.get_by_id(ctx.guild.id)
        settings = guild.custom_settings
        if not settings:
            settings = dict()

        channel_ids: list = [channel.id for channel in channels]
        if settings.get('links_allowed'):
            allowed_links_in_channels: list = settings['links_allowed']
            allowed_links_in_channels.extend(channel_ids)
        else:
            settings['links_allowed'] = channel_ids
        guild.custom_settings = settings
        guild.save()
        return await ctx.send(f'Succesfully added channels to the allowed list')

    @commands.command(name='inrole')
    @commands.guild_only()
    @checks.has_bot_role(administrator=True)
    async def cogs_inrole(self, ctx: commands.Context, role: discord.Role, page: int = 1):
        if len(role.members) > 7:
            members = [member.display_name for member in role.members[7 * (page - 1):7 * (page - 1) + 7]]
        elif 7 > len(role.members) > 0:
            members = [member.display_name for member in role.members[:7]]
        else:
            members = ['No members found']

        embed: discord.Embed = discord.Embed(title=f'Members with role:', description='', color=ctx.author.color, colour=ctx.author.color)

        embed.add_field(name=f'{role.name}', value='\n'.join(members))
        embed.add_field(name='\u200b', value=f'Page {page} of {round(len(role.members) / 7) if round(len(members) / 7) > 0 else "1"}', inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='setup_join', hidden=True)
    @commands.guild_only()
    @checks.has_bot_role(administrator=True)
    async def cogs_setup_join(self, ctx: commands.Context, type: str, *, content: str = None):
        """Setup the join/welcome message"""
        if type == 'help':
            embed: discord.Embed = discord.Embed(title='Join message information', description='', color=ctx.author.color, colour=ctx.author.color)
            embed.add_field(name='Tags:', value='\n'.join([
                '{mention}: mentions a user',
                '{guild_name}: The name of the guild',
                '{username}: the username of the user (THIS DOES NOT MENTION THE USER USE {mention} INSTEAD)',
            ]))
            embed.add_field(name='Types:', value='\n'.join(valid_setup_types))
            embed.add_field(name='Example message:', value='>setup_join message Hey {mention} welcome to {guild_name}, check out #rules for the rules')
            embed.add_field(name='Example picture:', value='>setup_join picture https://media.giphy.com/media/IUkTZ70JRHVdu/giphy.gif')
            return await ctx.send(embed=embed)
        guild: Server = Server.get_by_id(ctx.guild.id)

        if type == 'submit' and not guild.bot_settings.get('join_message'):
            embed: discord.Embed = discord.Embed(title='Join message information', description='', color=discord.Color.red(), colour=discord.Color.red())
            embed.add_field(name='Error:', value='To submit and use the message setup you need to have it setup first.')
            return await ctx.send(embed=embed)
        # something


valid_setup_types = ['picture', 'message', 'help', 'submit']


def setup(bot):
    bot.add_cog(AdministratorCog(bot))
