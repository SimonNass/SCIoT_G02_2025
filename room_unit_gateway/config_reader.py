#!/usr/bin/env python

import configparser
import json

from sensor import Sensor
from actuator import Actuator
from display import Display

def read_config(config_file_name: str):
    config = configparser.ConfigParser()
    config.read(config_file_name)
    #config.read('config.ini')

    # General
    version = config.get('General', 'version')
    if version == 1:
        print ("Error wrong config version")
    
    # RabitMQ
    rabitMQ_name = config.get('RabitMQ', 'name')
    rabitMQ_host = config.get('RabitMQ', 'host')
    rabitMQ_port = config.get('RabitMQ', 'port')
    rabitMQ_username = config.get('RabitMQ', 'username')

    # Sensors
    sensor_init_list = json.loads(config.get('Sensors','sensor_list'))
    sensor_class_list = []
    for sensor in sensor_init_list:
        sensor_class = Sensor(id=sensor[0],name=sensor[1],sensore_type=sensor[2],i2c=sensor[3],i2c_type=sensor[4],read_interval=sensor[5])
        sensor_class_list.append(sensor_class)
    
    # Actuators
    actuator_list = json.loads(config.get('Sensors','actuator_list'))
    actuator_class_list = []
    for actuator in actuator_list:
        actuator_class = Actuator(id=actuator[0],name=actuator[1],actuator_type=actuator[2],i2c=actuator[3],i2c_type=actuator[4],initial_value=actuator[5],min=actuator[6],max=actuator[7])
        actuator_class_list.append(actuator_class)
    
    # Displays
    display_list = json.loads(config.get('Sensors','display_list'))
    display_class_list = []
    for display in display_list:
        display_class = Display(id=display[0],name=display[1],display_type=display[2],i2c=display[3],i2c_type=display[4],initial_value=display[5])
        display_class_list.append(display_class)

    config_values = {
        'rabitMQ_name': rabitMQ_name,
        'rabitMQ_host': rabitMQ_host,
        'rabitMQ_port': rabitMQ_port,
        'rabitMQ_username': rabitMQ_username,
        'sensor_list': sensor_init_list,
        'sensor_class_list': sensor_class_list,
        'actuator_list': actuator_list,
        'actuator_class_list': actuator_class_list,
        'display_list': display_list,
        'display_class_list': display_class_list,
    }

    return config_values