#!/usr/bin/env python

import configparser
import json

from sensor import Sensor
from actuator import Actuator
from display import Display
from enumdef import Connectortype

def read_config(config_file_name):
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
        sensor_id = int(sensor['id'])
        sensor_name = sensor['name']
        sensor_type = sensor['sensore_type']
        sensor_i2c = int(sensor['i2c'])
        sensor_i2ctype = getattr(Connectortype, sensor['i2c_type'])
        sensor_interval = sensor['read_interval']
        sensor_class = Sensor(id=sensor_id,name=sensor_name,sensore_type=sensor_type,i2c=sensor_i2c,i2c_type=sensor_i2ctype,read_interval=sensor_interval)
        sensor_class_list.append(sensor_class)

    # Actuators
    actuator_list = json.loads(config.get('Actuators','actuator_list'))
    actuator_class_list = []
    for actuator in actuator_list:
        actuator_class = Actuator(id=int(actuator['id']),name=actuator['name'],actuator_type=actuator['actuator_type'],i2c=int(actuator['i2c']),i2c_type=getattr(Connectortype, actuator['i2c_type']),initial_value=actuator['initial_value'],min=actuator['min'],max=actuator['max'])
        actuator_class_list.append(actuator_class)

    # Displays
    display_list = json.loads(config.get('Displays','display_list'))
    display_class_list = []
    for display in display_list:
        display_class = Display(id=int(display['id']),name=display['name'],display_type=display['display_type'],i2c=int(display['i2c']),i2c_type=getattr(Connectortype, display['i2c_type']),initial_value=display['initial_value'])
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
