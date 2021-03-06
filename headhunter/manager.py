from pika import BlockingConnection, ConnectionParameters
import sys
import yaml
import marshal
import pickle
import os

class HunterManager(object):
  def __init__(self, amqp_server, queue_name):
    self.parameters = ConnectionParameters(amqp_server)
    self.queue_name = queue_name
    
    self.connection = BlockingConnection(self.parameters)
    self.channel = self.connection.channel()
    
    self.channel.queue_declare(self.queue_name,
      durable = True)
    
  def enqueue(self, function):
    if function.func_closure:
      closure = [x.cell_contents for x in function.func_closure]
    else:
      closure = []
    
    request = marshal.dumps(function.func_code)
    packet = pickle.dumps((closure, request))
    
    self.channel.basic_publish(
      exchange = '',
      routing_key = self.queue_name,
      body = packet
    )

if __name__ == '__main__':
  def hello_world_function():
    print("Hello, world!")
  
  sys.exit(HunterManager(**yaml.load(open('/etc/headhunter.yaml'))).
    enqueue(hello_world_function))