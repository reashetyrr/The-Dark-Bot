import discord
from discord.ext import commands
from checks import is_plugin_enabled, has_bot_role
from models.Server import Server
from datetime import datetime, timedelta, date
from typing import Union


valid_message_types = ['edit_message', 'delete_message', 'ban_user', 'unban_user', 'user_join', 'user_leave', 'user_warn']


class LoggingCog(commands.Cog):
    """All listeners for logging"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.last_trigger_id = None

    @staticmethod
    def get_logging_channel(guild: discord.Guild, logging_object: int):
        return discord.utils.get(guild.channels, id=logging_object)

    @commands.command(name='setup_logging', hidden=True)
    @commands.guild_only()
    @has_bot_role(administrator=True)
    async def cogs_logging_setup(self, ctx: commands.Context, logging_type: str, channel_to_log_to: discord.TextChannel = None):
        if logging_type not in valid_message_types and logging_type != 'all':
            return await ctx.send(f'Invalid logging type, must be one of: {",".join(valid_message_types)} or all')

        guild: Server = Server.get_by_id(ctx.guild.id)
        if not guild.bot_settings.get('logging'):
            guild.bot_settings['logging'] = dict()

        if not channel_to_log_to:
            channel_to_log_to = discord.utils.get(ctx.guild.channels, name='tdb-logs')

        assert channel_to_log_to, 'No channel has been specified, tried to get the channel: "tdb-logs" but this channel was not found.'
        if logging_type == 'all':
            for logging_type in valid_message_types:
                guild.bot_settings['logging'][logging_type] = channel_to_log_to.id
                guild.save()
                await ctx.send(f'Succesfully added logging for the type: {logging_type}, into channel: {channel_to_log_to.mention}')
        else:
            guild.bot_settings['logging'][logging_type] = channel_to_log_to.id
            guild.save()
            await ctx.send(f'Succesfully added logging for the type: {logging_type}, into channel: {channel_to_log_to.mention}')

    @commands.Cog.listener()
    @is_plugin_enabled('logging')
    async def on_message_edit(self, message_before_edit: discord.Message, message_after_edit: discord.Message):
        guild: Server = Server.get_by_id(message_after_edit.guild.id)
        author: discord.Member = message_before_edit.author
        if message_before_edit.clean_content == message_after_edit.clean_content:
            return

        if guild.bot_settings.get('logging') and guild.bot_settings['logging'].get('edit_message') and not author.bot:
            edit_message_logging_object: int = guild.bot_settings['logging']['edit_message']
            logging_channel: discord.TextChannel = LoggingCog.get_logging_channel(message_after_edit.guild, edit_message_logging_object)
            embed: discord.Embed = discord.Embed(title=f'Message edit', color=discord.Color.orange(), colour=discord.Color.orange(), description=f'Message edited in: {message_after_edit.channel.mention}')
            embed.set_thumbnail(url=author.avatar_url)
            embed.add_field(name='Original message:', value=message_before_edit.clean_content, inline=False)
            embed.add_field(name='New message:', value=message_after_edit.clean_content, inline=False)
            embed.set_footer(text=f'{author.display_name} {datetime.now():%B %d, %Y}CET')
            await logging_channel.send(embed=embed)

    @commands.Cog.listener()
    @is_plugin_enabled('logging')
    async def on_member_join(self, member: discord.Member):
        guild: Server = Server.get_by_id(member.guild.id)

        if guild.bot_settings.get('logging') and guild.bot_settings['logging'].get('user_join'):
            user_join_logging_object: int = guild.bot_settings['logging']['user_join']
            logging_channel: discord.TextChannel = LoggingCog.get_logging_channel(member.guild, user_join_logging_object)
            embed: discord.Embed = discord.Embed(title=f'Event', color=discord.Color.green(), colour=discord.Color.green(), description=f'User has joined the guild.')
            embed.set_thumbnail(url=member.avatar_url)
            datelimit = datetime.now() - timedelta(days=7)
            join_values: list = [f'Joined at: {member.joined_at}', f'Nickname: {member.display_name}', f'Bot: {"Yes" if member.bot else "No"}', f'Created at: {member.created_at}', f'Threat: {"None" if member.created_at < datelimit else "**New account**"}', f'User id: {member.id}']
            embed.add_field(name='Join details', value='\n'.join(join_values))
            await logging_channel.send(embed=embed)

    @commands.Cog.listener()
    @is_plugin_enabled('logging')
    async def on_member_remove(self, member: discord.Member):
        guild: Server = Server.get_by_id(member.guild.id)
        if isinstance(member, discord.User):
            return  # user was banned already
        if guild.bot_settings.get('logging') and guild.bot_settings['logging'].get('user_leave'):
            user_join_logging_object: int = guild.bot_settings['logging']['user_leave']
            logging_channel: discord.TextChannel = LoggingCog.get_logging_channel(member.guild, user_join_logging_object)
            embed: discord.Embed = discord.Embed(title=f'User Leave', color=discord.Color.red(), colour=discord.Color.red(), description=f'User has left the guild.')
            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name='Leave details', value=f'User "{member.display_name}"(id: {member.id}) has left the guild at: {datetime.now():%B %d, %Y}CET.')
            await logging_channel.send(embed=embed)

    @commands.Cog.listener()
    @is_plugin_enabled('logging')
    async def on_member_ban(self, guild: discord.Guild, member: Union[discord.Member, discord.User]):
        server: Server = Server.get_by_id(guild.id)
        if isinstance(member, discord.User):
            return  # user was banned already
        if not server.bot_settings:
            server.bot_settings = dict()
            server.save()
        if server.bot_settings.get('logging') and server.bot_settings['logging'].get('ban_user'):
            user_join_logging_object: int = server.bot_settings['logging']['ban_user']
            logging_channel: discord.TextChannel = LoggingCog.get_logging_channel(member.guild, user_join_logging_object)
            embed: discord.Embed = discord.Embed(title=f'User Ban', color=discord.Color.red(), colour=discord.Color.red(), description=f'User has been banned.')
            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name='Ban details', value=f'User "{member.display_name}"(id: {member.id}) has been banned at: {datetime.now():%B %d, %Y}CET.')
            await logging_channel.send(embed=embed)

    @commands.Cog.listener()
    @is_plugin_enabled('logging')
    async def on_raw_bulk_message_delete(self, payload: discord.RawBulkMessageDeleteEvent):
        server: Server = Server.get_by_id(payload.guild_id)
        guild: discord.Guild = self.bot.get_guild(payload.guild_id)

        if server.bot_settings.get('logging') and server.bot_settings['logging'].get('delete_message'):
            user_join_logging_object: int = server.bot_settings['logging']['delete_message']
            logging_channel: discord.TextChannel = LoggingCog.get_logging_channel(guild, user_join_logging_object)
            embed: discord.Embed = discord.Embed(title=f'Bulk message deletion', color=discord.Color.orange(), colour=discord.Color.orange(), description=f'Multiple messages have been deleted.')
            embed.set_thumbnail(url=guild.icon_url)
            channel: discord.TextChannel = guild.get_channel(payload.channel_id)
            embed.add_field(name='Deletion details', value=f'At: {datetime.now():%B %d, %Y}CET there has been a deletion of {len(payload.message_ids)} messages in channel: {channel.name}')
            await logging_channel.send(embed=embed)

    @commands.Cog.listener()
    @is_plugin_enabled('logging')
    async def on_message_delete(self, message: discord.Message):
        server: Server = Server.get_by_id(message.guild.id)
        guild: discord.Guild = message.guild

        if self.last_trigger_id and self.last_trigger_id == message.id:
            return

        self.last_trigger_id = message.id
        if server.bot_settings.get('logging') and server.bot_settings['logging'].get('delete_message'):
            user_join_logging_object: int = server.bot_settings['logging']['delete_message']
            logging_channel: discord.TextChannel = LoggingCog.get_logging_channel(guild, user_join_logging_object)
            embed: discord.Embed = discord.Embed(title=f'Message deletion', color=discord.Color.orange(), colour=discord.Color.orange(), description=f'A message has been deleted.')
            embed.set_thumbnail(url=guild.icon_url)
            channel: discord.TextChannel = message.channel
            embed.add_field(name='Deletion details', value=f'There has been a deletion of a message in channel: {channel.mention}.')
            embed.add_field(name='Message:', value=message.clean_content)
            embed.add_field(name='Author:', value=message.author.mention)
            embed.set_footer(text=f'{message.author.display_name} {datetime.now():%B %d, %Y}CET')
            await logging_channel.send(embed=embed)

    @commands.Cog.listener()
    @is_plugin_enabled('logging')
    async def on_member_warned(self, member: discord.Member, reason: str, warnings: list, warner: discord.Member = None):
        server: Server = Server.get_by_id(member.guild.id)
        guild: discord.Guild = member.guild
        if server.bot_settings.get('logging') and server.bot_settings['logging'].get('user_warn'):
            user_join_logging_object: int = server.bot_settings['logging']['user_warn']
            logging_channel: discord.TextChannel = LoggingCog.get_logging_channel(guild, user_join_logging_object)
            embed: discord.Embed = discord.Embed(title=f'Member warned', color=discord.Color.orange(), colour=discord.Color.orange(), description=f'A has received an warning.')
            embed.set_thumbnail(url=guild.icon_url)
            warning_messages = "\n".join([f'id ({t_id}): {t_reason}' if t_reason else f'id ({t_id}): No reason supplied' for t_id,t_user_id,t_guild_id,t_reason in warnings])
            embed.add_field(name='Warning:', value=f'User: {member.mention} has received the following warning: {reason}, this is warning number {len(warnings)}')
            embed.add_field(name='Warnings:', value=f'User: {member.mention} has the following warnings: \n {warning_messages}')
            if warner:
                embed.set_footer(text=f'Staffmember {warner.display_name} has given out the warning at {datetime.now():%B %d, %Y}CET')
            await logging_channel.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(LoggingCog(bot))
