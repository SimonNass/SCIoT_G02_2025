#!/usr/bin/env python
"""Module specifies the outgoing gateway communication in a domain specific way."""

from typing import List, Dict
import json
import logging
from networking.networking_paho import MQTTEndpoint
from networking.networking_reciever import GatewayNetworkReciever
from sensors.sensor import SensorInterface
from actuators.actuator import ActuatorInterface
from room_info import Room_Info
logger = logging.getLogger(__name__)

class GatewayNetwork:
    def __init__(self, host: str, port: int, username: str, password: str, room_info: Room_Info, actuators: List[ActuatorInterface]):
        topic_prefix = "SCIoT_G02_2025/" + str(room_info.floor_id) + "/" + str(room_info.room_extended_id) + "/"
        self.gateway_network_reciever = GatewayNetworkReciever(actuators)
        self.publisher = MQTTEndpoint(gateway=self.gateway_network_reciever, host=host,port=port,username=username,password=password,topic_prefix=topic_prefix)

    def send_all_data_sensor(self, sensor: SensorInterface, read_value: bool):
        read_dict = {}
        if read_value:
            read_dict = sensor.read_sensor()
        else:
            read_dict = sensor.__dict__()
        topic = f'sensor/{str(sensor.id)}/all'
        text = json.dumps(read_dict, ensure_ascii=False).encode('utf8')
        #print(text)
        #self.publisher.send(topic,text)

    def send_all_data_actuator(self, actuator: ActuatorInterface):
        topic = f'actuator/{str(actuator.id)}/all'
        text = json.dumps(actuator.__dict__(), ensure_ascii=False).encode('utf8')
        #print(text)
        #self.publisher.send(topic,text)

    def send_actuator_sensor_mapping(self, mapping: List[Dict[str,str]]):
        topic = 'mapping/all'
        text = json.dumps(mapping, ensure_ascii=False).encode('utf8')
        print(text)
        #self.publisher.send(topic,text)
