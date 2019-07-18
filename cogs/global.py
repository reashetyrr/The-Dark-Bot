import discord
from discord.ext import commands
from models.DB import DB
import json
import shlex
import string
import random


class GlobalCog(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.ext.commands.Bot = bot
        bot.remove_command('help')

    @commands.command(name='report')
    @commands.guild_only()
    async def cogs_report(self, ctx: commands.Context, id: int):
        """Report a member or guild by passing on the id"""
        if ctx.guild.id != 514806589174054923:
            return await ctx.send(f'Please report people using the dark hub.')

        valid_channels = (515557891038642191, 515557800617836544)

        if ctx.channel.id not in valid_channels:
            return await ctx.send(f'Please use the <#515557891038642191> to report a member or <#515557800617836544> to report a server.')

        guild = discord.utils.get(self.bot.guilds, id=id)
        member = await self.bot.get_user_info(id)

        id_type = 'guild' if guild else 'member'

        if not guild and not member:
            return await ctx.send(f'No member or guild found using the supplied id: {id}')

        if id_type == 'guild' and guild and ctx.channel.id != 515557800617836544:
            return await ctx.send(f'Please use channel <#515557800617836544> to report a guild.')
        if id_type == 'member' and member and ctx.channel.id != 515557891038642191:
            return await ctx.send(f'Please use channel <#515557891038642191> to report a member.')

        case_number = ''.join(random.SystemRandom().choices(string.ascii_uppercase + string.digits, k=5))

        g: discord.Guild = ctx.guild

        category: discord.CategoryChannel = discord.utils.get(g.categories, id=517261374825693194)

        channel_name = f'Case-{"M" if id_type == "member" else "G"}{case_number}'

        filer: discord.Member = ctx.author

        overwrites = {
            g.default_role: discord.PermissionOverwrite(read_messages=False),
            filer: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True, read_message_history=True)
        }

        case_channel = await g.create_text_channel(name=channel_name, category=category, overwrites=overwrites)

        await ctx.send(f'Succesfully created case: {case_number}, check the {channel_name} channel to view your case.')
        await case_channel.send(f'Please also provide us with all the information you have concerning your case against {id_type.capitalize()}: {guild.name if id_type == "guild" else member.name}')

    @commands.command(name='commands', aliases=['help', 'h', 'com', 'c'])
    @commands.guild_only()
    async def cogs_help(self, ctx):
        """Retrieve the help box"""
        emb = discord.Embed(title='%s - help' % ctx.guild.name, description='', color=ctx.message.author.color, colour=ctx.message.author.color)
        order = dict()
        for c in self.bot.commands:
            try:
                if not c.hidden and await c.can_run(ctx):
                    if not order.get(c.module):
                        order[c.module] = dict()
                    order[c.module][c.name] = c.help
            except (commands.CheckFailure, commands.NotOwner, Exception) as e:
                pass
        for module_name, cmds in order.items():
            emb.add_field(name=module_name.split('.')[1], value='\n'.join([f'**{com_name}**: {com_desc}' for com_name, com_desc in cmds.items()]), inline=False)
        await ctx.send(embed=emb)

    @commands.command(name='admin_commands', aliases=['ah', 'ac'])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def cogs_admin_help(self, ctx: commands.Context, *, command: str = None):
        """Retrieve the current Admin help box"""
        emb = discord.Embed(title='%s - admin help' % ctx.guild.name, description='', color=ctx.message.author.color, colour=ctx.message.author.color)
        order = dict()
        comm: commands.Command = ctx.command
        for c in self.bot.commands:
            try:
                if c.hidden and await c.can_run(ctx) or comm.name == c.name:
                    if not order.get(c.module):
                        order[c.module] = dict()
                    order[c.module][c.name] = c.help
            except (commands.CheckFailure, commands.NotOwner, Exception) as e:
                pass
        for module_name, cmds in order.items():
            if not command:
                if len(cmds.keys()) >= 10:
                    for i in range(int(len(cmds.keys()) / 10)):
                        emb.add_field(name=module_name.split('.')[1], value='\n'.join([f'**{com_name}**: {com_desc}' for com_name, com_desc in list(cmds.items())[i:i+10 if i + 10 <= len(cmds.keys()) - 1 else len(cmds.keys()) - 1]]), inline=False)
                else:
                    emb.add_field(name=module_name.split('.')[1], value='\n'.join([f'**{com_name}**: {com_desc}' for com_name, com_desc in cmds.items()]), inline=False)
            if command:
                emb.add_field(name=module_name.split('.')[1], value='\n'.join([f'**{com_name}**: {com_desc}' for com_name, com_desc in cmds.items() if com_name == command]), inline=False)

        await ctx.send(embed=emb)

    @commands.command(name='ranks', aliases=['r', 'rank'])
    @commands.guild_only()
    async def cogs_ranks(self, ctx):
        """Display the existing ranks in the server"""
        chain = DB().fetch_one(query='SELECT * FROM promotions WHERE guild_id=%s', params=(ctx.guild.id,))
        try:
            c_guild_id, c_ranks = chain
        except (ValueError, TypeError) as e:
            print(f'Received error upon executing ranks by user: {ctx.author.name}, with error: {str(e)}')
            return await ctx.send('Chain not setup, set it up first!')

        chain: list = json.loads(c_ranks)
        chain.reverse()
        tmp_chain = chain
        chain = []
        for role_id in tmp_chain:
            chain.append(ctx.guild.get_role(role_id))
        embed = discord.Embed(title=f'Ranks for guild: {ctx.guild.name}', description='\uFEFF', color=ctx.author.color)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        embed.add_field(name=f'Found {len(chain)} ranks.', value='\n'.join([c.name for c in chain]))

        await ctx.send(embed=embed)

    @commands.command(name='server', aliases=['serverinfo', 'info', 'statistics'])
    @commands.guild_only()
    async def cogs_statistics(self, ctx: commands.Context, *, selections: str = None):
        """Display the server statistics"""
        guild: discord.Guild = ctx.guild
        from models.Server import Server
        g = Server.get_by_id(guild.id)
        table_role: discord.Role = discord.utils.get(guild.roles, name='The Table')
        selection_options = dict(
            owner=guild.owner.mention if not g.network else table_role.mention,
            total_members=guild.member_count,
            people=len([m for m in guild.members if not m.bot]),
            bots=len([m for m in guild.members if m.bot]),
            created_at=guild.created_at,
        )

        message_content = []
        import shlex
        if selections:
            selections = shlex.split(selections)
        else:
            selections = selection_options.keys()

        for selection in selections:
            selection = selection.replace(" ", "_")
            message_content.append(f'{selection}: {selection_options[selection]}')

        emb = discord.Embed(title=f'{guild.name} - Statistics', description='', color=ctx.message.author.color, colour=ctx.message.author.color)
        emb.add_field(name='Info:', value=('\n'.join(message_content)).replace('_', ' '), inline=False)
        await ctx.send(embed=emb)


def setup(bot):
    bot.add_cog(GlobalCog(bot))
