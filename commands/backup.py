import json
import time
from models.Command import Command


class Backup(Command):
    def __init__(self, **kwargs):
        Command.__init__(self, **kwargs)

    async def execute(self):
        if not await self.run_test():
            return

        backup_dict = dict()

        guild = self.message.guild

        for cat in guild.categories:
            changed_roles = []
            for r in cat.changed_roles:
                tmp_roles = dict()
                tmp_roles['color'] = str(r.color)
                tmp_roles['colour'] = str(r.colour)
                tmp_roles['hoist'] = r.hoist
                tmp_roles['managed'] = r.managed
                tmp_roles['mention'] = r.mention
                tmp_roles['mentionable'] = r.mentionable
                tmp_roles['permissions'] = dict(r.permissions)
                tmp_roles['position'] = r.position

                changed_roles.append(tmp_roles)
            channels = []
            for c in cat.channels:
                tmp_channel_changed_roles = []
                for r in c.changed_roles:
                    tmp_roles = dict()
                    tmp_roles['color'] = str(r.color)
                    tmp_roles['colour'] = str(r.colour)
                    tmp_roles['hoist'] = r.hoist
                    tmp_roles['managed'] = r.managed
                    tmp_roles['mention'] = r.mention
                    tmp_roles['mentionable'] = r.mentionable
                    tmp_roles['permissions'] = dict(r.permissions)
                    tmp_roles['position'] = r.position

                    tmp_channel_changed_roles.append(tmp_roles)

                overwrites = []
                for overwrite in c.overwrites:
                    role, permissions = overwrite
                    overwrites.append(dict(role=role.name,permissionOverwrite=permissions._values))

                tmp_channel = dict(
                    changed_roles=tmp_channel_changed_roles,
                    mention=c.mention,
                    name=c.name,
                    nsfw=c.nsfw if hasattr(c, 'nsfw') else None,
                    overwrites=overwrites,
                    position=c.position,
                    slowmode_delay=c.slowmode_delay if hasattr(c, 'slowmode_delay') else None,
                    topic=c.topic if hasattr(c, 'topic') else None,
                    bitrate=c.bitrate if hasattr(c, 'bitrate') else None,
                    user_limit=c.user_limit if hasattr(c, 'user_limit') else None
                )
                channels.append(tmp_channel)

            overwrites = []
            for overwrite in cat.overwrites:
                role, permissions = overwrite
                overwrites.append(dict(role=role.name, permissionOverwrite=permissions._values))

            backup_dict[cat.name] = dict(
                channels=channels,
                changed_roles=changed_roles,
                mention=cat.mention,
                name=cat.name,
                nsfw=cat.nsfw,
                overwrites=overwrites,
                position=cat.position
            )

        # channels = sorted(backup_dict, key=lambda c: c.position)

        backup_json = json.dumps(backup_dict)

        timestamp = time.time()

        with open('backups/{timestamp}.json'.format(timestamp=timestamp), 'w+') as fp:
            fp.write(backup_json)

        return await self.message.channel.send('Succesfully created backup by name: {timestamp}.'.format(timestamp=timestamp))
