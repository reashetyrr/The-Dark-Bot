import pika
from config import rabbitmq_settings
from models.Message import Message
from methods import send_discord_message, generate_embed


class RabbitMQHandler(object):
    def __init__(self):
        self.queue = pika.BlockingConnection(pika.ConnectionParameters(
            host=rabbitmq_settings['host'],
            virtual_host=rabbitmq_settings['virtualhost'],
            credentials=pika.credentials.PlainCredentials(username=rabbitmq_settings['username'], password=rabbitmq_settings['password'])
        ))
        self.channel = self.queue.channel()
        self.channel.queue_declare(queue='commands_queue', durable=True)
        self.channel.queue_declare(queue='response_queue', durable=True)
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(receive, queue='response_queue')
        self.channel.start_consuming()

    def send(self, message: Message):
        self.channel.basic_publish(exchange='', routing_key='commands_queue', body=message.__json__(), properties=pika.BasicProperties(delivery_mode=2))


async def receive(ch, method, properties, body):
    msg = body.decode("utf-8")
    message = None
    try:
        message = Message.parse_json(msg)
    except:
        print('Invalid json found: %s' % msg)
    ch.basic_ack(delivery_tag=method.delivery_tag)

    print(msg)
    if message.get('type') == 'embed':
        msg = generate_embed(message)
    elif message.get('type') not in ('embed', 'plain'):
        return
    else:
        msg = message.message
    await send_discord_message(msg, message.channel_id, message.guild_id, message.type == 'embed')


if __name__ == '__main__':
    message_object = Message(message_action='display', message_command='tdb!test', message_user_id=0,
                             message_channel_id=0, message_server_id=0, message_type='test')
    RabbitMQHandler().send(message=message_object)