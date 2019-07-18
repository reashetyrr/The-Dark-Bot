import discord
from typing import Optional
from discord.ext import commands
from models.User import User


class MarketCog(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.ext.commands.Bot = bot

    @commands.group(name='market')
    @commands.guild_only()
    @commands.is_nsfw()
    async def cogs_market(self, ctx: commands.Context):
        """Marketplace commands"""
        if not ctx.subcommand_passed:
            command_list = self.bot.get_command(name='market').commands

            embed = discord.Embed(title='%s - Market help' % ctx.guild.name, description='', color=ctx.message.author.color, colour=ctx.message.author.color)

            order = dict()
            for c in command_list:
                if await c.can_run(ctx):
                    order[c.name] = c.help
            embed.add_field(name='Commands:', value='\n'.join([f'**{com_name}**: {com_desc}' for com_name, com_desc in order.items()]) if len(order.keys()) > 0 else 'No commands found', inline=False)
            await ctx.send(embed=embed)




def setup(bot):
    bot.add_cog(MarketCog(bot))
