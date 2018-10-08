import json


class Message(object):
    def __init__(self, message_type: str, message_action: str, message_command: str, message_parameters: str, message_raw_message: str, message_user_id: int, message_channel_id: int, message_server_id: int):
        self.type = message_type
        self.action = None if message_action == "'None'" else message_action
        self.command = message_command
        self.user_id = message_user_id
        self.channel_id = message_channel_id
        self.server_id = message_server_id
        self.message = message_raw_message
        self.parameters = None if message_parameters == "'None'" else message_parameters

    def __json__(self):
        return '{"type":"%s","action":"%s","command":"%s", "parameters": "%s", "message": "%s","user_id":%d,"channel_id":%d,"server_id":%d}' % (self.type, self.action, self.command, self.parameters, self.message, self.user_id, self.channel_id, self.server_id)

    @classmethod
    def parse_json(cls, json_content: str):
        required = ['type', 'command', 'message', 'user_id', 'channel_id', 'server_id']
        obj: dict = json.loads(json_content)
        for r in required:
            assert obj[r], 'Missing required parameter: %r' % r
        #  did basic check
        #  building the object automagically
        items = dict()
        for key, value in obj.items():
            prefix = ''
            if key == 'message':
                prefix = 'raw_'
            items['message_%s%s' % (prefix, key)] = value
        return cls(**items)
