import discord
from discord.ext import commands
from checks import is_plugin_enabled


class PokegymCog:
    def __init__(self, bot):
        self.bot: discord.ext.commands.Bot = bot

    @commands.group(name='pokegym', aliases=['pg'], hidden=True)
    @commands.guild_only()
    @is_plugin_enabled(plugin_name='pokegym')
    async def cogs_pokegym(self, ctx):
        """Pokegym commands | WORK IN PROGRESS!!!"""
        if not ctx.subcommand_passed:
            commands = self.bot.get_command(name='pokegym').commands

            emb = discord.Embed(title='%s - pokegym help' % ctx.guild.name, description='', color=ctx.message.author.color, colour=ctx.message.author.color)

            order = dict()
            for c in commands:
                if not c.hidden and await c.can_run(ctx):
                    order[c.name] = c.help
            emb.add_field(name='Commands:', value='\n'.join([f'**{com_name}**: {com_desc}' for com_name, com_desc in order.items()]) if len(order.keys()) > 0 else 'No commands found', inline=False)
            await ctx.send(embed=emb)

    @cogs_pokegym.command(name='setup', hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def cogs_pokegym_setup(self, ctx, gyms: int):
        """setup the module to be used, this includes making the category and channels"""
        pokecord = discord.utils.get(ctx.guild.members, id=36597565560874598)
        if not pokecord:
            return await ctx.send('To setup and use the pokegym module, you need to have Pokécord in your server.')


def setup(bot):
    bot.add_cog(PokegymCog(bot))
