#!/usr/bin/env python

import configparser

import object_factory

def read_config(config_file_name):
    config = configparser.ConfigParser()
    config.read(config_file_name)
    #config.read('config.ini')

    # General
    version = config.get('General', 'version', fallback=0)
    if version == 2:
        print ("Error wrong config version")

    # MQTT
    mqtt_name = config.get('MQTT', 'name', fallback='MQTT')
    mqtt_host = config.get('MQTT', 'host', fallback='0.0.0.0')
    mqtt_port = config.getint('MQTT', 'port', fallback=1234)
    mqtt_username = config.get('MQTT', 'username', fallback='root')
    floor_id = config.get('Architecture', 'floor_ID', fallback=0)
    max_rooms_per_floor = config.get('MQArchitectureTT', 'max_rooms_per_floor', fallback=100)
    room_id = config.get('Architecture', 'room_ID', fallback=0)

    print ("reading in sensors", flush=True)
    # Sensors
    sensor_types = object_factory.configure_sensor_types(config.get('Sensors','sensor_types', fallback="[]"))
    sensor_class_list = object_factory.configure_sensors(config.get('Sensors','sensor_list', fallback="[]"), sensor_types)

    print ("reading in actuators", flush=True)
    # Actuators
    actuator_types = object_factory.configure_actuator_types(config.get('Actuators','actuator_types', fallback="[]"))
    actuator_class_list = object_factory.configure_actuators(config.get('Actuators','actuator_list', fallback="[]"), actuator_types)

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
        'actuator_class_list': actuator_class_list
    }

    return config_values
