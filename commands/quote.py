import discord
import config
from models.Command import Command


class Quote(Command):
    def __init__(self, **kwargs):
        Command.__init__(self, **kwargs)

    async def execute(self):
        if not await self.run_test():
            return

        if not self.params or len(self.params) == 0:
            return await self.message.channel.send('Syntax: tdb!quote {message_id} {message to state in the quote}')

        message_id = self.params.pop(0)
        try:
            message_to_send = self.params.pop(0)
        except:
            message_to_send = ''

        message = await self.message.channel.get_message(message_id)

        embed = discord.Embed(title=self.message.author.name, description=message_to_send, color=config.embed_color, colour=config.embed_color)
        embed.add_field(name='Quote:', value='%s: %s' % (message.author.mention, message.content))

        await self.message.delete()

        return await self.message.channel.send(embed=embed)