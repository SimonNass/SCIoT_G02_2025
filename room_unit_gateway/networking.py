#!/usr/bin/env python

import pika

class MQTTendpoint:
    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = remove_quotation(host)
        self.port = port
        self.username = remove_quotation(username)
        self.password = password
        print ("Selected host: {} and port: {}".format(self.host,self.port))
        print ("RabbitMQ username {} with password length {}".format(self.username,len(self.password)))

        try:
            credentials = pika.PlainCredentials(self.username,self.password)
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.host,self.port,'/',credentials))
            self.channel = self.connection.channel()
            self.channel.exchange_declare(exchange='sciot.topic',exchange_type='topic',durable=True,auto_delete=False)
        except:
            print ("Connection unable to establisch.")

    def __del__(self):
        self.connection.close()
        pass

    def __str__(self):
        return "For RebitMQ > host:{},port:{},username:{},password length:{}".format(self.host,self.port,self.username,len(self.password))

    def send(self, topiy: str, routing_key: str, message: str):
        try:
            self.channel.basic_publish(exchange=topiy,routing_key=routing_key,body=message)
        except:
            print ("Connection failed.")

    def recv(self, topiy: str): # TODO
        try:
            for method_frame, properties, body in self.channel.consume(topiy):
                print (method_frame, properties, body)
                self.channel.basic_ack(method_frame.delivery_tag)
                if method_frame.delivery_tag == 10:
                    break
            _ = self.channel.cancel()
        except:
            print ("Connection failed.")

def remove_quotation(string):
    return string.replace("'","").replace('"','')
