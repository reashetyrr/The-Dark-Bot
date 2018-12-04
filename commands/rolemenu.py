import discord
import re
from config import embed_color
from models.DB import DB
from models.Command import Command


def generate_embed(title: str, fields: list):
    embed = discord.Embed(title=title, description='', color=embed_color, colour=embed_color)
    for field in fields:
        values = '\n'.join(field['values']) if field['newlines'] else field['values']
        embed.add_field(name=field['title'], value=values, inline=False)
    return embed


class Rolemenu(Command):
    def __init__(self, **kwargs):
        Command.__init__(self, **kwargs)
        rolemenus = DB().fetch_all('SELECT * FROM rolemenus WHERE guild_id=?', (self.message.guild.id,))
        self.rolemenus = {}
        for menu in rolemenus:
            d_id, d_guild_id, d_name, d_message_id = menu
            self.rolemenus[d_name] = Menu(name=d_name, message_id=d_message_id, guild=d_guild_id, menu_id=d_id)

    async def execute(self):
        # await self.message.delete()
        if not await self.run_test():
            return
        rolemenus = self.rolemenus
        channel = self.message.channel

        params = self.params
        if None is params or len(params) == 0:
            # empty, give explaination
            embed = generate_embed('Rolemenu help', [
                dict(
                    title='Rolemenu commands',
                    values=[
                        'list: Display all the available rolemenus for the server',
                        'create: Create a rolemenu (tdb!rolemenu create gender male{\N{BLACK HEART}} female{\N{PURPLE HEART}})',
                        'remove: Delete a rolemenu by name (tdb!rolemenu delete gender) this will also remove the existing menu',
                        # 'edit: Edit an existing rolemenu (tdb!rolemenu edit gender male{\N{YELLOW HEART}} female{\N{PURPLE HEART}})',
                        'render: Render an existing rolemenu (tdb!rolemenu render gender)'
                    ],
                    newlines=True,
                )
            ])
            return await channel.send(embed=embed)

        command = params.pop(0)

        if command == 'list':
            embed = generate_embed('Rolemenu\'s available', [
                dict(
                    title='List',
                    values=['%s (%d Roles)' % (key, len(value.roles)) for key, value in self.rolemenus.items()] if self.rolemenus else 'No menu\'s found, create some first!',
                    newlines=True if self.rolemenus else False,
                )
            ])
        elif command == 'create':
            if len(params) < 2:
                embed = generate_embed('Rolemenu Create', [
                    dict(
                        title='Error',
                        values='No title or role found!',
                        newlines=False,
                    ),
                    dict(
                        title='Example',
                        values='tdb!rolemenu create gender male{\N{BLACK HEART}} female{\N{PURPLE HEART}}',
                        newlines=False
                    )
                ])
                return await channel.send(embed=embed)
            role_menu_title = params.pop(0)
            rolemenu = DB().insert_return_id('INSERT INTO rolemenus(guild_id,name,message_id) VALUES(?,?,?)', (self.message.guild.id, role_menu_title, '')) # leave the message_id empty while it needs to be generated first
            roles = []
            val = ['Succesfully added the rolemenu(%s):' % role_menu_title]
            for role in params:
                role_name, role_icon = re.findall('(.+)\{([^[\]]*)\}', role)[0]
                roles.append((rolemenu, role_icon, role_name))
                val.append('%s %s' % (role_icon, role_name))
            DB().execute_many('INSERT INTO rolemenu_roles(rolemenu_id,icon,name) values(?,?,?)', roles)
            embed = generate_embed('Rolemenu', [
                dict(
                    title='Create',
                    values=val,
                    newlines=True
                )
            ])
        elif command == 'render':
            if len(params) < 1:
                embed = generate_embed('Rolemenu render', [
                    dict(
                        title='Error',
                        values='No rolemenu name is supplied!',
                        newlines=False,
                    ),
                    dict(
                        title='Example',
                        values='tdb!rolemenu render gender',
                        newlines=False
                    )
                ])
                return await channel.send(embed=embed)
            menu_name = params.pop(0)
            menu_id, guild_id, menu_name, message_id = DB().fetch_one('SELECT * FROM rolemenus WHERE name=? AND guild_id=?', (menu_name, self.message.guild.id))
            rolemenu = Menu(menu_id=menu_id, guild=guild_id, name=menu_name)

            values = ['%s %s' % (r.icon, r.name) for r in rolemenu.roles]

            embed = generate_embed('Rolemenu', [
                dict(
                    title=menu_name,
                    values=values,
                    newlines=True
                )
            ])

            message = await channel.send(embed=embed)
            DB().execute('UPDATE rolemenus SET message_id=? WHERE id=?', (message.id, menu_id))

            for role in rolemenu.roles:
                await message.add_reaction(role.icon)
            return
        elif command == 'remove':
            if len(params) < 1:
                embed = generate_embed('Rolemenu Remove', [
                    dict(
                        title='Error',
                        values='No rolemenu name is supplied!',
                        newlines=False,
                    ),
                    dict(
                        title='Example',
                        values='tdb!rolemenu remove gender',
                        newlines=False
                    )
                ])
                return await channel.send(embed=embed)
            menu_id, guild_id, menu_name, message_id = DB().fetch_one('SELECT * FROM rolemenus WHERE name=? AND guild_id=?', (params[0], self.message.guild.id))
            if not menu_id:
                embed = generate_embed('Rolemenu', [
                    dict(
                        title='Remove',
                        values='Unknown rolemenu name given: "%s"' % params[0],
                        newlines=False,
                    )
                ])
                return await channel.send(embed=embed)
            try:
                message = await self.message.guild.get_message(message_id)
                await message.delete()
            except:
                pass  # non existing skip

            DB().execute('DELETE FROM rolemenus WHERE id=?', (menu_id,))
            DB().execute('DELETE FROM rolemenu_roles WHERE rolemenu_id=?', (menu_id,))
            embed = generate_embed('Rolemenu', [
                dict(
                    title='Remove',
                    values='Succesfully removed rolemenu "%s"' % menu_name,
                    newlines=False,
                )
            ])
        else:
            embed = generate_embed('Rolemenu', [
                dict(
                    title="Error",
                    values='Unrecognised command, type tdb!rolemenu for the commands.',
                    newlines=False,
                )
            ])
        return await channel.send(embed=embed)


class Menu(object):
    def __init__(self, menu_id: int, guild: int, name: str, message_id: int=None):
        self.id = menu_id
        self.guild = guild
        self.name = name
        self.roles = []
        self.message_id = message_id
        tmp_roles = DB().fetch_all('SELECT * FROM rolemenu_roles WHERE rolemenu_id=?', (menu_id,))
        for r in tmp_roles:
            role_id, rolemenu_id, icon, name = r
            self.roles.append(Role(role_id=role_id, icon=icon, name=name))


class Role(object):
    def __init__(self, role_id: int, icon: str, name: str):
        self.id = role_id
        self.icon = icon
        self.name = name
