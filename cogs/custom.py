import discord
from discord.ext import commands


class CustomCog(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.ext.commands.Bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        kit = discord.utils.get(message.mentions, id=445246802627919874) or discord.utils.get(message.mentions, id=513778297662996486)
        if kit and message.clean_content.startswith('->pat'):
            await message.channel.send(f'{kit.mention} Purrs and wags her tail', file=discord.File('assets/custom/neko_tail_wag.gif'))


def setup(bot):
    bot.add_cog(CustomCog(bot))
