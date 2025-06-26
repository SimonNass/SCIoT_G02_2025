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
        _, floor_id, room_id, device_uuid, _ = topic.split('/')
        new_value = int(payload)
        for a in self.actuators:
            if str(a.id) != device_uuid:
                continue
            a.write_actuator(new_value)
        

