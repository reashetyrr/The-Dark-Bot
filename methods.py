import discord
from models.Message import Message


client = None


def generate_embed(message: Message):
    return ''


async def send_discord_message(message, channel_id, guild_id, embed=True):
    guild = client.get_guild(guild_id)
    channel = discord.utils.get(guild.channels, channel_id)
    if embed:
        await channel.send_message(embed=message)
    else:
        await channel.send_message(message)