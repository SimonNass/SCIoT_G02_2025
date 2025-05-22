#!/usr/bin/env python

import pika

class MQTTendpoint:
    def __init__(self, host, port, username, password):
        self.host = host.replace("'","").replace('"','')
        self.port = port
        self.username = username.encode('ascii','ignore').replace("'","").replace('"','')
        self.password = password
        print ("Selected host: {} and port: {}".format(self.host,self.port))
        print ("RabbitMQ username {} with password length {}".format(self.username,len(self.password)))

        try:
            credentials = pika.PlainCredentials(self.username,self.password)
            connection = pika.BlockingConnection(pika.ConnectionParameters(self.host,self.port,'/',credentials))
            self.channel = connection.channel()
            self.channel.exchange_declare(exchange='sciot.topic',exchange_type='topic',durable=True,auto_delete=False)
        except:
            print ("Connection unable to establisch.")

    #def __del__(self):
    #    pass

    def __str__(self):
        return "For RebitMQ > host:{},port:{},username:{},password length:{}".format(self.host,self.port,self.username,len(self.password))

    def send(self):
        try:
            self.channel.basic_publish(exchange='sciot.topic',routing_key='u38.0.353.window.t.12345',body='Hello World')
        except:
            print ("Connection failed.")

