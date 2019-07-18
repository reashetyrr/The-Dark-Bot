import discord
from discord.ext import commands
from models.Server import Server
from models.User import User
from datetime import datetime, timezone


class ConfigurationCog(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command(name='gen_spam', hidden=True)
    @commands.is_owner()
    async def cogs_gen_spam(self, ctx: commands.Context, amount: int = 10):
        await ctx.message.delete()
        for _ in range(amount):
            await ctx.send(f'Spam spam spam, cutie you :3')

    @commands.command(name='gen_invite', hidden=True)
    @commands.is_owner()
    async def cogs_gen_invite(self, ctx: commands.Context, guild: int):
        guild: discord.Guild = self.bot.get_guild(guild)
        general_channel: discord.TextChannel = discord.utils.find(lambda c: 'general' in c.name.lower(), guild.channels)
        invite: discord.Invite = await general_channel.create_invite(reason='', max_uses=1)

        await ctx.author.send(str(invite))

    @commands.command(name='load', hidden=True)
    @commands.is_owner()
    async def cogs_load(self, ctx, *, cog: str):
        """Command which Loads a Module. Optional to use a dot path notation"""
        if not cog.startswith('cogs.'):
            cog = 'cogs.' + cog
        try:
            self.bot.load_extension(cog)
        except (Exception, ModuleNotFoundError) as e:
            await ctx.send(f'**ERROR:** {type(e).__name__} - {e}')
        else:
            await ctx.send('**SUCCESS**')

    @commands.command(name='remove_user_plugin', hidden=True)
    @commands.is_owner()
    async def cogs_fix_plugins(self, ctx: commands.Context, *, plugin_type: str):
        users: list = User.get_all()
        for user in users:
            if user.plugins.get(plugin_type):
                del user.plugins[plugin_type]
                user.save()
                await ctx.send(f'Removed {plugin_type} from user: {user.display_name}')
        await ctx.send(f'Succesfully removed plugin {plugin_type} from all users')

    @commands.command(name='unload', hidden=True)
    @commands.is_owner()
    async def cogs_unload_command(self, ctx, *, cog: str):
        """Command which Unloads a Module. Optional to use a dot path notation"""
        if not cog.startswith('cogs.'):
            cog = 'cogs.' + cog
        try:
            self.bot.unload_extension(cog)
        except (Exception, ModuleNotFoundError) as e:
            await ctx.send(f'**ERROR:** {type(e).__name__} - {e}')
        else:
            await ctx.send('**SUCCESS**')

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def cogs_reload(self, ctx, *, cog: str):
        """Command which Reloads a Module. Optional to use a dot path notation"""
        if not cog.startswith('cogs.'):
            cog = 'cogs.' + cog
        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except (Exception, ModuleNotFoundError) as e:
            await ctx.send(f'**ERROR:** {type(e).__name__} - {e}')
        else:
            await ctx.send('**SUCCESS**')

    @commands.command(name='fix_servers', hidden=True)
    @commands.is_owner()
    async def cogs_fix_servers(self, ctx: commands.Context):
        servers = Server.get_non_blacklisted()
        for server in servers:
            try:
                d_server: discord.Guild = self.bot.get_guild(server.id) # discord.utils.get(self.bot.guilds, id=server.id)
                server.icon_url = d_server.icon_url_as(format='png')
                server.name = d_server.name
                server.member_count = len([m for m in d_server.members if not m.bot])
                if not server.bot_settings.get('moderators'):
                    server.bot_settings['moderators'] = []
                if not server.bot_settings.get('administrators'):
                    server.bot_settings['administrators'] = []
                server.save()
            except AttributeError as e:
                await ctx.send(f'Skipping server {server.name}({server.id}), bot is not in server anymore, blacklisting now.')
                server.blacklisted = 1
                server.save()
        await ctx.send(f'Succesfully updated all the known servers')

    @commands.command(name='fix_user_ids', hidden=True)
    @commands.is_owner()
    async def cogs_fix_user_ids(self, ctx: commands.context):
        from models.User import User
        from re import search
        users: list = User.get_all()
        ten_percentage = int(len(users) * 0.1)
        for index, user in enumerate(users):
            res = search('\<\@!?(\d+)\>', user.mention)
            try:
                user.id = res.group(1)
            except AttributeError:
                pass
            user.save()
            if index % ten_percentage == 0 and index != 0:
                await ctx.send(f'Succesfully updated {int((index/len(users)) * 100)}% ({index}/{len(users)}) user ids')
        await ctx.send(f'Succesfully fixed the user ids of {len(users)} users')

    @commands.command(name='leave', hidden=True)
    @commands.is_owner()
    async def cogs_leave_guild(self, ctx: commands.Context, guild: int):
        guild: discord.Guild = discord.utils.get(self.bot.guilds, id=guild)
        await guild.leave()
        await ctx.send(f'Succesfully left guild {guild.name}')

    @commands.command(name='render_blacklist', hidden=True)
    @commands.is_owner()
    async def cogs_render_blacklist(self, ctx: commands.Context):
        def check_blacklist_purge(message: discord.Message):
            return len(message.embeds) > 0
        blacklisted_guilds: list = [guild for guild in Server.get_all() if guild.blacklisted]
        for guild in self.bot.guilds:
            blacklist_channel: discord.TextChannel = discord.utils.get(guild.channels, name='blacklist')
            if blacklist_channel:
                await blacklist_channel.purge(limit=100, check=check_blacklist_purge)
                for blacklisted in blacklisted_guilds:
                    embed = discord.Embed(title=f'Blacklisted guild', description='', color=ctx.message.author.color, colour=ctx.message.author.color)
                    embed.add_field(name='Guild name:', value=blacklisted.name)
                    embed.add_field(name='Guild id (last known):', value=blacklisted.id)
                    embed.add_field(name='Member count:', value=blacklisted.member_count)
                    if blacklisted.member_count and blacklisted.name:
                        await blacklist_channel.send(embed=embed)

    @commands.command(name='bot_announce', hidden=True)
    @commands.is_owner()
    async def cogs_bot_announce(self, ctx: commands.Context, *, message: str):
        """Make an announcement in every guild she is in, split title from message using '|'"""
        servers: list = Server.get_non_blacklisted()

        msg = ''
        if '@here' in message:
            msg += '@here '
        if '@everyone' in message:
            msg += '@everyone '

        title, message = message.split('|')
        for server in servers:
            s: discord.Guild = discord.utils.get(self.bot.guilds, id=server.id)
            announcement_channel: discord.TextChannel = discord.utils.find(lambda c: 'announcement' in c.name.lower() and not 'staff' in c.name.lower(), s.channels)
            if not announcement_channel:
                continue
            embed = discord.Embed(title=f'The Dark Bot Announcement', description='', color=discord.colour.Color.dark_purple(), colour=discord.colour.Color.dark_purple())
            embed.add_field(name=title, value=message)
            await announcement_channel.send(msg, embed=embed)
            await ctx.send(f'Succesfully made announcement in {s.name}')

    @commands.command(name='shard_info', hidden=True)
    @commands.is_owner()
    @commands.guild_only()
    async def cogs_shard_info(self, ctx: commands.Context):
        bot: commands.AutoShardedBot = self.bot
        current_shard_id: int = ctx.guild.shard_id
        shard: discord.shard.Shard = bot.shards[current_shard_id]
        shard_ids = bot.shard_ids or [current_shard_id]
        shards_info = {sid: [] for sid in shard_ids}
        total_members: int = len([_ for _ in self.bot.get_all_members()])
        total_guilds: int = len(bot.guilds)
        for guild in bot.guilds:
            guild: discord.Guild = guild
            shards_info[current_shard_id].append(guild.member_count)

        current_shard = shards_info[current_shard_id]
        current_shard_members = 0
        for _ in current_shard:
            current_shard_members += _

        latency: int = round(bot.latency * 1000.0)

        res = User.get_by_id(self.bot.owner_id)
        current_time = datetime.now(timezone.utc).replace(tzinfo=None)
        created_at = ctx.message.created_at
        db_latency = round((current_time - created_at).microseconds / 1000.0)

        embed: discord.Embed = discord.Embed(title=f'The Dark Bot Shards', description='', color=discord.colour.Color.dark_purple(), colour=discord.colour.Color.dark_purple())
        embed.add_field(name='Shards', value=f'{bot.shard_count} Shards', inline=True)
        embed.add_field(name=f'This shard ({current_shard_id})', value=f'{len(current_shard)} Guilds, {current_shard_members} Members')
        embed.add_field(name='Latency', value=f'{latency} ms')
        from memory_profiler import memory_usage
        mem_used = memory_usage(proc=-1, interval=.1, timeout=.1)
        embed.add_field(name='All Shards', value=f'{total_guilds} Guilds, {total_members} Members', inline=True)
        embed.add_field(name='Memory Usage', value=f'{int(mem_used[0])} MB', inline=True)
        embed.add_field(name='Database Latency', value=f'{db_latency} ms', inline=True)

        await ctx.send(embed=embed)

    @commands.command(name='botban', hidden=True)
    @commands.guild_only()
    @commands.is_owner()
    async def cogs_botban(self, ctx: commands.Context, member_id: int, *, reason: str = None):
        """Ban an user by id (User does not have to be inside the server)"""
        guilds: list = self.bot.guilds
        user = discord.Object(id=member_id)
        local_user = User.get_by_id(member_id)
        if local_user:
            local_user.banned = True
            local_user.save()
        for guild in guilds:
            try:
                await guild.ban(user=user, reason=reason)
            except:
                pass
        await ctx.send(f'Succesfully banned member {user.id} from {len(guilds)} guilds')
        log_channel: discord.TextChannel = discord.utils.get(guild.channels, name='tdb-logs')
        if log_channel:
            log_embed = discord.Embed(color=discord.colour.Colour.dark_red(), title=f'User banned')
            log_embed.add_field(name='Event:', value=f'{ctx.author.mention} has succesfully banned user {user.mention} using his/her id with reason: {reason}')
            await log_channel.send(embed=log_embed)


def setup(bot):
    bot.add_cog(ConfigurationCog(bot))
