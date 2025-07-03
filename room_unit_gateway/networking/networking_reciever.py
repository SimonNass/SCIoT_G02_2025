#!/usr/bin/env python

from typing import List
import json
import logging
logger = logging.getLogger(__name__)

from actuators.actuator import ActuatorInterface

class GatewayNetworkReciever:
    def __init__(self, actuators: List[ActuatorInterface]):
        self.actuators = actuators

    def recv_messages(self, topic, payload):
        try:
            hotel_prefix, floor_id, room_id, iot_type, device_uuid, comand = topic.split('/')
            
            payload_json = json.loads(payload)
            new_value = float(payload_json["new_value"])

            # malke sure the message has an actuator uuid
            if iot_type != 'actuator':
                logger.error(f"iot_type {iot_type} Answer failed {e}")
                return
            
            #select the actuator based on uuid
            specified_actuator = self.actuators[0]
            for a in self.actuators:
                if str(a.id) != device_uuid:
                    continue
                specified_actuator = a

            # write new value
            specified_actuator.write_actuator(new_value)
        except Exception as e:
            print ("Answer failed.")
            #print (e)
            logger.error("Answer failed {}".format(e))

