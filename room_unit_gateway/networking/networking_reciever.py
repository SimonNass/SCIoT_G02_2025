#!/usr/bin/env python
"""Module specifies the incoming gateway communication in a domain specific way."""

from typing import List
import json
import logging
from actuators.actuator import ActuatorInterface
from sensors.sensor import SensorInterface
logger = logging.getLogger(__name__)

class GatewayNetworkReciever:
    def __init__(self, sensors: List[SensorInterface], actuators: List[ActuatorInterface]):
        self.sensors = []
        self.sensors = sensors
        self.actuators = actuators

    def find_sensor(self, device_uuid):
        try:
            #select the actuator based on uuid
            specified_sensor = self.sensors[0]
            for s in self.sensors:
                if str(s.general_iot_device.id) != device_uuid:
                    continue
                specified_sensor = s
            return specified_sensor
        except Exception as e:
            logger.error(f"Can not find actuator with uuid {device_uuid} {e}")
            raise e

    def find_actuator(self, device_uuid):
        try:
            #select the actuator based on uuid
            specified_actuator = self.actuators[0]
            for a in self.actuators:
                if str(a.general_iot_device.id) != device_uuid:
                    continue
                specified_actuator = a
            return specified_actuator
        except Exception as e:
            logger.error(f"Can not find actuator with uuid {device_uuid} {e}")
            raise e

    def recv_messages(self, topic: str, payload):
        try:
            # hotel_prefix, floor_id, room_id, iot_type, device_uuid, comand = topic.split('/')
            _, _, _, iot_type, device_uuid, _ = topic.split('/')

            payload_json = json.loads(payload)
            new_value = float(payload_json["new_value"])

            if iot_type == 'actuator':
                #select the actuator based on uuid
                specified_actuator = self.find_actuator(device_uuid)
                # write new value
                specified_actuator.write_actuator(new_value)
            elif iot_type == 'sensor':
                #select the sensor based on uuid
                specified_sensor = self.find_sensor(device_uuid)
                # write new value
                specified_sensor.write_sensor(new_value)
            else:
                logger.error(f"iot_type {iot_type} Answer failed {device_uuid}")
                return
        except Exception as e:
            print ("Answer failed.")
            #print (e)
            logger.error(f"Answer failed {e}")
