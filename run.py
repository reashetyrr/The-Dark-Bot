import discord
import config
import shlex
import json
import methods
import socket
from models.Message import Message
from rabbit_handler import RabbitMQHandler as rabbit

# from server.models.Command import is_command
# from server.models.User import User
# from server.models.DB import DB


client = methods.client = discord.Client()
rabbit = rabbit()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
addr_info = (config.tdb_process['host'], 9998)
print('Starting socket on %s:%d' % addr_info)
sock.connect(addr_info)
process_client = sock
print('Connected to socket')


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    # embi_leave_messages = ['bye bitch', 'Hey bitch! Read', 'User Join', 'User Leave']
    #
    # if message.channel.id == 476811184578887680 and (any(leave in message.content for leave in embi_leave_messages) or (len(message.embeds) > 0 and message.author.id == 172002275412279296)):
    #     return await message.delete()
    #
    # embi_leave_messages.append('tdb!cleanup')
    #
    # if 'tdb!cleanup' == message.content and message.channel.id == 476811184578887680:
    #     channel: discord.TextChannel = message.channel
    #
    #     async for msg in channel.history(limit=300):
    #         if any(leave in msg.content for leave in embi_leave_messages) or len(msg.embeds) > 0 and msg.author.id == 172002275412279296:
    #             await msg.delete()
    #     return

    try:
        content_spit = shlex.split(message.content)
        command = content_spit.pop(0) if len(content_spit) >= 1 else message.content
    except ValueError:
        command = message.content

    if command.startswith('tdb!') and message.channel.id == 488652189510664217:

        msg = Message(
            message_type='message',
            message_action=content_spit[0] if content_spit and len(content_spit) >= 1 else None,
            message_command=command,
            message_parameters=json.dumps(content_spit).replace('\"', '\'') if content_spit and len(content_spit) >= 1 else None,
            message_server_id=message.guild.id,
            message_channel_id=message.channel.id,
            message_user_id=message.author.id,
            message_raw_message=message.content.replace('\"', '\\"'),
        )
        send_message(msg)
        print('send message %s' % msg.__json__())

    # command_object = is_command(command)
    # if command_object:
    #     from server import commands
    #     tmp = getattr(commands, command_object['name'].capitalize())
    #     await tmp(command=command_object, author=message.author, client=client, message=message, params=content_spit if len(content_spit) >= 1 else None).execute()


@client.event
async def on_raw_reaction_add(payload):
    user = payload.user_id
    if user == client.user.id:
        return

    if payload.channel_id != 488652189510664217:
        return

    msg = Message(
        message_type='reaction',
        message_action='react',
        message_command='reaction_added',
        message_server_id=payload.guild_id,
        message_channel_id=payload.channel_id,
        message_user_id=payload.user_id,
        message_raw_message=str(payload.emoji),
        message_parameters=''
    )
    send_message(msg)
    print('send message %s' % msg.__json__())

    # channel: discord.TextChannel = client.get_channel(payload.channel_id)
    # user: discord.Member = channel.guild.get_member(user)
    #
    # poll = DB().fetch_one('SELECT * FROM polls WHERE message_id=?', (payload.message_id,))
    # if poll:
    #     # is poll
    #     # return await channel.send('Thank you {user} for reacting'.format(user=user.mention))
    #     pass
    #
    # rolemenu = DB().fetch_one('SELECT * FROM rolemenus WHERE message_id=?', (payload.message_id,))
    # if rolemenu:
    #     role_name = DB().fetch_one('SELECT name FROM rolemenu_roles WHERE rolemenu_id=? AND icon=?', (rolemenu[0], str(payload.emoji)))[0]
    #     role = discord.utils.get(channel.guild.roles, name=role_name)
    #     await user.add_roles(role)


@client.event
async def on_raw_reaction_remove(payload):
    if payload.channel_id != 488652189510664217:
        return
    msg = Message(
        message_type='reaction',
        message_action='react',
        message_command='reaction_removed',
        message_server_id=payload.guild_id,
        message_channel_id=payload.channel_id,
        message_user_id=payload.user_id,
        message_raw_message='',
        message_parameters=''
    )
    send_message(msg)
    print('send message %s' % msg.__json__())

    # user = payload.user_id
    # channel: discord.TextChannel = client.get_channel(payload.channel_id)
    # user: discord.Member = channel.guild.get_member(user)
    #
    # rolemenu = DB().fetch_one('SELECT * FROM rolemenus WHERE message_id=?', (payload.message_id,))
    # if rolemenu:
    #     role_name = DB().fetch_one('SELECT name FROM rolemenu_roles WHERE rolemenu_id=? AND icon=?',
    #                                (rolemenu[0], str(payload.emoji)))[0]
    #     role = discord.utils.get(channel.guild.roles, name=role_name)
    #     if role:
    #         await user.remove_roles(role)


@client.event
async def on_member_join(member):
    if member.name == client.user.name:
        return

    msg = Message(
        message_type='join',
        message_action='join',
        message_command='user_join',
        message_server_id=member.guild.id,
        message_channel_id=0,  # any channel, its a join
        message_user_id=member.id,
        message_raw_message='',
        message_parameters=''
    )
    send_message(msg)
    print('send message %s' % msg.__json__())

    # if 'discord.gg' in member.name:
    #     await member.guild.ban(member, reason='No channel promoting allowed in user names', delete_message_days=1)
    #     channel = discord.utils.get(member.guild.channels, channel='tdb-logs')
    #     if not channel:
    #         channel = await member.guild.create_channel('tdb-logs')
    #     return await channel.send_message('Succesfully banned member: %s, reason: promoting using name' % member.mention)
    # return User(member.id, member.avatar_url if member.avatar_url else member.default_avatar_url, member.created_at, member.discriminator, member.mention, member.name, member.display_name, {})


def send_message(message: Message):
    rabbit.send(message=message)

async def send_discord_message(message: Message):
    if message.type == 'embed':
        # generate embed
        msg = json.loads(message.message) # retrieve the body which is send as dict
        embed = discord.Embed()
    elif message.type == 'rolemenu':
        params = json.loads(message.parameters)
        guild = client.get_guild(message.server_id)
        user = client.get_user(message.user_id)
        role = discord.utils.get(guild.roles, name=params['rolemenu_name'])

        if message.command == 'reaction_added':
            await user.add_roles(role)
        else:
            await user.remove_roles(role)
    else:


@client.event
async def on_ready():
    current_user = client.user
    print('Logged in as')
    print(current_user)
    print('-------------')
    await client.change_presence(activity=discord.Game(config.game))
    print('set custom game status')

client.run(config.bot_credentials['token'])

while True:
    try:
        received = process_client.recv(2048)
        print('received through process listener %s' % received)
        message = Message.parse_json(received)
        send_discord_message(message)
        # handle here
    except EOFError:
        pass  # Nothing found just continue
