import discord
from discord.ext import commands
from models.User import User
import typing

levels = [(28 * x) + 25 for x in range(100)]


class LevelsCog:
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        # bot.before_invoke(self.before_command_invocation)

    @commands.command(name='level')
    @commands.guild_only()
    async def cogs_level(self, ctx: commands.Context, member: typing.Optional[discord.Member] = None):
        member: User = User.get_by_id(member.id if member else ctx.author.id)
        await ctx.send(f'{member.mention} is level {member.plugins["prev_level"]}')

    @commands.command(name='add_xp', aliases=['xpadd', 'xpa', 'axp'], hidden=True)
    @commands.is_owner()
    async def cogs_add_xp(self, ctx: commands.Context, xp: int, members: commands.Greedy[discord.Member]):
        m_list = [m.mention for m in members]
        members = [User.get_by_id(m.id) for m in members]
        for member in members:
            member.plugins['level_experience'] += xp
            current_level = 0
            xp_required = 0
            for level, req_xp in enumerate(levels):
                xp_required += req_xp
                if member.plugins['level_experience'] > xp_required:
                    current_level = level + 1
            if current_level > member.plugins['prev_level']:
                member.plugins['prev_level'] = current_level
                await ctx.send(f'Congratulations {member.mention}, you have succesfully leveled up and are now level {current_level}')
        await ctx.send(f'Succesfully gave {xp}xp to: {",".join(m_list)}')


def setup(bot: discord.ext.commands.Bot):
    bot.add_cog(LevelsCog(bot))

# @bot.before_invoke
# async def before_command_invocation(ctx: discord.ext.commands.Context):
#     from random import randint
#     gained_xp = randint()
