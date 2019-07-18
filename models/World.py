import json
from models.DB import DB
from models.Server import Server
from models.rpg.Building import Building
from enum import IntEnum


class WorldType(IntEnum):
    SLAVEMARKET = 0
    MARKETPLACE = 1
    REGULAR = 2
    GODREALM = 3


class World:
    def __init__(self, server: Server, world_name: str, map_location: dict, authority: dict, wealth: int, world_level: int, power_level: int, world_buildings: dict, world_id: int = None, world_type: WorldType = WorldType.REGULAR):
        self.id: int = world_id
        self.server: Server = server
        self.world_name: str = world_name
        self.location: dict = map_location
        self.authority: dict = authority
        self.wealth: int = wealth
        self.world_level: int = world_level
        self.power_level: int = power_level
        self.world_buildings: dict = world_buildings
        self.world_type: WorldType = world_type

    @classmethod
    def get_by_id(cls, server_id):
        result = DB().fetch_one('SELECT * FROM `servers` WHERE id=%s', [int(server_id)])
        return cls(*result, status='existing') if result else None

    @classmethod
    def get_network_servers(cls):
        result = DB().fetch_all('SELECT * FROM `servers` WHERE network=1')
        return [cls(*server, status='existing') for server in result] if result else None

    @classmethod
    def get_all(cls):
        results = DB().fetch_all('SELECT * FROM `servers`')
        return [cls(*server, status='existing') for server in results] if results else None

    @classmethod
    def get_non_blacklisted(cls):
        results = DB().fetch_all('SELECT * FROM servers WHERE blacklisted=0')
        return [cls(*server, status='existing') for server in results] if results else None

    def save(self):
        query = 'INSERT OR REPLACE INTO servers(id, name, plugins, icon_url, member_count, blacklisted) VALUES(%s,%s,%s,%s,%s,%s)' if self.status == 'new' else 'UPDATE servers SET name=%s, plugins=%s, validations=%s, on_join=%s, network=%s, server_types=%s, icon_url=%s, member_count=%s, currency_name=%s, custom_settings=%s, bot_settings=%s, blacklisted=%s WHERE id=%s'
        values = (self.id, self.name, json.dumps(self.plugins), self.icon_url, self.member_count, self.blacklisted) if self.status == 'new' else (self.name, json.dumps(self.plugins), json.dumps(self.validations) if self.validations else None, json.dumps(self.on_join) if self.on_join else None, self.network, json.dumps(self.server_types) if self.server_types else None, self.icon_url, self.member_count, self.currency_name, json.dumps(self.custom_settings) if self.custom_settings else None, json.dumps(self.bot_settings), self.blacklisted, self.id)
        return DB().execute(query, values)


if __name__ == '__main__':
    network = Server.get_network_servers()
    network_list = [n.__dict__ for n in network]
    print (json.dumps(network_list))
    pass
