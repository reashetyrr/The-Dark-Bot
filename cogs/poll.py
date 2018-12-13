import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from checks import is_plugin_enabled
import shlex


class PollCog:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='quote')
    @commands.cooldown(5, 60, BucketType.channel)
    @commands.guild_only()
    @is_plugin_enabled(plugin_name='poll')
    async def cog_quote(self, ctx, message_id: int, *, reply: str = None):
        """Quote a message by adding an message id"""
        if not message_id:
            return await ctx.send('Missing message id')

        mess = await ctx.channel.get_message(message_id)

        embed = discord.Embed(title='\uFEFF', description=mess.content, color=mess.author.color)
        embed.set_author(name=mess.author.name, icon_url=mess.author.avatar_url)

        await ctx.message.delete()
        await ctx.send(reply if reply else '', embed=embed)

    @commands.command(name='poll', aliases=['cp'], hidden=True)
    @commands.cooldown(5, 60, BucketType.channel)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @is_plugin_enabled(plugin_name='poll')
    async def cog_poll(self, ctx, poll_name, poll_question, *, options: str):
        """Create a poll using a name, question and options"""
        options = shlex.split(options)
        if len(options) > 10:
            return await ctx.send('Please limit the options to 10 max')
        choices = [
            dict(
                choice=None,
                emote='\N{DIGIT ZERO}\N{COMBINING ENCLOSING KEYCAP}',
            ),
            dict(
                choice=None,
                emote='\N{DIGIT ONE}\N{COMBINING ENCLOSING KEYCAP}',
            ),
            dict(
                choice=None,
                emote='\N{DIGIT TWO}\N{COMBINING ENCLOSING KEYCAP}',
            ),
            dict(
                choice=None,
                emote='\N{DIGIT THREE}\N{COMBINING ENCLOSING KEYCAP}',
            ),
            dict(
                choice=None,
                emote='\N{DIGIT FOUR}\N{COMBINING ENCLOSING KEYCAP}',
            ),
            dict(
                choice=None,
                emote='\N{DIGIT FIVE}\N{COMBINING ENCLOSING KEYCAP}',
            ),
            dict(
                choice=None,
                emote='\N{DIGIT SIX}\N{COMBINING ENCLOSING KEYCAP}',
            ),
            dict(
                choice=None,
                emote='\N{DIGIT SEVEN}\N{COMBINING ENCLOSING KEYCAP}',
            ),
            dict(
                choice=None,
                emote='\N{DIGIT EIGHT}\N{COMBINING ENCLOSING KEYCAP}',
            ),
            dict(
                choice=None,
                emote='\N{DIGIT NINE}\N{COMBINING ENCLOSING KEYCAP}',
            ),
        ]

        for index, option in enumerate(options):
            choices[index]['choice'] = option

        tmp_choices = choices.copy()

        choices = []
        for option in tmp_choices:
            if option['choice']:
                choices.append(option)

        emb = discord.Embed(title=f'{ctx.guild.name} - {poll_name}', description=poll_question, color=ctx.message.author.color, colour=ctx.message.author.color)

        emb.add_field(name='Answers:', value='\n'.join([f'{option["emote"]} {option["choice"]}' for option in choices]))

        poll = await ctx.send(embed=emb)

        for option in choices:
            await poll.add_reaction(option['emote'])


def setup(bot):
    bot.add_cog(PollCog(bot))
