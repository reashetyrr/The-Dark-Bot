import pika
from config import rabbitmq_settings
from models.Message import Message


class RabbitMQHandler(object):
    def __init__(self):
        self.queue = pika.BlockingConnection(pika.ConnectionParameters(
            host=rabbitmq_settings['host'],
            virtual_host=rabbitmq_settings['virtualhost'],
            credentials=pika.credentials.PlainCredentials(username=rabbitmq_settings['username'],
                                                          password=rabbitmq_settings['password'])
        ))
        self.channel = self.queue.channel()
        self.channel.queue_declare(queue='commands_queue', durable=True)

    def send(self, message: Message):
        self.channel.basic_publish(exchange='', routing_key='commands_queue', body=message.__json__(), properties=pika.BasicProperties(delivery_mode=2))


if __name__ == '__main__':
    message_object = Message(message_action='display', message_command='tdb!test', message_user_id=0, message_channel_id=0, message_server_id=0, message_type='test')
    RabbitMQHandler().send(message=message_object)
