#!/usr/bin/env python

from typing import List
import json
import logging
logger = logging.getLogger(__name__)

from actuators.actuator import ActuatorInterface

class GatewayNetworkReciever:
    def __init__(self, actuators: List[ActuatorInterface]):
        self.actuators = actuators

    def find_actuator(self, device_uuid):
        try:
            #select the actuator based on uuid
            specified_actuator = self.actuators[0]
            for a in self.actuators:
                if str(a.id) != device_uuid:
                    continue
                specified_actuator = a
            return specified_actuator
        except Exception as e:
            logger.error(f"Can not find actuator with uuid {device_uuid} {e}")

    def recv_messages(self, topic, payload):
        try:
            # hotel_prefix, floor_id, room_id, iot_type, device_uuid, comand = topic.split('/')
            _, _, _, iot_type, device_uuid, _ = topic.split('/')
            
            payload_json = json.loads(payload)
            new_value = float(payload_json["new_value"])

            # malke sure the message has an actuator uuid
            if iot_type != 'actuator':
                logger.error(f"iot_type {iot_type} Answer failed {device_uuid}")
                return
            
            #select the actuator based on uuid
            specified_actuator = self.find_actuator(device_uuid)

            # write new value
            specified_actuator.write_actuator(new_value)
        except Exception as e:
            print ("Answer failed.")
            #print (e)
            logger.error(f"Answer failed {e}")

