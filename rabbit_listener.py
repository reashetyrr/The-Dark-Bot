import models.aconsumer
from config import rabbitmq_settings
from models.Message import Message
import requests


async def receive(ch, method, body):
    msg = body.decode("utf-8")
    try:
        message = Message.parse_json(msg)
    except:
        print('Invalid json found: %s' % msg)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    requests.post('http://127.0.0.1:1337/message', json=msg)


class RabbitMQListener(object):
    def __init__(self):
        self.consumer = consumer = models.aconsumer.Consumer(u'amqp://{username}:{password}@{host}/tdb'.format(username=rabbitmq_settings['username'], password=rabbitmq_settings['password'], host=rabbitmq_settings['host']))
        on_message_callback = lambda channel, basic_deliver, properties, body: receive(channel, basic_deliver, body)

        consumer.set_message_count_limit(0)
        consumer.set_acknowledge_messages(True)
        consumer.set_queue('commands_queue')
        consumer.add_on_message_callback(on_message_callback)

        consumer.run()