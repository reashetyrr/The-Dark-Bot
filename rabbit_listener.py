import models.aconsumer
import socket
from config import rabbitmq_settings, tdb_process
from models.Message import Message


process_listener = None


def receive(body):
    global process_listener
    msg = body.decode("utf-8")
    # try:
    Message.parse_json(msg)
    process_listener.sendall(body)
    print('send message to client for handling')
    # except:
    #     print('Invalid json found: %s' % msg)


class RabbitMQListener(object):
    def __init__(self):
        self.consumer = consumer = models.aconsumer.Consumer(u'amqp://{username}:{password}@{host}/tdb'.format(username=rabbitmq_settings['username'], password=rabbitmq_settings['password'], host=rabbitmq_settings['host']))
        on_message_callback = lambda channel, basic_deliver, properties, body: receive(body)

        consumer.set_message_count_limit(0)
        consumer.set_queue('response_queue')
        consumer.add_on_message_callback(on_message_callback)

        print('Now listening to response_queue')
        consumer.run()


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addr_info = (tdb_process['host'], 9998)
    print('Starting socket on %s:%d' % addr_info)
    sock.bind(addr_info)
    sock.listen(1)
    print('Waiting for client to connect.')
    process_listener, client_addr = sock.accept()
    print('Client connected from: %s:%d' % client_addr)
    RabbitMQListener()
