import discord
from models.Command import Command


class Moderation(Command):
    def __init__(self, **kwargs):
        Command.__init__(self, **kwargs)
        self.log_channel = discord.utils.find(lambda c: 'log' in str(c), self.message.guild.channels)

    async def execute(self):
        if not await self.run_test():
            return

        guild: discord.Guild = self.message.guild
        log_channel = discord.utils.find(lambda c: 'log' in str(c), guild.channels)

        action = self.params.pop(0)
        id_or_tag = self.params.pop(0)
        reason = self.params.pop(0)



