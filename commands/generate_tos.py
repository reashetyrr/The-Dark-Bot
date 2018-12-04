import discord
import config
from models.Command import Command


class Generatetos(Command): 
    def __init__(self, **kwargs):
        Command.__init__(self, **kwargs)

    async def execute(self):
        if not await self.run_test():
            return

        if None is not self.params and 'embi' in self.params:
            return await self.message.channel.send('GTFO, i dont support embi in any way anymore!')
            # rules = '\n'.join(config.rules_embi)
            # extended_rules = '\n'.join(config.rules_embi_extended)
            #
            # embed = discord.Embed(title='FAMILY\N{HEAVY BLACK HEART}\N{EARTH GLOBE EUROPE-AFRICA}\N{TONGUE} - Server ToS', description='', color=config.embed_color, colour=config.embed_color)
            # embed.add_field(name='Rules', value=rules, inline=False)

            # embed.set_author(name='MOM\N{BLACK HEART}', icon_url='https://cdn.discordapp.com/avatars/388339529922379787/9d0cfe3c02eb36ed6b253995bc8d29e7.jpg?size=1024')

            # await self.message.channel.send(embed=embed)

            # embed.clear_fields()
            # embed.add_field(name='Rules', value=extended_rules, inline=False)
            # return await self.message.channel.send(embed=embed)

        if None is not self.params and 'kitty' in self.params:
            rules = '\n'.join(config.rules_kitty)
            extended_rules = '\n'.join(config.rules_kitty_extended)
            
            embed = discord.Embed(title='Server Rules', description='', color=config.embed_color, colour=config.embed_color)
            embed.add_field(name='Rules', value=rules, inline=False)
            embed.add_field(name='Continued', value=extended_rules, inline=False)
            embed.add_field(name='Please help the server grow by sharing this link!', value='https://discord.gg/YTjuWVv', inline=False)

            embed.set_author(name=self.message.guild.name, icon_url='')
            await self.message.channel.purge()
            return await self.message.channel.send(embed=embed)

        else:
            rules = config.rules

            embed = discord.Embed(title='The Dark Room - Server ToS', description='', color=config.embed_color, colour=config.embed_color)
            embed.add_field(name='About', value=rules['about'], inline=False)
            embed.add_field(name='General Rules', value='\n'.join(rules['general']), inline=False)

            for rule in rules['verification']:
                r = rules['verification'][rule]
                embed.add_field(name=r['title'], value=r['message'], inline=False)

            embed.add_field(name='Notice', value='If you plan on breaking any of the rules, we suggest you leave in advance', inline=False)
            try:
                await self.message.channel.purge()
            except discord.errors.HTTPException:
                await self.message.channel.send('Messages are too old to purge, manual removal required.')

        message = await self.message.channel.send(embed=embed)
        return message
