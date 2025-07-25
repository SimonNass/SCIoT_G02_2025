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
    def __init__(self, host: str, port: int, username: str, password: str, timeout: int, base_topic: str, room_info: Room_Info, sensors: List[SensorInterface], actuators: List[ActuatorInterface]):
        topic_prefix = f"{base_topic}/" + str(room_info.floor_id) + "/" + str(room_info.room_extended_id) + "/"
        self.gateway_network_reciever = GatewayNetworkReciever(sensors, actuators)
        self.publisher = MQTTEndpoint(gateway=self.gateway_network_reciever, host=host,port=port,username=username,password=password,timeout=timeout,topic_prefix=topic_prefix)

    def send_all_data_sensor(self, sensor: SensorInterface, read_value: bool):
        read_dict = {}
        if read_value:
            read_dict = sensor.read_sensor()
        else:
            read_dict = sensor.__dict__()
        topic = f'sensor/{str(sensor.general_iot_device.id)}/all'
        text = json.dumps(read_dict, ensure_ascii=False).encode('utf8')
        #print(text)
        try:
            self.publisher.send(topic,text)
        except Exception as e:
            logger.warning(f"send_all_data_sensor failed {str(sensor.general_iot_device.id)} {sensor.general_iot_device.name} {e}")

    def send_all_data_actuator(self, actuator: ActuatorInterface):
        topic = f'actuator/{str(actuator.general_iot_device.id)}/all'
        text = json.dumps(actuator.__dict__(), ensure_ascii=False).encode('utf8')
        #print(text)
        try:
            self.publisher.send(topic,text)
        except Exception as e:
            logger.warning(f"send_all_data_actuator failed {str(actuator.general_iot_device.id)} {actuator.general_iot_device.name} {e}")

    def send_actuator_sensor_mapping(self, mapping: List[Dict[str,str]]):
        topic = 'mapping/all'
        text = json.dumps(mapping, ensure_ascii=False).encode('utf8')
        #print(text)
        try:
            self.publisher.send(topic,text)
        except Exception as e:
            logger.warning(f"send_actuator_sensor_mapping failed {e}")

    def send_delete_ald_IoT(self):
        topic = 'delete/all'
        text = json.dumps("", ensure_ascii=False).encode('utf8')
        #print(text)
        try:
            self.publisher.send(topic,text)
        except Exception as e:
            logger.warning(f"send_delete_ald_IoT failed {e}")
