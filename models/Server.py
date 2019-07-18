import json
from models.DB import DB


class Server(object):
    def __init__(self, server_id, server_name, plugins, validations, on_join, network, server_types, icon_url, member_count, blacklisted, currency_name=None, custom_settings=None, bot_settings=None, status='new'):
        if custom_settings == '' or custom_settings is None:
            custom_settings = dict()
        if plugins == '' or plugins is None:
            plugins = []
        if server_types == '' or server_types is None:
            server_types = dict()
        if validations == '' or validations is None:
            validations = dict()
        if on_join == '' or on_join is None:
            on_join = dict()
        self.id = int(server_id)
        self.name = server_name
        self.plugins = plugins if type(plugins) is list or plugins is None else json.loads(plugins)
        self.status = status
        self.validations = validations if (type(validations) is dict or validations is None) else json.loads(validations)
        self.on_join = on_join if (type(on_join) is dict or on_join is None) else json.loads(on_join)
        self.network = True if network == 1 or network == '1' else False
        self.server_types = server_types if (type(server_types) is dict or server_types is None) else json.loads(server_types)
        self.icon_url = icon_url
        self.member_count = member_count
        self.blacklisted = blacklisted == 1
        self.currency_name = currency_name
        self.custom_settings = custom_settings if (type(custom_settings) is dict) else json.loads(custom_settings)
        self.bot_settings = json.loads(bot_settings) if bot_settings else dict(administrators=[], moderators=[])

    @classmethod
    def get_by_id(cls, server_id):
        result = DB().fetch_one('SELECT * FROM servers WHERE id=%s', [int(server_id)])
        return cls(*result, status='existing') if result else None

    @classmethod
    def get_network_servers(cls):
        result = DB().fetch_all('SELECT * FROM servers WHERE network=1')
        return [cls(*server, status='existing') for server in result] if result else None

    @classmethod
    def get_all(cls):
        results = DB().fetch_all('SELECT * FROM servers')
        return [cls(*server, status='existing') for server in results] if results else None

    @classmethod
    def get_non_blacklisted(cls):
        results = DB().fetch_all('SELECT * FROM servers WHERE blacklisted=0')
        return [cls(*server, status='existing') for server in results] if results else None

    def save(self):
        query = 'REPLACE INTO servers(id,name,plugins,validations,on_join,network,server_types,icon_url,member_count,blacklisted,currency_name,custom_settings,bot_settings) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)' if self.status == 'new' else 'UPDATE servers SET name=%s, plugins=%s, validations=%s, on_join=%s, network=%s, server_types=%s, icon_url=%s, member_count=%s, currency_name=%s, custom_settings=%s, bot_settings=%s, blacklisted=%s WHERE id=%s'
        values = [
            self.id,
            self.name,
            json.dumps(self.plugins) if self.plugins else None,
            json.dumps(self.validations) if self.validations else None,
            json.dumps(self.on_join) if self.on_join else None,
            self.network,
            json.dumps(self.server_types) if self.server_types else None,
            self.icon_url,
            self.member_count,
            self.blacklisted,
            self.currency_name,
            json.dumps(self.custom_settings) if self.custom_settings else None,
            json.dumps(self.bot_settings) if self.bot_settings else None
        ] if self.status == 'new' else [
            self.name,
            json.dumps(self.plugins) if self.plugins else None,
            json.dumps(self.validations) if self.validations else None,
            json.dumps(self.on_join) if self.on_join else None,
            self.network,
            json.dumps(self.server_types) if self.server_types else None,
            self.icon_url,
            self.member_count,
            self.currency_name,
            json.dumps(self.custom_settings) if self.custom_settings else None,
            json.dumps(self.bot_settings) if self.bot_settings else None,
            self.blacklisted,
            self.id
        ]
        return DB().execute(query, values)


if __name__ == '__main__':
    network = Server.get_network_servers()
    network_list = [n.__dict__ for n in network]
    print (json.dumps(network_list))
    pass
