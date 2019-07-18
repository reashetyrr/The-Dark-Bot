import discord
from discord.ext import commands
from models.User import User
from models.Server import Server
import random
import asyncio
import typing


class CurrencyCog(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    @commands.command(name='currency', aliases=['money', 'coins', 'bal', 'balance'])
    @commands.guild_only()
    async def cogs_currency(self, ctx: commands.Context, member: typing.Optional[discord.Member] = None):
        """Check the amount of coins you have"""
        member: User = User.get_by_id(member.id if member else ctx.author.id)
        guild: Server = Server.get_by_id(ctx.guild.id)
        currency_name = guild.currency_name if guild.currency_name else 'coins'
        if member.id == ctx.author.id:
            await ctx.send(f'You currently have {member.plugins.get("currency", 0):,} {currency_name}')
        else:
            await ctx.send(f'{member.mention} currently has {member.plugins.get("currency", 0):,} {currency_name}')

    @commands.command(name='add_coins', aliases=['coinsadd', 'addcoins'], hidden=True)
    @commands.is_owner()
    async def cogs_add_coins(self, ctx: commands.Context, coins: int, members: commands.Greedy[discord.Member]):
        """Add coins to members"""
        guild: Server = Server.get_by_id(ctx.guild.id)
        m_list = [m.mention for m in members]
        members = [User.get_by_id(m.id) for m in members]
        currency_name = guild.currency_name if guild.currency_name else 'coins'
        for member in members:
            if not member.plugins.get('currency'):
                member.plugins['currency'] = 0

            member.plugins['currency'] += coins
            member.save()
        await ctx.send(f'{",".join(m_list)} you have been gifted {coins:,} {currency_name}')

    @commands.command(name='reset_coins', aliases=['money_reset'])
    @commands.guild_only()
    async def cogs_reset_coins(self, ctx: commands.Context):
        """Reset the current amount of coins back to 0"""
        def is_author(message: discord.Message):
            return message.author == ctx.author
        user: User = User.get_by_id(ctx.author.id)
        guild: Server = Server.get_by_id(ctx.guild.id)
        currency_name = guild.currency_name if guild.currency_name else 'coins'
        await ctx.send(f'Are you sure you want to reset your {currency_name}?')
        try:
            reply: discord.Message = await self.bot.wait_for('message', timeout=10, check=is_author)
            if reply.clean_content in ('y', 'yes', 'yup', 'yush', 'j', 'ja'):
                user.plugins['currency'] = 0
                user.save()
                await ctx.send('Succesfully reset currency')
            else:
                await ctx.send('No succesfull reply, deleting reset request')
        except asyncio.TimeoutError:
            await ctx.send('Did not receive an response in time, deleting reset request')

    @commands.command(name='givecoins')
    @commands.guild_only()
    async def cogs_give(self, ctx: commands.Context, member: discord.Member, coins: typing.Union[int, str]):
        guild: Server = Server.get_by_id(server_id=ctx.guild.id)
        user: User = User.get_by_id(user_id=ctx.author.id)
        if coins == 'all':
            coins = user.plugins.get('currency', 0)
        if type(coins) == 'str' and ',' in coins:
            coins = int(coins.replace(',', ''))
        if coins <= 0:
            return await ctx.send(f'{coins:,} is not a valid amount of {guild.currency_name if guild.currency_name else "coins"}')
        if coins > user.plugins.get('currency', 0):
            return await ctx.send(f'You dont have {coins:,} {guild.currency_name if guild.currency_name else "coins"}')

        target: User = User.get_by_id(user_id=member.id)
        target.plugins['currency'] = target.plugins.get('currency', 0) + coins
        target.save()

        user.plugins['currency'] -= coins
        user.save()
        await ctx.send(f'Succesfully gave {member.mention} {coins:,} {guild.currency_name if guild.currency_name else "coins"}, you now have: {user.plugins["currency"]:,} {guild.currency_name if guild.currency_name else "coins"}')

    @commands.command(name='blackjack', aliases=['bj'])
    @commands.guild_only()
    async def cogs_blackjack(self, ctx: commands.Context, coins: typing.Union[int, str]):
        guild: Server = Server.get_by_id(server_id=ctx.guild.id)
        user: User = User.get_by_id(user_id=ctx.author.id)
        if coins == 'all':
            coins = user.plugins.get('currency', 0)
        if type(coins) == 'str' and ',' in coins:
            coins = int(coins.replace(',', ''))
        if coins <= 0:
            return await ctx.send(f'{coins:,} is not a valid amount of {guild.currency_name if guild.currency_name else "coins"}')
        if coins > user.plugins.get('currency', 0):
            return await ctx.send(f'You dont have {coins:,} {guild.currency_name if guild.currency_name else "coins"}')

        card_options: list = [
            dict(
                name='ace',
                values=[11, 1]
            ),
            dict(
                name='two',
                values=[2, 2]
            ),
            dict(
                name='three',
                values=[3, 3]
            ),
            dict(
                name='four',
                values=[4, 4]
            ),
            dict(
                name='five',
                values=[5, 5]
            ),
            dict(
                name='6',
                values=[6, 6]
            ),
            dict(
                name='seven',
                values=[7, 7]
            ),
            dict(
                name='eight',
                values=[8, 8]
            ),
            dict(
                name='nine',
                values=[9, 9]
            ),
            dict(
                name='ten',
                values=[10, 10]
            ),
            dict(
                name='jack',
                values=[10, 10]
            ),
            dict(
                name='king',
                values=[10, 10]
            ),
            dict(
                name='queen',
                values=[10, 10]
            ),
        ]
        card_suits: list = [
            ('spades', '\N{black spade suit}'),
            ('hearts', '\N{black heart suit}'),
            ('diamonds', '\N{black diamond suit}'),
            ('clubs', '\N{black club suit}')
        ]
        options = []
        for _ in range(4):
            options.append((random.choice(card_suits)[1], random.choice(card_options)['values']))

        cards_selected: dict = dict(player=options[:2], dealer=options[2:])
        total_score = dict(
            player=cards_selected['player'][0][1][0] + cards_selected['player'][1][1][0] if cards_selected['player'][0][1][0] + cards_selected['player'][1][1][0] <= 21 else cards_selected['player'][0][1][1] + cards_selected['player'][1][1][1],
            dealer=cards_selected['dealer'][0][1][0] + cards_selected['dealer'][1][1][0] if cards_selected['dealer'][0][1][0] + cards_selected['dealer'][1][1][0] <= 21 else cards_selected['dealer'][0][1][1] + cards_selected['dealer'][1][1][1]
        )
        dealer_string = ' '.join([cards_selected['dealer'][_][0] + (str(cards_selected['dealer'][_][1][0]) if cards_selected['dealer'][_][1][0] == cards_selected['dealer'][_][1][1] else '/'.join([str(cards_selected['dealer'][_][1][0]), str(cards_selected['dealer'][_][1][1])])) for _ in range(2)])
        player_string = ' '.join([cards_selected['player'][_][0] + (str(cards_selected['player'][_][1][0]) if cards_selected['player'][_][1][0] == cards_selected['player'][_][1][1] else '/'.join([str(cards_selected['player'][_][1][0]), str(cards_selected['player'][_][1][1])])) for _ in range(2)])
        dealer_bust = ''
        player_bust = ''
        if total_score['dealer'] == 21:
            dealer_bust = 'BLACKJACK'
        elif total_score['dealer'] > 21:
            dealer_bust = 'BUST'
        if total_score['player'] == 21:
            player_bust = 'BLACKJACK'
        elif total_score['player'] > 21:
            player_bust = 'BUST'
        await ctx.send(f'Dealer ({total_score["dealer"]}): {dealer_string} {dealer_bust} | Player ({total_score["player"]}): {player_string} {player_bust}')

    @commands.command(name='hl')
    @commands.guild_only()
    async def cogs_higher_lower(self, ctx: commands.Context, coins: typing.Union[int, str]):
        """Play higher or lower for the chance of doubling the amount of coins used for bet"""
        guild: Server = Server.get_by_id(server_id=ctx.guild.id)
        user: User = User.get_by_id(user_id=ctx.author.id)
        if coins == 'all':
            coins = user.plugins.get('currency', 0)
        if type(coins) == 'str' and ',' in coins:
            coins = int(coins.replace(',', ''))
        if coins <= 0:
            return await ctx.send(f'{coins:,} is not a valid amount of {guild.currency_name if guild.currency_name else "coins"}')
        if coins > user.plugins.get('currency', 0):
            return await ctx.send(f'You dont have {coins:,} {guild.currency_name if guild.currency_name else "coins"}')

        if coins > 10000:
            difficulty = 25
        elif coins > 100000:
            difficulty = 50
        else:
            difficulty = 10

        random_number = random.randint(0, difficulty)
        await ctx.send(f'The random number is: {random_number}, type higher (h) ,lower (l) or equal')
        reply = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)
        rand = random.randint(0, difficulty)
        if (rand > random_number and (reply.clean_content.lower() == 'higher' or reply.clean_content.lower() == 'h')) or (rand < random_number and (reply.clean_content.lower() == 'lower' or reply.clean_content.lower() == 'l')):
            user.plugins['currency'] += coins
            user.save()
            await ctx.send(f'You have guessed correct, the number was: {rand}, you have gained {coins:,} {guild.currency_name if guild.currency_name else "coins"}')
        elif rand == random_number and reply.clean_content.lower() == 'equal':
            user.plugins['currency'] += coins * 3
            user.save()
            await ctx.send(f'You have guessed correct, you have gained 3 times the bet, {coins*3:,} {guild.currency_name if guild.currency_name else "coins"} have been added to your pouch')
        elif (rand < random_number and (reply.clean_content.lower() == 'higher' or reply.clean_content.lower() == 'h')) or (rand > random_number and (reply.clean_content.lower() == 'lower' or reply.clean_content.lower() == 'l')) or rand != random_number and reply.clean_content.lower() == 'equal':
            user.plugins['currency'] -= coins
            user.save()
            await ctx.send(f'You have guessed incorrect, the number was: {rand}, you have lost {coins:,} {guild.currency_name if guild.currency_name else "coins"}')


def setup(bot: discord.ext.commands.Bot):
    bot.add_cog(CurrencyCog(bot))

# @bot.before_invoke
# async def before_command_invocation(ctx: discord.ext.commands.Context):
#     from random import randint
#     gained_xp = randint()
