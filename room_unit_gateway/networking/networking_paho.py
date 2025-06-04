#!/usr/bin/env python

from paho.mqtt.client import mqtt
from paho.mqtt.properties import Properties
from paho.mqtt.packettypes import PacketTypes

class MQTTPublishEndpoint:
    def __init__(self, host: str, port: int, username: str, password: str, topic_prefix: str):
        self.host = remove_quotation(host)
        self.port = port
        self.username = remove_quotation(username)
        self.password = password
        self.topic_prefix = topic_prefix # eg. str("iot/1/101/")
        self.mqtt_client = None
        self.timeout = 60
        self.qos = 2
        print ("Selected host: {} and port: {}".format(self.host,self.port))
        print ("RabbitMQ username {} with password length {}".format(self.username,len(self.password)))
        self.connect()

    def __del__(self):
        if self.is_connected():
            self.mqtt_client.close()

    def __str__(self):
        return "For RebitMQ > host:{},port:{},username:{},password length:{}".format(self.host,self.port,self.username,len(self.password))

    def connect(self):
        try:
            self.mqtt_client = mqtt.Client("test_gateway_1")
            self.mqtt_client.subscribe(self.topic_prefix + '#')
            self.mqtt_client.connect(host=self.host, port=self.port, timeout=self.timeout)
            self.mqtt_client.loop_start()
        except Exception as e:
            print ("Connection unable to establisch.")
            print (e)

    def send(self, topiy: str, routing_key: str, message: str):
        if not self.is_connected():
            self.connect()
        try:
            properties = Properties(PacketTypes.PUBLISH)
            properties.MessageExpiryInterval = self.timeout
            self.mqtt_client.publish(exchange=self.topic_prefix + topiy,body=message,qos=self.qos,properties=properties)
        except Exception as e:
            print ("Connection failed.")
            print (e)
    
    def recv(self): # TODO
        if not self.is_connected():
            self.connect()
        try:
            for method_frame, properties, body in self.channel.consume(self.topic_prefix + "*"):
                print (method_frame, properties, body)
                #send to main loop here TODO
                self.channel.basic_ack(method_frame.delivery_tag)
                if method_frame.delivery_tag == 10:
                    break
            _ = self.channel.cancel()
        except Exception as e:
            print ("Connection failed.")
            print (e)
    
    def is_connected(self): # TODO
        return self.connection != None

def remove_quotation(string):
    return string.replace("'","").replace('"','')
