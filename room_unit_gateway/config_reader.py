#!/usr/bin/env python

import configparser
import json
import uuid

from sensor import Sensor
from actuator import Actuator
from display import Display
from enumdef import Connectortype

def read_config(config_file_name):
    config = configparser.ConfigParser()
    config.read(config_file_name)
    #config.read('config.ini')

    # General
    version = config.get('General', 'version', fallback=0)
    if version == 1:
        print ("Error wrong config version")

    # MQTT
    mqtt_name = config.get('MQTT', 'name', fallback='MQTT')
    mqtt_host = config.get('MQTT', 'host', fallback='0.0.0.0')
    mqtt_port = config.getint('MQTT', 'port', fallback=1234)
    mqtt_username = config.get('MQTT', 'username', fallback='root')
    floor_id = config.get('Architecture', 'floor_ID', fallback=0)
    max_rooms_per_floor = config.get('MQArchitectureTT', 'max_rooms_per_floor', fallback=100)
    room_id = config.get('Architecture', 'room_ID', fallback=0)

    print ("reading in sensors")
    # Sensors
    sensor_init_list = json.loads(config.get('Sensors','sensor_list', fallback="[]"))
    sensor_class_list = []
    for sensor in sensor_init_list:
        sensor_id = uuid.uuid1() #int(sensor['id'])
        sensor_name = str(sensor['name'])
        sensor_type = str(sensor['sensore_type'])
        sensor_i2c = int(sensor['i2c'])
        sensor_i2ctype = getattr(Connectortype, str(sensor['i2c_type']))
        sensor_interval = int(sensor['read_interval'])
        try:
            sensor_class = Sensor(id=sensor_id,name=sensor_name,sensore_type=sensor_type,i2c=sensor_i2c,i2c_type=sensor_i2ctype,read_interval=sensor_interval)
            sensor_class_list.append(sensor_class)
        except Exception as e:
            print (e, flush=True)

    print ("reading in actuators")
    # Actuators
    actuator_list = json.loads(config.get('Actuators','actuator_list', fallback="[]"))
    actuator_class_list = []
    for actuator in actuator_list:
        actuator_id = uuid.uuid1() #int(actuator['id'])
        actuator_name = str(actuator['name'])
        actuator_type = str(actuator['actuator_type'])
        actuator_i2c = int(actuator['i2c'])
        actuator_i2ctype = getattr(Connectortype, str(actuator['i2c_type']))
        actuator_initial_value = int(actuator['initial_value'])
        actuator_min = int(actuator['min'])
        actuator_max = int(actuator['max'])
        try:
            actuator_class = Actuator(id=actuator_id,name=actuator_name,actuator_type=actuator_type,i2c=actuator_i2c,i2c_type=actuator_i2ctype,initial_value=actuator_initial_value,min_value=actuator_min,max_value=actuator_max)
            actuator_class_list.append(actuator_class)
        except Exception as e:
            print (e, flush=True)

    print ("reading in display")
    # Displays
    display_list = json.loads(config.get('Displays','display_list', fallback="[]"))
    display_class_list = []
    for display in display_list:
        display_id = int(display['id'])
        display_name = str(display['name'])
        display_type = str(display['display_type'])
        display_i2c = int(display['i2c'])
        display_i2ctype = getattr(Connectortype, str(display['i2c_type']))
        display_initial_value = str(display['initial_value'])
        try:
            display_class = Display(id=display_id,name=display_name,display_type=display_type,i2c=display_i2c,i2c_type=display_i2ctype,initial_value=display_initial_value)
            display_class_list.append(display_class)
        except Exception as e:
            print (e, flush=True)

    # returnobject
    config_values = {
        'mqtt_name': mqtt_name,
        'mqtt_host': mqtt_host,
        'mqtt_port': mqtt_port,
        'mqtt_username': mqtt_username,
        'floor_id': floor_id,
        'max_rooms_per_floor': max_rooms_per_floor,
        'room_id': room_id,
        'sensor_class_list': sensor_class_list,
        'actuator_class_list': actuator_class_list,
        'display_class_list': display_class_list,
    }

    return config_values
