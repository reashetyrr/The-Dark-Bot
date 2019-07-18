import discord
from datetime import datetime
from discord.ext import commands
from checks import is_plugin_enabled, has_bot_role
from models.Server import Server
from models.User import User


class TestsCog(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.ext.commands.Bot = bot

    @commands.group(name='test', hidden=True)
    @commands.guild_only()
    @is_plugin_enabled(plugin_name='tests')
    @has_bot_role(moderator=True)
    async def cogs_tests(self, ctx: commands.Context):
        """Testing commands"""
        guild: discord.Guild = ctx.guild
        server: Server = Server.get_by_id(guild.id)
        if not ctx.subcommand_passed:
            command_list = self.bot.get_command(name='test').commands

            embed = discord.Embed(title='%s - Testing commands help' % guild.name, description='', color=ctx.message.author.color, colour=ctx.message.author.color)
            embed.set_thumbnail(url=guild.icon_url)
            order = dict()
            for c in command_list:
                if await c.can_run(ctx):
                    order[c.name] = c.help
            embed.add_field(name='Commands:', value='\n'.join([f'**{com_name}**: {com_desc}' for com_name, com_desc in order.items()]) if len(order.keys()) > 0 else 'No commands found', inline=False)
            await ctx.send(embed=embed)

    @cogs_tests.command(name='levelup', aliases=['tlu'], hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def cogs_tests_levelup(self, ctx: commands.Context, member: discord.Member = None):
        """Generate an level up, optional: supply an member"""
        user: User = User.get_by_id(member.id if member else ctx.author.id)
        guild: Server = Server.get_by_id(ctx.guild.id)
        ctx_guild: discord.Guild = ctx.guild

        mention, level, guild_name, username, added_coins, total_coins, currency = user.mention, user.plugins.get('prev_level', 333), ctx_guild.name, member.display_name if member else ctx.author.display_name, 666, user.plugins.get('currency', 9999999), guild.currency_name

        level_up_message: str = guild.custom_settings.get('level_up_message', 'Congratulations {mention}, you have succesfully leveled up and are now level {level:,}')

        lvl_msg = guild.custom_settings.get('level_up_message')
        if lvl_msg and lvl_msg != 'None':
            await ctx.send(level_up_message.format(
                mention=mention,
                level=level,
                guild_name=guild_name,
                username=username,
                added_coins=added_coins,
                total_coins=total_coins,
                currency=currency if currency else 'Coins',
            ))
        else:
            await ctx.send(f'Level up messages have been disabled')

    @cogs_tests.command(name='join', hidden=True)
    @commands.guild_only()
    @has_bot_role(moderator=True)
    @is_plugin_enabled('welcome message')
    async def cogs_tests_join(self, ctx: commands.Context, member: discord.Member = None):
        """Generate an join message, optional: supply an member"""
        guild: Server = Server.get_by_id(ctx.guild.id)
        ctx_guild: discord.Guild = ctx.guild
        if not member:
            member: discord.Member = ctx.author

        welcome_message: str = guild.custom_settings.get('welcome_message', '{mention} has joined {guild_name}')
        embed: discord.Embed = discord.Embed(title=f'Event', color=discord.Color.green(), colour=discord.Color.green(), description=f'User has joined the guild.')
        embed.set_thumbnail(url=member.avatar_url)
        username: str = member.display_name
        mention: str = member.mention
        guild_name: str = guild.name
        embed.add_field(name=member.display_name, value=welcome_message.format(
            mention=mention,
            username=username,
            guild_name=guild_name
        ))
        embed.set_footer(text=f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} CET')
        await ctx.send(embed=embed)

    @cogs_tests.command(name='moderator', aliases=['mod'], hidden=True)
    @commands.guild_only()
    async def cogs_tests_moderator(self, ctx: commands.Context, member: discord.Member = None):
        """Test if someone has moderator rights"""
        guild: Server = Server.get_by_id(ctx.guild.id)
        if not member:
            member: discord.Member = ctx.author
        mod = True
        if member.id not in guild.custom_settings.get('moderators', []) + guild.custom_settings.get('administrators', []):
            mod = False
        if member.guild_permissions.administrator:
            mod = True
        await ctx.send(f'User has {"no " if not mod else ""}moderator rights')

    @cogs_tests.command(name='administrator', aliases=['admin'], hidden=True)
    @commands.guild_only()
    @has_bot_role(administrator=True)
    async def cogs_tests_administrator(self, ctx: commands.Context, member: discord.Member = None):
        guild: Server = Server.get_by_id(ctx.guild.id)
        if not member:
            member: discord.Member = ctx.author
        admin = True
        if member.id not in guild.custom_settings.get('administrators', []):
            admin = False
        if member.guild_permissions.administrator:
            admin = True
        await ctx.send(f'User has {"no " if not admin else ""}administrator rights')


def setup(bot):
    bot.add_cog(TestsCog(bot))
