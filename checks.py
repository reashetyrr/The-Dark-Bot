from models.DB import DB
import discord
from discord.ext import commands
from models.Server import Server
import json
import itertools


def is_plugin_enabled(plugin_name):
    async def plugin_enabled_check(ctx):
        guild = Server.get_by_id(ctx.guild.id)
        if not guild:
            raise commands.CheckFailure('The current server is not indexed, please ask an administrator to run the reindex command.')
        if plugin_name in guild.plugins:
            return True
        raise commands.CheckFailure(message=f'This command requires the plugin: {plugin_name}, please ask an administrator to enable the plugin.')
    return commands.check(plugin_enabled_check)


def is_network_server():
    async def network_server_check(ctx):
        guild: Server = Server.get_by_id(ctx.guild.id)
        if not guild:
            raise commands.CheckFailure('The current server is not indexed, please ask an administrator to run the reindex command.')
        if guild.network:
            return True
        raise commands.CheckFailure(message=f'This server is not a network server')
    return commands.check(network_server_check)


def has_bot_role(**perms):
    async def bot_role_check(ctx):
        guild: Server = Server.get_by_id(server_id=ctx.guild.id)
        author: discord.Member = ctx.author
        has_permission = False
        permissions = ctx.channel.permissions_for(ctx.author)

        missing = [perm for perm, value in perms.items() if getattr(permissions, perm, None) != value]

        mod_list = guild.bot_settings.get('moderators')
        admin_list = guild.bot_settings.get('administrators')
        if not missing:
            has_permission = True
        if has_permission or author.guild_permissions.administrator or ((perms.get('moderator') and (ctx.author.id in itertools.chain(mod_list, admin_list))) or perms.get('administrator') and ctx.author.id in admin_list):
            return True
        raise commands.MissingPermissions(missing)
    return commands.check(bot_role_check)


def is_guild_admin():
    async def guild_admin_check(ctx: commands.Context):
        guild: Server = Server.get_by_id(server_id=ctx.guild.id)


def is_plugin_activated(guild_id: int, plugin_name: str):
    guild = Server.get_by_id(guild_id)
    if guild:
        return plugin_name in guild.plugins if guild.plugins else False
    return False


def is_server_owner():
    async def server_owner_check(ctx):
        guild = ctx.guild
        if guild.owner is ctx.author:
            return True
        raise commands.NotOwner()
    return commands.check(server_owner_check)


def is_guild(guild: discord.Guild, failure_message: str = 'This command needs to be executed in a seperate guild.'):
    async def guild_check(ctx: commands.Context):
        if ctx.guild == guild:
            return True
        raise commands.CheckFailure(message=failure_message)
    return commands.check(guild_check)

