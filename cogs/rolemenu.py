import discord
import shlex
import typing
import json
from discord.ext import commands
from checks import is_plugin_enabled
from models.rolemenu import Rolemenu
from models.rolemenu_emote import RolemenuEmote


class PluginCog:
    def __init__(self, bot):
        self.bot: discord.ext.commands.Bot = bot

    @commands.group(name='rolemenu', aliases=['rm'], hidden=True)
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @is_plugin_enabled('rolemenus')
    async def cogs_rolemenu(self, ctx):
        """Rolemenu commands"""
        if not ctx.subcommand_passed:
            commands = self.bot.get_command(name='rolemenu').commands

            embed = discord.Embed(title='%s - Rolemenu help' % ctx.guild.name, description='', color=ctx.message.author.color, colour=ctx.message.author.color)

            order = dict()
            for c in commands:
                if await c.can_run(ctx):
                    order[c.name] = c.help
            embed.add_field(name='Commands:', value='\n'.join(
                [f'**{com_name}**: {com_desc}' for com_name, com_desc in order.items()]) if len(
                order.keys()) > 0 else 'No commands found', inline=False)
            await ctx.send(embed=embed)

    @cogs_rolemenu.command(name='create', aliases=['c'], hidden=True)
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @is_plugin_enabled('rolemenus')
    async def cogs_rolemenu_create(self, ctx: commands.Context, title: str, roles: commands.Greedy[discord.Role], *emotes: typing.Union[discord.Emoji, discord.PartialEmoji, str]):
        """Create a rolemenu"""
        emotes = [x for x in emotes if x not in (' ', '')]
        if len(roles) > 10:
            return await ctx.send(f'Please limit the amount of roles/emotes to 10')

        if len(emotes) != len(roles):
            return await ctx.send(f'Expected the same amount of emotes as roles, received {len(roles)} roles and {len(emotes)} emotes')

        rolemenu = Rolemenu(guild_id=ctx.guild.id, name=title)
        rolemenu.save()

        for _ in range(len(roles)):
            role: discord.Role = roles[_]
            rme = RolemenuEmote(rolemenu_id=rolemenu.id, icon=emotes[_] if type(emotes[_]) is str else json.dumps(dict(type=emotes[_].__class__.__name__, id=emotes[_].id)), name=role.name)
            rme.save()

        await ctx.send(f'Succesfully created rolemenu {rolemenu.name} with {len(roles)} roles')

    @cogs_rolemenu.command(name='list', aliases=['l'], hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @is_plugin_enabled('rolemenus')
    async def cogs_rolemenu_list(self, ctx):
        """List the available rolemenus"""
        rolemenus = Rolemenu.get_all_by_guild(ctx.guild.id)
        embed = discord.Embed(title=f'{ctx.guild.name} - Rolemenus', description='', color=ctx.message.author.color, colour=ctx.message.author.color)
        if not rolemenus or 0 == len(rolemenus):
            embed.add_field(name='Error', value=f'No rolemenus found')
            return await ctx.send(embed=embed)
        rolemenus_list = [f'{r.id}: {r.name} ({len(r.emotes) if r.emotes else "0"})' for r in rolemenus]
        embed.add_field(name='Rolemenus:', value='\n'.join(rolemenus_list))
        await ctx.send(embed=embed)

    @cogs_rolemenu.command(name='render', aliases=['r'], hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @is_plugin_enabled('rolemenus')
    async def cogs_rolemenu_render(self, ctx, rolemenu: typing.Union[int, str]):
        """Render/display an rolemenu"""
        if type(rolemenu) is str:
            r = Rolemenu.get_by_name_and_id(name=rolemenu, guild_id=ctx.guild.id)
        else:
            r = Rolemenu.get_by_id_and_guild(menu_id=rolemenu, guild_id=ctx.guild.id)
        embed = discord.Embed(title=f'{ctx.guild.name} - Rolemenu', description='', color=ctx.message.author.color, colour=ctx.message.author.color)
        if not r:
            embed.add_field(name='Error', value=f'The specified rolemenu: "{rolemenu}" cannot be found, please check your spelling or execute: >rolemenu [list|l]')
            return await ctx.send(embed=embed)

        rendered = ''
        guild: discord.Guild = ctx.guild
        for _ in range(len(r.emotes)):
            try:
                icon = json.loads(r.emotes[_].icon)
                emoji: discord.Emoji = discord.utils.get(guild.emojis, id=icon['id'])
            except:
                emoji = r.emotes[_].icon
            rendered += f'{emoji} {r.emotes[_].name.title()}\n'
        embed.add_field(name=r.name.title(), value=rendered)
        rolemenu_message: discord.Message = await ctx.send(embed=embed)
        r.messsage_id = rolemenu_message.id
        r.save()

        for emote in r.emotes:
            try:
                icon = json.loads(emote.icon)
                emoji: discord.Emoji = discord.utils.get(guild.emojis, id=icon['id'])
            except:
                emoji = emote.icon
            await rolemenu_message.add_reaction(emoji)

    @cogs_rolemenu.command(name="delete", hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @is_plugin_enabled('rolemenus')
    async def cogs_rolemenu_delete(self, ctx: commands.Context, *rolemenus: typing.Union[int, str]):
        del_message = []
        for menu in rolemenus:
            if type(menu) == str:
                rolemenu = Rolemenu.get_by_name_and_id(name=menu, guild_id=ctx.guild.id)
            elif type(menu) == int:
                rolemenu = Rolemenu.get_by_id(rolemenu_id=menu)
                if rolemenu.guild_id != ctx.guild.id:
                    continue # skip not rolemenu of current guild
            else:
                continue # skip invalid type

            if not rolemenu:
                continue

            del_message.append(menu)
            if rolemenu.emotes:
                for rolemenu_icon in rolemenu.emotes:
                    rolemenu_icon.delete()

            rolemenu.delete()

        await ctx.send(f'Succesfully deleted {len(del_message)} rolemenus')


def setup(bot: discord.ext.commands.Bot):
    bot.add_cog(PluginCog(bot))
