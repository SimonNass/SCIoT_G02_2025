#!/usr/bin/env python
"""Module specifies the gateway communication to the MQTT brocer in a domain independent way."""

import paho.mqtt.client as mqtt
from paho.mqtt.properties import Properties
from paho.mqtt.packettypes import PacketTypes

from networking.networking_reciever import GatewayNetworkReciever
import logging
logger = logging.getLogger(__name__)

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
        print (f"Selected host: {self.host} and port: {self.port}")
        print (f"Username {self.username} with password length {len(self.password)}")
        logger.info(f"Selected host: {self.host} and port: {self.port}")
        logger.info(f"Username {self.username} with password length {len(self.password)}")
        self.connect()

    def __del__(self):
        if self.is_connected():
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            logging.info("MQTT client stopped")

    def __str__(self):
        return f"For RebitMQ > host:{self.host},port:{self.port},username:{self.username},password length:{len(self.password)}"

    def connect(self):
        try:
            self.mqtt_client = mqtt.Client()

            self.mqtt_client.on_message = recv(self.gateway, self.topic_prefix)
            self.mqtt_client.connect(host=self.host, port=self.port, keepalive=self.timeout)
            self.mqtt_client.subscribe(self.topic_prefix + '#', qos=1)
            self.mqtt_client.loop_start()
            logging.info(f"MQTT client started and connecting to {self.host}:{self.port}")
        except Exception as e:
            print ("MQTT Connection unable to establisch.")
            #print (e)
            logger.error(f"MQTT Connection unable to establisch. {e}")

    def send(self, topic: str, message: str):
        if not self.is_connected():
            self.connect()
        try:
            properties = Properties(PacketTypes.PUBLISH)
            properties.MessageExpiryInterval = self.timeout
            self.mqtt_client.publish(self.topic_prefix + topic,payload=message,qos=self.qos,properties=properties)
            #print (f'Sent on topic {self.topic_prefix + topic} the message {message}')
            logger.info(f'Sent on topic {self.topic_prefix + topic} the message {message}')
        except Exception as e:
            print ("Connection failed.")
            #print (e)
            logger.error(f"Connection failed {e}")


    def is_connected(self):
        return (self.mqtt_client is not None) and (self.mqtt_client.is_connected())

def remove_quotation(string):
    return string.replace("'","").replace('"','')

def recv(gateway: GatewayNetworkReciever, topic_prefix: str):
    def on_message(client, userdata, msg):
        try:
            topic = msg.topic

            # filter out wrong topics
            if topic_prefix not in topic:
                logger.error(f"Recieved message from wrong topic prefix {topic}")
                return
            if 'GET' not in topic and 'UPDATE' not in topic:
                logger.info(f"Recieved message from wrong topic prefix {topic}")
                return

            payload = msg.payload.decode('utf-8')
            print (f'Recieved on topic {topic} the message {payload}')
            logger.info(f'Recieved on topic {topic} the message {payload}')
            gateway.recv_messages(topic=topic, payload=payload)
        except Exception as e:
            print ("General answer failed.")
            #print (e)
            logger.error(f"General answer failed {e}")
    return on_message
