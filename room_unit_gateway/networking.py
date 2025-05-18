#!/usr/bin/env python

import pika

class MQTTendpoint:
    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host #ip
        self.port = port
        self.username = username
        self.password = password
        print ("Selected host: {} and port: {}".format(self.host,self.port))
        print ("RabbitMQ username {} with password length {}".format(self.username,len(self.password)))

        credentials = pika.PlainCredentials(self.username,self.password)
        connection = pika.BlockingConnection(pika.ConnectionParameters(self.host,self.port,'/',credentials))
        self.channel = connection.channel()
        self.channel.exchange_declare(exchange='sciot.topic',exchange_type='topic',durable=True,auto_delete=False)

    #def __del__(self):
    #    pass

    def __str__(self):
        return f"For RebitMQ > host:{self.host},port:{self.port},username:{self.username},password length:{len(self.password)}"
    
    def send(self):
        self.channel.basic_publish(exchange='sciot.topic',routing_key='u38.0.353.window.t.12345',body='Hello World')
        