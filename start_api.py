import cherrypy


class API:
    def __init__(self):
        cherrypy.config.update({
            'server.socket_host': '0.0.0.0',
            'server.socket_port': 999,
        })

        conf = {
            '/': {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                "tools.encode.on": True,
                'tools.encode.encoding': 'utf-8',
                'tools.decode.on': True,
                'tools.decode.encoding': 'utf-8',
                'tools.sessions.timeout': 60,
                'tools.response_headers.on': True,
                'tools.response_headers.headers': [('Access-Control-Allow-Origin', '*'),
                                                   ('Access-Control-Allow-Methods', 'POST,GET,PUT,DELETE'),
                                                   ('Access-Control-Allow-Headers', 'Content-Type')]
            }
        }

        cherrypy.quickstart(Main(), '/', conf)


class Main:
    exposed = True

    def __init__(self):
        pass

    @cherrypy.tools.json_out()
    def GET(self):
        from models.Server import Server

        def compare_servers(s1: Server, s2: Server):
            matches = []
            for tag in s1.server_types:
                if tag in s2.server_types or tag == 'ALL':
                    matches.append(tag)
            return len(matches), (s1.id, s2.id)

        servers: list = Server.get_network_servers()
        nodelist = dict(
            nodes=[],
            edges=[]
        )

        for index, server in enumerate(servers):
            other_servers = [s for s in servers if s.id != server.id]  # loop through all servers inside
            for server2 in other_servers:
                matches, ids = compare_servers(server, server2)

                if matches > 0:
                    existing = False
                    for edge in nodelist['edges']:
                        if edge['s1'] in (server.id, server2.id) and edge['s2'] in (server.id, server2.id):
                            existing = True
                    if not existing:
                        nodelist['edges'].append(dict(s1=ids[0], s2=ids[1], weight=matches))
            nodelist['nodes'].append(dict(id=server.id, member_count=server.member_count, name=server.name, tags=server.server_types, image=server.icon_url))

        return nodelist


if __name__ == '__main__':
    API()
