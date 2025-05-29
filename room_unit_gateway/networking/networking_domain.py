#!/usr/bin/env python

import json

from networking.networking import MQTTPublishEndpoint, MQTTSubscribeEndpoint
from sensors.sensor import SensorInterface
from actuators.actuator import Actuator
from actuators.display import Display

class GatewayNetwork:
    def __init__(self, host: str, port: int, username: str, password: str, floor_id: int, max_rooms_per_floor: int, room_id: int):
        topic_prefix = "iot/" + str(floor_id) + "/" + str(floor_id * max_rooms_per_floor + room_id) + "/"
        self.publisher = MQTTPublishEndpoint(host=host,port=port,username=username,password=password,topic_prefix=topic_prefix)
        self.subscriber = MQTTSubscribeEndpoint(host=host,port=port,username=username,password=password,topic_prefix=topic_prefix)

    def send_all_sensor(self, sensor: SensorInterface, read_value: bool):
        if read_value:
            sensor.read_sensor()
        topic = '{}/all'.format(str(sensor.id))
        text = json.dumps(sensor.__dict__())
        #print (topic)
        #print (text)
        self.publisher.send(topic,'u38.0.353.window.t.12345',text)

    def send_all_actuator(self, actuator: Actuator):
        topic = '{}/all'.format(str(actuator.id))
        text = json.dumps(actuator.__dict__())
        #print (topic)
        #print (text)
        self.publisher.send(topic,'u38.0.353.window.t.12345',text)

    def check_vor_messages(self):
        self.subscriber.recv()

