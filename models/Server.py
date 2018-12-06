import json
from models.DB import DB


class Server(object):
    def __init__(self, server_id, server_name, plugins, validations, on_join, network, server_types, icon_url, member_count, status='new'):
        self.id = int(server_id)
        self.name = server_name
        self.plugins = plugins if type(plugins) is dict else json.loads(plugins)
        self.status = status
        self.validations = validations if (type(validations) is dict or validations is None) else json.loads(validations)
        self.on_join = on_join if (type(on_join) is dict or on_join is None) else json.loads(on_join)
        self.network = True if network == 1 or network == '1' else False
        self.server_types = server_types if (type(server_types) is dict or server_types is None) else json.loads(server_types)
        self.icon_url = icon_url
        self.member_count = member_count

    @classmethod
    def get_by_id(cls, server_id):
        result = DB().fetch_one('SELECT * FROM `servers` WHERE id=?', [int(server_id)])
        server_id, server_name, plugins, validations, on_join, network, server_types, icon_url, member_count = result
        return cls(server_id, server_name, plugins, validations, on_join, network, server_types, icon_url, member_count, status='existing')

    @classmethod
    def get_network_servers(cls):
        result = DB().fetch_all('SELECT * FROM `servers` WHERE network=1')
        servers = []
        for res in result:
            server_id, server_name, plugins, validations, on_join, network, server_types, icon_url, member_count = res
            servers.append(cls(server_id, server_name, plugins, validations, on_join, network, server_types, icon_url, member_count, status='existing'))
        return servers

    @classmethod
    def get_all(cls):
        results = DB().fetch_all('SELECT * FROM `servers`')
        servers = []
        for res in results:
            server_id, server_name, plugins, validations, on_join, network, server_types, icon_url, member_count = res
            servers.append(cls(server_id, server_name, plugins, validations, on_join, network, server_types, icon_url, member_count, status='existing'))
        return servers

    def save(self):
        query = 'INSERT OR REPLACE INTO servers(id, name, plugins) VALUES(?,?,?,?,?)' if self.status == 'new' else 'UPDATE servers SET name=?, plugins=?, validations=?, on_join=?, network=?, server_types=?, icon_url=?, member_count=? WHERE id=?'
        values = (self.id, self.name, json.dumps(self.plugins), self.icon_url, self.member_count) if self.status == 'new' else (self.name, json.dumps(self.plugins), json.dumps(self.validations) if self.validations else None, json.dumps(self.on_join) if self.on_join else None, self.network, json.dumps(self.server_types) if self.server_types else None, self.icon_url, self.member_count, self.id)
        return DB().execute(query, values)


if __name__ == '__main__':
    network = Server.get_network_servers()
    network_list = [n.__dict__ for n in network]
    print (json.dumps(network_list))
    pass