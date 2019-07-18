import config as config
import discord
import sys
from discord.ext import commands
from models.DB import DB


def get_prefix(bot, message):
    if not message.guild:
        return '..'
    return commands.when_mentioned_or(*config.tdb_settings['prefixes'])(bot, message)


initial_extensions = [
    'cogs.logging',
    'cogs.events',
    'cogs.global',
    'cogs.custom',
    'cogs.configuration',
    'cogs.plugin',
    'cogs.administration',
    'cogs.poll',
    'cogs.fun',
    'cogs.levels',
    'cogs.currency',
    'cogs.rolemenu',
    'cogs.tests'
    # 'cogs.marketplace'
    # 'cogs.pokegym',
]


bot = commands.AutoShardedBot(command_prefix=get_prefix, description='The Dark Bot Reloaded', case_insensitive=True, owner_id=197106036899971072, max_message=9000000)


if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except (Exception, ModuleNotFoundError) as e:
            print(f'Failed to load extension {extension}, {e}', file=sys.stderr)


# @bot.check
# async def is_tdr(ctx):
#     return ctx.guild and ctx.guild.id == 479604566162145280
#
# @bot.before_invoke
# async def before_invocation(ctx: discord.ext.commands.Context):
#     from BETA.checks import is_plugin_enabled
#     try:
#         is_plugin_enabled('levels')
#         # xp gathering here
#         # very ugly try to do this using cogs
#     except commands.CheckFailure:
#         # its not activated so just bypass
#         pass


@bot.event
async def on_ready():
    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')
    await bot.change_presence(activity=discord.Game(name=config.game))
    print(f'Successfully logged in and booted...!')


bot.run(config.bot_credentials['token'], bot=True, reconnect=True)
