#!/usr/bin/env python

from typing import List
import json
import logging
logger = logging.getLogger(__name__)

from networking.networking_paho import MQTTEndpoint
from sensors.sensor import SensorInterface
from actuators.actuator import ActuatorInterface

class GatewayNetwork:
    def __init__(self, host: str, port: int, username: str, password: str, floor_id: int, max_rooms_per_floor: int, room_id: int, actuators: List[ActuatorInterface]):
        room_extended_id = int(floor_id) * int(max_rooms_per_floor) + int(room_id)
        topic_prefix = "SCIoT_G02_2025/" + str(floor_id) + "/" + str(room_extended_id) + "/"
        self.publisher = MQTTEndpoint(self, host=host,port=port,username=username,password=password,topic_prefix=topic_prefix)
        self.actuators = actuators

    def send_all_data_sensor(self, sensor: SensorInterface, read_value: bool):
        read_dict = {}
        if read_value:
            read_dict = sensor.read_sensor()
        else:
            read_dict = sensor.__dict__()
        topic = 'sensor/{}/all'.format(str(sensor.id))
        text = json.dumps(read_dict)
        #print (topic)
        #print (text)
        self.publisher.send(topic,text)

    def send_all_data_actuator(self, actuator: ActuatorInterface):
        topic = 'actuator/{}/all'.format(str(actuator.id))
        text = json.dumps(actuator.__dict__())
        #print (topic)
        #print (text)
        self.publisher.send(topic,text)

    def recv_messages(self, topic, payload):
        _, floor_id, room_id, device_uuid, _ = topic.split('/')
        new_value = int(payload)
        for a in self.actuators:
            if str(a.id) != device_uuid:
                continue
            a.write_actuator(new_value)
        

