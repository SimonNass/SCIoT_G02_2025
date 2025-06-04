#!/usr/bin/env python

import paho.mqtt.client as mqtt
from paho.mqtt.properties import Properties
from paho.mqtt.packettypes import PacketTypes

class MQTTEndpoint:
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
        print ("Username {} with password length {}".format(self.username,len(self.password)))
        self.connect()

    def __del__(self):
        if self.is_connected():
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()

    def __str__(self):
        return "For RebitMQ > host:{},port:{},username:{},password length:{}".format(self.host,self.port,self.username,len(self.password))

    def connect(self):
        try:
            self.mqtt_client = mqtt.Client("test_gateway_1")
            self.mqtt_client.subscribe(self.topic_prefix + '#')
            self.mqtt_client.on_message = self.recv()
            self.mqtt_client.connect(host=self.host, port=self.port, keepalive=self.timeout)
            self.mqtt_client.loop_start()
        except Exception as e:
            print ("Connection unable to establisch.")
            print (e)

    def send(self, topic: str, routing_key: str, message: str):
        if not self.is_connected():
            self.connect()
        try:
            properties = Properties(PacketTypes.PUBLISH)
            properties.MessageExpiryInterval = self.timeout
            self.mqtt_client.publish(self.topic_prefix + topic,payload=message,qos=self.qos,properties=properties)
        except Exception as e:
            print ("Connection failed.")
            print (e)
    
    def recv(self): # TODO
        try:
            pass
        except Exception as e:
            print ("Connection failed.")
            print (e)
    
    def is_connected(self): # TODO
        return (self.mqtt_client != None) and (self.mqtt_client.is_connected())

def remove_quotation(string):
    return string.replace("'","").replace('"','')
