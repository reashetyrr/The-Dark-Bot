import discord
from discord.ext import commands
from models.Server import Server


class ConfigurationCog:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='load', hidden=True)
    @commands.is_owner()
    async def cog_load(self, ctx, *, cog: str):
        """Command which Loads a Module. Remember to use dot path. e.g: cogs.owner"""
        try:
            self.bot.load_extension(cog)
        except (Exception, ModuleNotFoundError) as e:
            await ctx.send(f'**ERROR:** {type(e).__name__} - {e}')
        else:
            await ctx.send('**SUCCESS**')

    @commands.command(name='unload', hidden=True)
    @commands.is_owner()
    async def cog_unload(self, ctx, *, cog: str):
        """Command which Unloads a Module. Remember to use dot path. e.g: cogs.owner"""
        try:
            self.bot.unload_extension(cog)
        except (Exception, ModuleNotFoundError) as e:
            await ctx.send(f'**ERROR:** {type(e).__name__} - {e}')
        else:
            await ctx.send('**SUCCESS**')

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def cog_reload(self, ctx, *, cog: str):
        """Command which Reloads a Module. Remember to use dot path. e.g: cogs.owner"""
        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except (Exception, ModuleNotFoundError) as e:
            await ctx.send(f'**ERROR:** {type(e).__name__} - {e}')
        else:
            await ctx.send('**SUCCESS**')

    @commands.command(name='fix_servers', hidden=True)
    @commands.is_owner()
    async def cog_fix_servers(self, ctx: commands.Context):
        servers = Server.get_all()
        for server in servers:
            try:
                d_server: discord.Guild = self.bot.get_guild(server.id) # discord.utils.get(self.bot.guilds, id=server.id)
                server.icon_url = d_server.icon_url_as(format='png')
                server.name = d_server.name
                server.member_count = len([m for m in d_server.members if not m.bot])
                server.save()
            except AttributeError as e:
                await ctx.send(f'Skipping server {server.id}, bot is not in server anymore')
        await ctx.send(f'Succesfully updated all the known servers')

def setup(bot):
    bot.add_cog(ConfigurationCog(bot))
