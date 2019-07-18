import discord
from discord.ext import commands
from models.Server import Server
from models.plugin import Plugin


class PluginCog(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.ext.commands.Bot = bot

    @commands.group(name='plugin', aliases=['p'], hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def cogs_plugin(self, ctx):
        """Plugin commands"""
        if not ctx.subcommand_passed:
            commands = self.bot.get_command(name='plugin').commands

            embed = discord.Embed(title='%s - Plugin help' % ctx.guild.name, description='', color=ctx.message.author.color, colour=ctx.message.author.color)

            order = dict()
            for c in commands:
                if await c.can_run(ctx):
                    order[c.name] = c.help
            embed.add_field(name='Commands:', value='\n'.join([f'**{com_name}**: {com_desc}' for com_name, com_desc in order.items()]) if len(order.keys()) > 0 else 'No commands found', inline=False)
            await ctx.send(embed=embed)

    @cogs_plugin.command(name='enable', aliases=['e'], hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def plugin_enable_cog(self, ctx, *, plugin_name: str):
        """Enable a plugin"""
        plugin = Plugin.get_plugin_by_name(plugin_name)
        embed = discord.Embed(title=f'{ctx.guild.name} - Plugin management', description='', color=ctx.message.author.color, colour=ctx.message.author.color)
        if not plugin:
            embed.add_field(name='Error', value=f'The specified plugin: "{plugin_name}" cannot be found, please check your spelling or execute: >[plugin|p] [list|l]')
            return await ctx.send(embed=embed)
        guild = Server.get_by_id(ctx.guild.id)
        if not guild:
            return await ctx.send(f'Server {ctx.guild.name} is not indexed, please run >reindex')
        guild.plugins.append(plugin_name)
        guild.save()
        embed.add_field(name='Success', value=f'Enabled the plugin "{plugin_name}".')
        await ctx.send(embed=embed)

        if plugin.on_enable:
            channels = plugin.on_enable.get('channels')
            if channels:
                for channel in channels:
                    if discord.utils.get(ctx.guild.channels, name=channel):
                        continue  # required channel already exist
                    d_guild: discord.Guild = ctx.guild
                    await d_guild.create_text_channel(name=channel)

    @cogs_plugin.command(name='list', aliases=['l'], hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def plugin_list_cog(self, ctx):
        """Retrieve the list of available plugins"""
        plugins = sorted(Plugin.get_all(), key=lambda k: k.name.lower())
        embed = discord.Embed(title=f'{ctx.guild.name} - Plugin management', description='', color=ctx.message.author.color, colour=ctx.message.author.color)
        if not plugins or 0 == len(plugins):
            embed.add_field(name='Error', value=f'Plugin database retrieval returned 0 results, please contact <@{self.bot.owner_id}>')
            return await ctx.send(embed=embed)
        plugin_list = [p.name for p in plugins]
        embed.add_field(name='Plugins:', value='\n'.join(plugin_list))
        await ctx.send(embed=embed)

    @cogs_plugin.command(name='disable', aliases=['d'], hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def plugin_disable_cog(self, ctx, *, plugin_name: str):
        """Disable a plugin, RUNS ON_DELETION"""
        plugin = Plugin.get_plugin_by_name(plugin_name)
        embed = discord.Embed(title=f'{ctx.guild.name} - Plugin management', description='', color=ctx.message.author.color, colour=ctx.message.author.color)
        if not plugin:
            embed.add_field(name='Error', value=f'The specified plugin: "{plugin_name}" cannot be found, please check your spelling or execute: >[plugin|p] [list|l]')
            return await ctx.send(embed=embed)
        guild = Server.get_by_id(ctx.guild.id)
        guild.plugins.remove(plugin_name)
        guild.save()
        embed.add_field(name='Success', value=f'Disabled the plugin "{plugin_name}".')
        await ctx.send(embed=embed)

        if plugin.on_disable:
            channels = plugin.on_disable.get('channels')
            if channels:
                for channel in channels:
                    try:
                        g_channel = discord.utils.get(ctx.guild.channels, name=channel)
                        await g_channel.delete()
                    except:
                        pass # do nothing, channels already deleted

    @cogs_plugin.command(name='disable_safe', aliases=['ds'], hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def plugin_disable_safe_cog(self, ctx, *, plugin_name: str):
        """Disable a plugin, SKIPS ON_DELETION"""
        plugin = Plugin.get_plugin_by_name(plugin_name)
        embed = discord.Embed(title=f'{ctx.guild.name} - Plugin management', description='', color=ctx.message.author.color, colour=ctx.message.author.color)
        if not plugin:
            embed.add_field(name='Error', value=f'The specified plugin: "{plugin_name}" cannot be found, please check your spelling or execute: >[plugin|p] [list|l]')
            return await ctx.send(embed=embed)
        guild = Server.get_by_id(ctx.guild.id)
        guild.plugins.remove(plugin_name)
        guild.save()
        embed.add_field(name='Success', value=f'Disabled the plugin "{plugin_name}".')
        await ctx.send(embed=embed)

    @cogs_plugin.command(name='enabled', aliases=['ep'], hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def plugin_enabled_cog(self, ctx):
        """Get a list of currently activated plugins"""
        guild = Server.get_by_id(ctx.guild.id)
        embed = discord.Embed(title=f'{ctx.guild.name} - Plugin management', description='', color=ctx.message.author.color, colour=ctx.message.author.color)
        embed.add_field(name='Enabled plugins:', value='\n'.join(guild.plugins))
        await ctx.send(embed=embed)


def setup(bot: discord.ext.commands.Bot):
    bot.add_cog(PluginCog(bot))
