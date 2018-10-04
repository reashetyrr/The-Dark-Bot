import discord
import config
from models.DB import DB
from models.Command import Command


class Poll(Command):
    def __init__(self, **kwargs):
        Command.__init__(self, **kwargs)

    async def execute(self):
        if not await self.run_test():
            return

        if not self.params or len(self.params) == 0:
            return await self.message.channel.send('Syntax: tdb!poll {title} {question} {optional answers(max 5)}')

        title = self.params.pop(0)

        if len(self.params) == 0:
            return await self.message.channel.send('To start a poll you need to add a question')

        if len(self.params) > 6:
            return await self.message.channel.send('Please limit the answers to 5.')

        options = [
            dict(
                name=self.params[1] if len(self.params) > 1 else 'Yes',
                icon='\N{DIGIT ONE}\N{COMBINING ENCLOSING KEYCAP}' if len(self.params) > 3 else '\N{WHITE HEAVY CHECK MARK}',
                unicode=u'\u0031 \u20E3' if len(self.params) > 3 else u'\u2705',
            ),
            dict(
                name=self.params[2] if len(self.params) > 2 else 'No',
                icon='\N{DIGIT TWO}\N{COMBINING ENCLOSING KEYCAP}' if len(self.params) > 3 else '\N{NEGATIVE SQUARED CROSS MARK}',
                unicode=u'\u0032 \u20E3' if len(self.params) > 3 else u"\u274E",
            ),
            dict(
                name=self.params[3] if len(self.params) > 3 else None,
                icon='\N{DIGIT THREE}\N{COMBINING ENCLOSING KEYCAP}',
                unicode=u'\u0033 \u20E3',
            ),
            dict(
                name=self.params[4] if len(self.params) > 4 else None,
                icon='\N{DIGIT FOUR}\N{COMBINING ENCLOSING KEYCAP}',
                unicode=u'\u0034 \u20E3',
            ),
            dict(
                name=self.params[5] if len(self.params) == 6 else None,
                icon='\N{DIGIT FIVE}\N{COMBINING ENCLOSING KEYCAP}',
                unicode=u'\u0035 \u20E3',
            ),
        ]
        embed = discord.Embed(title='%s - Poll' % self.message.guild.name, description='', color=config.embed_color, colour=config.embed_color)
        embed.add_field(name='Question:', value=self.params[0], inline=False)

        m = ''
        for x in range(len(self.params) - 1 if len(self.params) > 1 else 2):
            c = options[x]
            choice = '{emoticon} {name}'.format(emoticon=c['icon'], name=c['name'])
            m = '{old}\n{new}'.format(old=m, new=choice)

        embed.add_field(name='Choices:', value=m, inline=False)

        await self.message.channel.purge(limit=1)

        message = await self.message.channel.send(embed=embed)
        for x in range(len(self.params) - 1 if len(self.params) > 1 else 2):
            c = options[x]
            await message.add_reaction(c['icon'])

        DB().execute('INSERT INTO polls(message_id, title, server_id) VALUES(?, ?, ?)', (message.id, title, self.message.guild.id))
