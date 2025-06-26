#!/usr/bin/env python

import paho.mqtt.client as mqtt
from paho.mqtt.properties import Properties
from paho.mqtt.packettypes import PacketTypes
import logging
logger = logging.getLogger(__name__)

from networking.networking_reciever import GatewayNetworkReciever

class MQTTEndpoint:
    def __init__(self, gateway: GatewayNetworkReciever, host: str, port: int, username: str, password: str, topic_prefix: str):
        self.gateway = gateway
        self.host = remove_quotation(host)
        self.port = port
        self.username = remove_quotation(username)
        self.password = password
        self.topic_prefix = topic_prefix # eg. str("iot/1/101/")
        self.mqtt_client = None
        self.timeout = 600
        self.qos = 2
        print ("Selected host: {} and port: {}".format(self.host,self.port))
        print ("Username {} with password length {}".format(self.username,len(self.password)))
        logger.info("Selected host: {} and port: {}".format(self.host,self.port))
        logger.info("Username {} with password length {}".format(self.username,len(self.password)))
        self.connect()

    def __del__(self):
        if self.is_connected():
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            logging.info("MQTT client stopped")

    def __str__(self):
        return "For RebitMQ > host:{},port:{},username:{},password length:{}".format(self.host,self.port,self.username,len(self.password))

    def connect(self):
        try:
            self.mqtt_client = mqtt.Client()

            self.mqtt_client.subscribe(self.topic_prefix + '#')
            self.mqtt_client.on_message = self.recv
            self.mqtt_client.connect(host=self.host, port=self.port, keepalive=self.timeout)
            self.mqtt_client.loop_start()
            logging.info(f"MQTT client started and connecting to {self.host}:{self.port}")
        except Exception as e:
            print ("MQTT Connection unable to establisch.")
            #print (e)
            logger.info("MQTT Connection unable to establisch. {}".format(e))

    def send(self, topic: str, message: str):
        if not self.is_connected():
            self.connect()
        try:
            properties = Properties(PacketTypes.PUBLISH)
            properties.MessageExpiryInterval = self.timeout
            self.mqtt_client.publish(self.topic_prefix + topic,payload=message,qos=self.qos,properties=properties)
        except Exception as e:
            print ("Connection failed.")
            #print (e)
            logger.info("Connection failed {}".format(e))
    
    def recv(self, client, userdata, msg): # TODO
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            logging.info(f"Message received on topic {topic} > Payload: {payload}")
            self.gateway.recv_messages(topic=topic, payload=payload)
        except Exception as e:
            print ("Answer failed.")
            #print (e)
            logger.info("Answer failed {}".format(e))
    
    def is_connected(self): # TODO
        return (self.mqtt_client != None) and (self.mqtt_client.is_connected())

def remove_quotation(string):
    return string.replace("'","").replace('"','')
