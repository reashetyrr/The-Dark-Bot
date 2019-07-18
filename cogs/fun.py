import random
import discord
import shlex
import urllib3
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from config import assets
from models.DB import DB
from models.User import User
from models.quote import Quote
from models.neverhaveieverqueston import NeverHaveIEverQueston
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from typing import Union
import qrcode
import tempfile


class FunCog(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.ext.commands.Bot = bot

    @commands.group(name='nsfw')
    @commands.guild_only()
    @commands.cooldown(5, 60, BucketType.member)
    @commands.is_nsfw()
    async def cogs_nsfw(self, ctx: commands.Context):
        pass

    @cogs_nsfw.command(name='search')
    @commands.guild_only()
    @commands.is_nsfw()
    @commands.cooldown(5, 60, BucketType.member)
    async def cogs_nsfw_search(self, ctx: commands.Context, *, tags: str):
        import requests
        from random import choice
        import os.path
        tags = shlex.split(tags)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
        }
        res = requests.get(f'https://www.sex.com/search/gifs?query={"+".join(tags)}', headers=headers)

        soup = BeautifulSoup(res.content, 'html5lib')
        container = soup.find(id='masonry_container')
        images = container.find_all('img')
        try:
            image = choice(images)

            img_src = image['data-src']

            req = requests.get(img_src)
            # http = urllib3.PoolManager()
            # req = http.request('GET', img_src, preload_content=False)

            with open(os.path.join(f'./assets/downloads/{img_src[img_src.rfind("/")+1:]}'), 'wb+') as fp:
                fp.write(req.content)

            await ctx.send(f'I found this', file=discord.File(os.path.join(f'./assets/downloads/{img_src[img_src.rfind("/")+1:]}')))
        except IndexError:
            await ctx.send(f'I couldnt find anythhing with the tags: {", ".join(tags)}')

    @commands.command(name='qrcode')
    @commands.guild_only()
    async def cogs_qrcode(self, ctx, *, message: str = None):
        if not message or len(message) == 0:
            return
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(message)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        tmp_name = tmp.name
        tmp.close()
        img.save(tmp_name, format='png')

        await ctx.send(file=discord.File(tmp_name))

    @commands.command(name='kiss')
    @commands.guild_only()
    @commands.cooldown(5, 60, BucketType.channel)
    async def cogs_kiss(self, ctx, members: commands.Greedy[discord.Member], *, message: str = None):
        """Kiss a member"""
        
        if len(members) == 0:
            return await ctx.send(f'Please target atleast one member.')
        members = ', '.join([member.mention for member in members])
        await ctx.send(f'{members} you have been kissed by {ctx.message.author.mention}', file=discord.File(random.choice(assets['kissing'])))

    @commands.command(name='fuck', aliases=['rape'])
    @commands.guild_only()
    @commands.is_nsfw()
    @commands.cooldown(5, 600, BucketType.channel)
    async def cogs_fuck(self, ctx, members: commands.Greedy[discord.Member], *, message: str = None):
        """Fuck a member"""
        
        if len(members) == 0:
            return await ctx.send(f'Please target atleast one member.')
        targets = []
        action = 'fucked' if ctx.invoked_with == 'fuck' else 'raped'
        for member in members:
            user = User.get_by_id(member.id)
            if user.plugins.get('immunity') and 'fuck' in user.plugins.get('immunity') or user.id == 256070670029553666:
                plural = 'fucking' if ctx.invoked_with == 'fuck' else 'raping'
                return await ctx.send(f'{ctx.message.author.mention} instead of {plural} {user.mention} you have been {action} by {user.mention} instead', file=discord.File(random.choice(assets['fucking'])))
            targets.append(user)
        members = ', '.join([member.mention for member in targets])
        await ctx.send(f'{members} you have been {action} by {ctx.message.author.mention}', file=discord.File(random.choice(assets['fucking'])))

    @commands.command(name='choke')
    @commands.guild_only()
    @commands.is_nsfw()
    @commands.cooldown(5, 600, BucketType.channel)
    async def cogs_choke(self, ctx, members: commands.Greedy[discord.Member], *, message: str = None):
        """Choke a member"""
        
        if len(members) == 0:
            return await ctx.send(f'Please target atleast one member.')
        targets = []
        action = 'choked'
        for member in members:
            user = User.get_by_id(member.id)
            if user.plugins.get('immunity') and 'choke' in user.plugins.get('immunity') or user.id == 256070670029553666:
                plural = 'choking'
                return await ctx.send(f'{ctx.message.author.mention} instead of {plural} {user.mention} you have been {action} by {user.mention} instead', file=discord.File(random.choice(assets['choking'])))
            targets.append(user)
        members = ', '.join([member.mention for member in targets])
        await ctx.send(f'{members} you have been {action} by {ctx.message.author.mention}', file=discord.File(random.choice(assets['choking'])))

    @commands.command(name='spank')
    @commands.guild_only()
    @commands.is_nsfw()
    @commands.cooldown(5, 600, BucketType.channel)
    async def cogs_spank(self, ctx, members: commands.Greedy[discord.Member], *, message: str = None):
        """Choke a member"""
        
        if len(members) == 0:
            return await ctx.send(f'Please target atleast one member.')
        targets = []
        action = 'spanked'
        for member in members:
            user = User.get_by_id(member.id)
            if user.plugins.get('immunity') and 'spank' in user.plugins.get('immunity') or user.id == 256070670029553666:
                plural = 'spanking'
                return await ctx.send(f'{ctx.message.author.mention} instead of {plural} {user.mention} you have been {action} by {user.mention} instead', file=discord.File(random.choice(assets['spanking'])))
            targets.append(user)
        members = ', '.join([member.mention for member in targets])
        await ctx.send(f'{members} you have been {action} by {ctx.message.author.mention}', file=discord.File(random.choice(assets['spanking'])))

    @commands.command(name='cuddle')
    @commands.guild_only()
    async def cogs_cuddle(self, ctx, members: commands.Greedy[discord.Member], *, message: str = None):
        """Choke a member"""
        
        if len(members) == 0:
            return await ctx.send(f'Please target atleast one member.')
        targets = []
        action = 'cuddled'
        for member in members:
            user = User.get_by_id(member.id)
            if user.plugins.get('immunity') and 'cuddle' in user.plugins.get('immunity') or user.id == 256070670029553666:
                plural = 'cuddling'
                return await ctx.send(f'{ctx.message.author.mention} instead of {plural} {user.mention} you have been {action} by {user.mention} instead', file=discord.File(random.choice(assets['cuddling'])))
            targets.append(user)
        members = ', '.join([member.mention for member in targets])
        await ctx.send(f'{members} you have been {action} by {ctx.message.author.mention}', file=discord.File(random.choice(assets['cuddling'])))

    # @commands.command(name='hug')
    # @commands.guild_only()
    # @commands.cooldown(5, 600, BucketType.channel)
    # async def cogs_hug(self, ctx, members: commands.Greedy[discord.Member], *, message: str = None):
    #     """Choke a member"""
    #     if len(members) == 0:
    #         return await ctx.send(f'Please target atleast one member.')
    #     targets = []
    #     action = 'hugged'
    #     for member in members:
    #         user = User.get_by_id(member.id)
    #         if user.plugins.get('immunity') and 'hug' in user.plugins.get('immunity'):
    #             plural = 'hugging'
    #             return await ctx.send(f'{ctx.message.author.mention} instead of {plural} {user.mention} you have been {action} by {user.mention} instead', file=discord.File(random.choice(assets['spanking'])))
    #         targets.append(user)
    #     members = ', '.join([member.mention for member in targets])
    #     await ctx.send(f'{members} you have been {action} by {ctx.message.author.mention}', file=discord.File(random.choice(assets['hugging'])))

    @commands.command(name='never_have_i_ever', aliases=['nhie'])
    @commands.guild_only()
    @commands.is_nsfw()
    async def cogs_nhie(self, ctx: commands.Context):
        """Get a random Never Have I Ever question"""
        questions = NeverHaveIEverQueston.get_all()
        question: NeverHaveIEverQueston = random.choice(questions)

        await ctx.send(question.question)

    @commands.command(name='love')
    @commands.guild_only()
    async def cogs_love(self, ctx: commands.Context, users: commands.Greedy[discord.Member]):
        """Calculate love between 2 users, ping 1 member to calculate YOUR love with them"""
        from hashlib import md5

        if len(users) == 1:
            target_member, host_member = (users[0], ctx.author)
        else:
            target_member, host_member = (users[1], users[0])

        # if 256070670029553666 in (target_member.id, host_member.id):
        #     return await ctx.send('0%')

        if target_member == host_member:
            return await ctx.send(f'110%, one should love him/herself')

        member_one_acii_number = 0
        for _ in md5(host_member.name.encode('utf-8')).hexdigest():
            member_one_acii_number += ord(_)

        member_one_acii_number -= int(host_member.discriminator)

        member_two_ascii_number = 0
        for _ in md5(target_member.name.encode('utf-8')).hexdigest():
            member_two_ascii_number += ord(_)

        member_two_ascii_number -= int(target_member.discriminator)

        if member_one_acii_number > member_two_ascii_number:
            res = int(abs(member_two_ascii_number / (member_one_acii_number / 100)))
        else:
            res = int(abs(member_one_acii_number / (member_two_ascii_number / 100)))

        # member_one_id, member_two_id = host_member.id, target_member.id
        #
        # res = int(abs(member_one_id - member_two_id) / ((member_one_id + member_two_id) / 100))
        if res < 80:
            res += 19
        elif res > 100:
            res = 100
        await ctx.send(f'{res}%')

    @commands.command(name='leaderboard', aliases=['lb', 'top'])
    @commands.guild_only()
    async def cogs_leaderboard(self, ctx: commands.Context):
        embed = discord.Embed(title=f'The dark bot leaderboards', color=ctx.author.color, colour=ctx.author.color, description='')
        users = User.get_all()

    @commands.command(name='angel', aliases=['ea', 'easter_egg'], hidden=True)
    @commands.guild_only()
    async def cogs_ea(self, ctx: commands.Context):
        await ctx.send(f'Bow down to the, bow down to <@256070670029553666>')

    @commands.command(name='ping')
    @commands.guild_only()
    async def cogs_fun_ping(self, ctx: commands.Context):
        if ctx.author.id == 466409084623519744:
            return await ctx.send('🍑💦🍆✊')
        current_time = datetime.now(timezone.utc).replace(tzinfo=None)
        created_at = ctx.message.created_at
        difference = current_time - created_at
        return await ctx.send(f'pong: {int(difference.microseconds / 1000)}ms')

    @commands.command(name='pdb')
    @commands.guild_only()
    async def cogs_fun_pdb(self, ctx: commands.Context):
        res = User.get_by_id(self.bot.owner_id)
        current_time = datetime.now(timezone.utc).replace(tzinfo=None)
        created_at = ctx.message.created_at
        difference = current_time - created_at
        return await ctx.send(f'Database pong: {round(difference.microseconds / 1000.0)} ms')

    @commands.command(name='emote_id')
    @commands.guild_only()
    async def cogs_fun_emote_id(self, ctx: commands.Context, emote: discord.PartialEmoji):
        return await ctx.send(emote.id)

    @commands.command(name='quotes')
    @commands.guild_only()
    async def cogs_fun_quotes(self, ctx: commands.Context, quote: str = None, member: Union[discord.Member, discord.User] = None, year: int = None):
        """add or get a random quote"""
        if not quote and not member and not year:
            quote: Quote = Quote.get_random(ctx.guild.id)
            try:
                member: discord.Member = ctx.guild.get_member(quote.user_id)
            except:
                member: User = User.get_by_id(quote.user_id)

            if not member:
                member: User = User.get_by_id(quote.user_id)
            await ctx.send(f'"{quote.quote}" - **{member.display_name}** {quote.year}')
            return
        if quote and not member:
            return await ctx.send('You need to ping the member to quote')
        if member and not year:
            return await ctx.send('Please supply the 4 digit year example: 2019')

        quote: Quote = Quote(quote=quote, user_id=member.id, year=year, guild_id=ctx.guild.id)
        quote.save()
        await ctx.send(f'Succesfully stored quote: "{quote.quote}" - {member.display_name} {quote.year}')

    @commands.command('list_quotes')
    @commands.guild_only()
    async def cogs_list_quotes(self, ctx: commands.Context, member: Union[discord.Member, int]):
        """List all quotes from a specific user"""
        if isinstance(member, int):
            member = User.get_by_id(member)
        quotes: list = Quote.get_by_user_id(ctx.guild.id, member.id)
        emb = discord.Embed(title=f'**{member.display_name}** - Quotes', description='', color=ctx.message.author.color, colour=ctx.message.author.color)
        emb.add_field(name='quotes', value='\n'.join([f'{quote.quote}' for quote in quotes]) if quotes else f'No quotes found for user {member.display_name}')
        await ctx.send(embed=emb)

    @commands.command('test_quote')
    @commands.guild_only()
    @commands.is_owner()
    async def cogs_test_quote(self, ctx: commands.Context, quote_id: int):
        """Display quote by id"""
        await ctx.message.delete()
        quote: Quote = Quote.get_by_id(quote_id=quote_id)
        try:
            member: discord.Member = ctx.guild.get_member(quote.user_id)
            await ctx.send(f'"{quote.quote}" - **{member.display_name}** {quote.year}')
        except:
            await ctx.send(f'The quote could not be found')


def setup(bot):
    bot.add_cog(FunCog(bot))
