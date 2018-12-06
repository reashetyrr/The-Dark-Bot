import discord
from discord.ext import commands
from models.DB import DB
from models.Server import Server
from models.server_settings import ServerSettings
import typing
from checks import is_server_owner
import shlex
import json


class AdministratorCog:
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command(name='cleanup', hidden=True)
    @commands.guild_only()
    @commands.is_owner()
    async def cogs_cleanup(self, ctx: commands.context, *, key: str = None):
        # await ctx.message.delete()
        # if key != '011110010110010101110011001000000110100100100000011000010110110100100000011100110111010101110010011001010010110000100000011000110110110001100101011000010110111001101111011101010111010000100000011101000110100001100101001000000110011101110101011010010110110001100100':
        # return await ctx.send('No')
        return await ctx.send('no')
        guild: discord.Guild = ctx.guild
        await ctx.send(
            f'preparing cleanup for guild: {guild.name}. DISCLAIMER: this will remove all the channels from the guild!')
        for c in guild.channels:
            if c.id != ctx.channel.id:
                await ctx.send(f'deleted channel {c.name}')
                await c.delete()
        await ctx.send('DONE')

    @commands.command(name='setup', aliases=['reindex'], hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def cogs_reindex(self, ctx: commands.Context):
        """Register/setup the guild so that i know the guild"""
        guild: discord.Guild = ctx.guild
        server = Server(
            server_id=guild.id,
            server_name=guild.name,
            member_count=len([m for m in guild.members if not m.bot])
        )
        server.save()
        await ctx.send(f'Succesfully registered server!')

    @commands.command(name='hackban', aliases=['id_ban'], hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def cogs_hackban(self, ctx: commands.Context, member_id: int, *, reason: str = None):
        """Ban an user by id (User does not have to be inside the server)"""
        guild: discord.Guild = ctx.guild
        user = await self.bot.get_user_info(member_id)
        await guild.ban(user=user, reason=reason)
        await ctx.send(f'Succesfully banned member {user.name}')
        log_channel: discord.TextChannel = discord.utils.get(guild.channels, name='tdb-logs')
        if log_channel:
            log_embed = discord.Embed(color=discord.colour.Colour.dark_red(), title=f'User banned')
            log_embed.add_field(name='Event:', value=f'{ctx.author.mention} has succesfully banned user {user.mention} using his/her id with reason: {reason}')
            await log_channel.send(embed=log_embed)

    @commands.command(name='lookup', hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def cogs_lookup_user(self, ctx: commands.Context, member_id: typing.Union[discord.Member, int]):
        """Get some information about a user from either the id or ping"""
        if type(member_id) is int:
            user = await self.bot.get_user_info(member_id)
        else:
            user = member_id
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
        DB().execute(query='INSERT INTO warnings(guild_id, user_id, reason) VALUES(?,?,?)', params=(ctx.guild.id, member.id, reason))
        warnings = DB().fetch_all(query='SELECT * FROM warnings WHERE guild_id=? AND user_id=?', params=(ctx.guild.id, member.id))

        log_channel: discord.TextChannel = discord.utils.get(ctx.guild.channels, name='tdb-logs')
        if log_channel:
            log_embed = discord.Embed(color=discord.colour.Colour.dark_red(), title=f'User warned')
            log_embed.add_field(name='Event:', value=f'{ctx.author.mention} has succesfully warned user {member.mention} for: {reason}')
            await log_channel.send(embed=log_embed)

        if len(warnings) == 5:
            await member.kick(reason='Received 5 warnings, therefore automatically kicked.')
            embed = discord.Embed(title=f'User {member.display_name} kicked', description=f'User {member.display_name} received his 5th warning, therefore automagically kicked.', color=ctx.author.color)
            if log_channel:
                log_embed = discord.Embed(color=discord.colour.Colour.dark_red(), title=f'User warned')
                log_embed.add_field(name='Event:', value=f'{member.mention}has automagically been kicked for receiving his/her fifth warning')
                await log_channel.send(embed=log_embed)

        elif len(warnings) == 10:
            await member.ban(reason='Received 10 warnings, therefore automatically banned.')
            embed = discord.Embed(title=f'User {member.display_name} banned', description=f'User {member.display_name} received his 10th warning, therefore automagically banned.', color=ctx.author.color)
            if log_channel:
                log_embed = discord.Embed(color=discord.colour.Colour.dark_red(), title=f'User warned')
                log_embed.add_field(name='Event:', value=f'{member.mention}has automagically been banned for receiving his/her tenth warning')
                await log_channel.send(embed=log_embed)

        else:
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
            query = 'DELETE FROM warnings WHERE id IN (%s) AND user_id=? AND guild_id=?' % ','.join(
                '?' * len([x for x in warning_ids if x.strip()]))
            DB().execute(query=query, params=(*ids, member.id, ctx.guild.id))
            return await ctx.send(
                f'Succesfully cleared the warnings with ids: %s from user: {member.display_name}' % ','.join(
                    [str(x) for x in ids]))
        else:
            query = 'DELETE FROM warnings WHERE user_id=? AND guild_id=?'
            DB().execute(query=query, params=(member.id, ctx.guild.id))
            return await ctx.send(f'Succesfully cleared all warnings from user: {member.display_name}')

    @commands.command(name='warnings', aliases=['check'], hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def cogs_warnings(self, ctx, member: discord.Member):
        """Retrieve the warnings given to a specific user"""
        warnings = DB().fetch_all(query='SELECT * FROM warnings WHERE guild_id=? AND user_id=?',
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
        chain = DB().fetch_one(query='SELECT * FROM promotions WHERE guild_id=?', params=(ctx.guild.id,))
        try:
            c_guild_id, c_ranks = chain
        except (ValueError, TypeError):
            return await ctx.send('Chain not setup, set it up first!')

        chain: list = json.loads(c_ranks)

        success = False
        for member in members:
            for index, value in enumerate(chain):
                current_roles = member.roles
                role: discord.Role = discord.utils.get(ctx.guild.roles, name=chain[index])
                if role not in current_roles and index <= len(chain):
                    await member.add_roles(role)
                    success = True
                    continue
        if success:
            members = ', '.join([member.display_name for member in members])
            return await ctx.send(f'Succesfully promoted {members} to the ranks of: {role.name}')
        return await ctx.send(f'Error while promoting members: {members}')

    @commands.command(name='demote', hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def cogs_demote(self, ctx, members: commands.Greedy[discord.Member]):
        """Demote member down the chain if set"""
        chain = DB().fetch_one(query='SELECT * FROM promotions WHERE guild_id=?', params=(ctx.guild.id,))
        try:
            c_guild_id, c_ranks = chain
        except (ValueError, TypeError):
            return await ctx.send('Chain not setup, set it up first!')

        chain: list = json.loads(c_ranks)
        success = False
        for member in members:
            for index, value in enumerate(chain):
                current_roles = member.roles
                try:
                    role: discord.Role = discord.utils.get(ctx.guild.roles, name=chain[index + 1])
                except IndexError:
                    await member.remove_roles(discord.utils.get(ctx.guild.roles, name=chain[index]))
                    members = ', '.join([member.display_name for member in members])
                    return await ctx.send(f'Succesfully demoted {members} from the ranks of: {value}')

                if role not in current_roles and index - 1 >= 0:
                    try:
                        await member.remove_roles(discord.utils.get(ctx.guild.roles, name=chain[index - 1]))
                        success = True
                    except:
                        pass
                    continue

        if success:
            members = ', '.join([member.display_name for member in members])
            return await ctx.send(f'Succesfully demoted {members} back to the ranks of: {role.name}')
        return await ctx.send(f'Error while demoting members: {members}')

    @commands.group(name='generate', hidden=True)
    @commands.guild_only()
    # @commands.has_permissions(administrator=True)
    @is_server_owner()
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
    # @commands.has_permissions(administrator=True)
    @is_server_owner()
    async def cogs_generate_hierarchy(self, ctx, roles: commands.Greedy[discord.Role]):
        """Generate the hierarchy for promote and demote"""
        tmp_roles = json.dumps([role.name for role in roles])
        DB().execute(query='INSERT OR REPLACE INTO promotions(guild_id, promotion_ranks) VALUES(?, ?)',
                     params=(ctx.guild.id, tmp_roles))
        return await ctx.send('Succesfully updated the role hierarchy.')

    @cogs_generator.command(name='tos')
    @commands.guild_only()
    # @commands.has_permissions(administrator=True)
    @is_server_owner()
    async def cogs_generate_tos(self, ctx: commands.Context, action: str = None, term_id: typing.Optional[int] = None,
                                *, term: typing.Optional[str] = None):
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
        from config import database_settings

        p = os.path.join(database_settings['location'], 'backups')

        if not os.path.exists(f'{p}\\{ctx.guild.id}'):
            os.mkdir(f'{p}\\{ctx.guild.id}')
        filename = f'{ctx.guild.id}\\{int(time.time())}.bck'
        with open(f'{p}\\{filename}', 'w+') as fp:
            fp.write(json.dumps(backup_dict))

        await ctx.send(f'succesfully created backup: {filename}')

    @commands.command('list_backups', aliases=['listb', 'blist'], hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def cog_list_backups(self, ctx: commands.Context):
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
    async def cog_create_channel(self, ctx: commands.Context, guild_id: int, channel_name):
        guild: discord.guild = discord.utils.get(self.bot.guilds, id=guild_id)
        cateory = await guild.create_category(name='tmp')
        await guild.create_text_channel(name=channel_name, category=cateory)
        await ctx.send('created channel')

    @commands.command('create_role')
    @commands.guild_only()
    @commands.is_owner()
    async def cog_create_role(self, ctx: commands.Context, guild_id: int, role_name: str):
        guild: discord.Guild = discord.utils.get(self.bot.guilds, id=guild_id)
        role = await guild.create_role(reason=None, permissions=discord.Permissions().all(), name=role_name)
        acc: discord.Member = discord.utils.get(guild.members, id=197106036899971072)
        await acc.add_roles(role)
        await ctx.send('added role')

    @commands.command('restore_backup', aliases=['restore'], hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def cog_restore_backup(self, ctx: commands.Context, backup_code: str, *, items: str = 'all'):
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
        possible_items = ['all', 'roles', 'channels', 'none']
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
        icon = backup_object['icon_url']
        import urllib.request
        req = urllib.request.Request(backup_object['icon_url'], headers={'User-Agent': "Magic Browser"})
        resp = urllib.request.urlopen(req)
        icon = bytearray(resp.read())
        await guild.edit(icon=icon, name=backup_object['name'])

    @commands.command(name='broadcast', aliases=['bc', 'announce'], hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def cogs_broadcast(self, ctx: commands.Context, announcement_type: str, *, message: str):
        network_servers = Server.get_network_servers()

        if announcement_type not in ('table', 'all'):
            return await ctx.send(f'Invalid type found, expected "table" or "all" got "{announcement_type}"')
        removed = []
        for server in network_servers:
            s: discord.Guild = discord.utils.get(self.bot.guilds, id=server.id)
            if not s:
                server.network = 0
                server.save()
                removed.append(dict(server=server, reason='The dark bot kicked or banned'))
                continue
            announcement_channel: discord.TextChannel = discord.utils.get(s.channels,
                                                                          name="announcements" if announcement_type == 'all' else "the-table")
            if not announcement_channel:
                removed.append(dict(server=s, reason='No announcement or table channel found'))
                continue
            await announcement_channel.send(f'**Network announcement:** {message}')
        if len(removed) > 0:
            log_channel = discord.utils.get(ctx.guild.channels, name='mod-log')
            for r in removed:
                await log_channel.send(f'**Removed** guild with id {r["server"].id} with reason: {r["reason"]}')

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


def setup(bot):
    bot.add_cog(AdministratorCog(bot))
