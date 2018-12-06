import discord
import config
import shlex
from models.Command import is_command
from models.User import User
from models.DB import DB


client = discord.Client()


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

    if message.channel.id == 488652189510664217:
        return

    if len(message.embeds) > 0:
        return

    command_object = is_command(command)
    if command_object:
        import commands
        tmp = getattr(commands, command_object['name'].capitalize())
        await tmp(command=command_object, author=message.author, client=client, message=message, params=content_spit if len(content_spit) >= 1 else None).execute()


@client.event
async def on_raw_reaction_add(payload):
    user = payload.user_id
    if user == client.user.id:
        return
    if payload.channel_id == 501356854975135745:
        return
    channel: discord.TextChannel = client.get_channel(payload.channel_id)
    user: discord.Member = channel.guild.get_member(user)

    poll = DB().fetch_one('SELECT * FROM polls WHERE message_id=?', (payload.message_id,))
    if poll:
        # is poll
        # return await channel.send('Thank you {user} for reacting'.format(user=user.mention))
        pass

    rolemenu = DB().fetch_one('SELECT * FROM rolemenus WHERE message_id=?', (payload.message_id,))
    if rolemenu:
        role_name = DB().fetch_one('SELECT name FROM rolemenu_roles WHERE rolemenu_id=? AND icon=?', (rolemenu[0], str(payload.emoji)))[0]
        role = discord.utils.get(channel.guild.roles, name=role_name)
        await user.add_roles(role)


@client.event
async def on_raw_reaction_remove(payload):
    user = payload.user_id
    channel: discord.TextChannel = client.get_channel(payload.channel_id)
    user: discord.Member = channel.guild.get_member(user)

    rolemenu = DB().fetch_one('SELECT * FROM rolemenus WHERE message_id=?', (payload.message_id,))
    if rolemenu:
        role_name = DB().fetch_one('SELECT name FROM rolemenu_roles WHERE rolemenu_id=? AND icon=?',
                                   (rolemenu[0], str(payload.emoji)))[0]
        role = discord.utils.get(channel.guild.roles, name=role_name)
        if role:
            await user.remove_roles(role)


@client.event
async def on_member_join(member):
    if member.name == client.user.name:
        return

    if 'discord.gg' in member.name:
        await member.guild.ban(member, reason='No channel promoting allowed in user names', delete_message_days=1)
        channel = discord.utils.get(member.guild.channels, channel='tdb-logs')
        if not channel:
            channel = await member.guild.create_channel('tdb-logs')
        return await channel.send('Succesfully banned member: %s, reason: promoting using name' % member.mention)
    if member.guild.id == 479604566162145280:
        role = discord.utils.get(member.guild.roles, name='Users')
        await member.add_roles(role)
        channel = member.guild.get_channel(479715873817362432)
        await channel.send('{} Welcome to The Dark Room, please setup your roles at: <#480057290649501706> and be sure to read our <#479604566166339584>'.format(member.mention))
        channel = member.guild.get_channel(480091660605456420) # logs channel
        embed = discord.Embed(title='Server Join', description='', color=config.embed_color, colour=config.embed_color)
        embed.add_field(name='User', value='{} Joined us'.format('%s(%d)' % (member.name, member.id)), inline=False)
        await channel.send(embed=embed)
    if member.guild.id == 501843757042237450:
        role = discord.utils.get(member.guild.roles, name='member')
        await member.add_roles(role)
    return User(member.id, member.avatar_url if member.avatar_url else member.default_avatar_url, member.created_at, member.discriminator, member.mention, member.name, member.display_name, {})


@client.event
async def on_member_remove(member):
    if member.guild.id == 479604566162145280:
        channel = member.guild.get_channel(480091660605456420) # logs channel
        embed = discord.Embed(title='Server Leave', description='', color=config.embed_color, colour=config.embed_color)
        embed.add_field(name='User', value='{} Left us'.format('%s(%d)' % (member.name, member.id)), inline=False)
        await channel.send(embed=embed)


@client.event
async def on_ready():
    current_user = client.user
    guilds = client.guilds
    print('Logged in as')
    print(current_user)
    print('-------------')
    await client.change_presence(activity=discord.Game(config.game))
    print('set custom game status')

client.run(config.bot_credentials['token'])
