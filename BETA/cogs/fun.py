import random
import discord
import BETA.helpers
from jellyfish import jaro_distance
from config import assets
from models.User import User
from models.neverhaveieverqueston import NeverHaveIEverQueston
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType


class FunCog:
    def __init__(self, bot):
        self.bot: discord.ext.commands.Bot = bot

    @commands.command(name='kiss')
    @commands.guild_only()
    @commands.cooldown(5, 60, BucketType.channel)
    async def cog_kiss(self, ctx, members: commands.Greedy[discord.Member], *, message: str = None):
        """Kiss a member"""
        if len(members) == 0:
            return await ctx.send(f'Please target atleast one member.')
        members = ', '.join([member.mention for member in members])
        await ctx.send(f'{members} you have been kissed by {ctx.message.author.mention}', file=discord.File(random.choice(assets['kissing'])))

    @commands.command(name='fuck', aliases=['rape'])
    @commands.guild_only()
    @commands.is_nsfw()
    @commands.cooldown(5, 600, BucketType.channel)
    async def cog_fuck(self, ctx, members: commands.Greedy[discord.Member], *, message: str = None):
        """Fuck a member"""
        if len(members) == 0:
            return await ctx.send(f'Please target atleast one member.')
        targets = []
        action = 'fucked' if ctx.invoked_with == 'fuck' else 'raped'
        for member in members:
            user = User.get_by_id(member.id)
            if user.plugins.get('immunity') and 'fuck' in user.plugins.get('immunity'):
                plural = 'fucking' if ctx.invoked_with == 'fuck' else 'raping'
                return await ctx.send(f'{ctx.message.author.mention} instead of {plural} {user.mention} you have been {action} by {user.mention} instead', file=discord.File(random.choice(assets['fucking'])))
            targets.append(user)
        members = ', '.join([member.mention for member in targets])
        await ctx.send(f'{members} you have been {action} by {ctx.message.author.mention}', file=discord.File(random.choice(assets['fucking'])))

    @commands.command(name='never_have_i_ever', aliases=['nhie'])
    @commands.guild_only()
    @commands.is_nsfw()
    async def cog_nhie(self, ctx: commands.Context):
        """Get a random Never Have I Ever question"""
        questions = NeverHaveIEverQueston.get_all()
        question: NeverHaveIEverQueston = random.choice(questions)

        await ctx.send(question.question)

    @commands.command(name='love')
    @commands.guild_only()
    async def cog_love(self, ctx: commands.Context, users: commands.Greedy[discord.Member]):
        """Calculate love between 2 users, ping 1 member to calculate YOUR love with them"""
        if len(users) == 1:
            target_member, host_member = (users[0], ctx.author)
        else:
            target_member, host_member = (users[1], users[0])

        if target_member == host_member:
            return await ctx.send(f'110%, one should love him/herself')
        # return await ctx.send(f'{random.randint(0,100)}%')
        member_one_name, member_two_name = (host_member.display_name, target_member.display_name)
        await ctx.send(f'{int(jaro_distance(member_one_name, member_two_name) * 100)}%')
        # member_one_characters, member_two_characters = (list(set([x for x in member_one_name])), list(set([x for x in member_two_name])))
        #
        # for _ in member_one_characters:
        #     member_one_char_occurences[_] = member_one_name.count(_)
        # for _ in member_two_characters:
        #     member_two_char_occurences[_] = member_two_name.count(_)
        #
        # love: list = []
        # for _ in member_one_characters:
        #     love.append(member_two_name.count(_) * member_one_char_occurences[_])
        #
        # love_number: int = 0
        # for l in love:
        #     love_number += l
        #
        # member_one_count, member_two_count = len([x for x in member_one_name]), len([x for x in member_two_name])
        # max_num: int = 0
        # if member_one_count > member_two_count:
        #     for _ in member_one_char_occurences:
        #         max_num += member_one_char_occurences[_] * 2
        # else:
        #     for _ in member_two_char_occurences:
        #         max_num += member_two_char_occurences[_] * 2
        #
        # if self.bot.owner_id in (host_member.id, target_member.id):
        #     love_number = max_num
        #
        # await ctx.send(f'{int((love_number/max_num) * 100)}%')


def setup(bot):
    bot.add_cog(FunCog(bot))
