class Message(object):
    def __init__(self, message_type: str, message_action: str, message_command: str, message_raw_message: str, message_user_id: int, message_channel_id: int, message_server_id: int):
        self.type = message_type
        self.action = message_action
        self.command = message_command
        self.user_id = message_user_id
        self.channel_id = message_channel_id
        self.server_id = message_server_id
        self.message = message_raw_message

    def __json__(self):
        return '{"type":"%s","action":"%s","command":"%s","message": "%s","user_id":%d,"channel_id":%d,"server_id":%d}' % (self.type, self.action, self.command, self.message, self.user_id, self.channel_id, self.server_id)
