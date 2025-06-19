#!/usr/bin/env python

import configparser
import logging
logger = logging.getLogger(__name__)

import object_factory

def read_config(config_file_name):
    config = configparser.ConfigParser(interpolation=None)
    config.read(config_file_name)
    #config.read('config.ini')

    print ("reading in general", flush=True)
    logger.info("reading in general")
    # General
    version = config.get('General', 'version', fallback=0)
    if version == 2:
        print ("Error wrong config version")
        logger.info("Error wrong config version")
    max_cycle_time = config.get('General', 'max_cycle_time', fallback=100)

    print ("reading in MQTT", flush=True)
    logger.info("reading in MQTT")
    # MQTT
    mqtt_name = config.get('MQTT', 'name', fallback='MQTT')
    mqtt_host = config.get('MQTT', 'host', fallback='0.0.0.0')
    mqtt_port = config.getint('MQTT', 'port', fallback=1884)
    mqtt_username = config.get('MQTT', 'username', fallback='root')
    floor_id = config.get('Architecture', 'floor_ID', fallback=0)
    max_rooms_per_floor = config.get('MQArchitectureTT', 'max_rooms_per_floor', fallback=100)
    room_id = config.get('Architecture', 'room_ID', fallback=0)

    
    print ("reading in ardoino", flush=True)
    logger.info("reading in ardoino")
    # Ardoino connection
    message_end_signal = config.get('Ardoino', 'message_end_signal', fallback='')
    usb_channel_type = config.get('Ardoino', 'usb_channel_type_default', fallback='/dev/ttyACM0')
    usb_channel_data_rate = config.get('Ardoino', 'usb_channel_data_rate', fallback=9600)
    ardoino_serial = object_factory.configure_ardoino_connection(message_end_signal=message_end_signal,usb_channel_type=usb_channel_type,usb_channel_data_rate=usb_channel_data_rate)

    print ("reading in sensors", flush=True)
    logger.info("reading in sensors")
    # Sensors
    sensor_types = object_factory.configure_sensor_types(config.get('Sensors','sensor_types', fallback="[]"))
    sensor_class_list = object_factory.configure_sensors(config.get('Sensors','sensor_list', fallback="[]"), sensor_types, ardoino_serial)

    print ("reading in actuators", flush=True)
    logger.info("reading in actuators")
    # Actuators
    actuator_types = object_factory.configure_actuator_types(config.get('Actuators','actuator_types', fallback="[]"))
    actuator_class_list = object_factory.configure_actuators(config.get('Actuators','actuator_list', fallback="[]"), actuator_types, ardoino_serial)

    print ("reading in VirtualEnfironment mapping", flush=True)
    logger.info("reading in VirtualEnfironment mapping")
    # VirtualEnfironment
    virtual_enfironment_list = object_factory.configure_environment_map(config.get('VirtualEnfironment','virtual_enfironment_list', fallback="[]"))

    # returnobject
    config_values = {
        'max_cycle_time': max_cycle_time,
        'mqtt_name': mqtt_name,
        'mqtt_host': mqtt_host,
        'mqtt_port': mqtt_port,
        'mqtt_username': mqtt_username,
        'ardoino_serial': ardoino_serial,
        'floor_id': floor_id,
        'max_rooms_per_floor': max_rooms_per_floor,
        'room_id': room_id,
        'sensor_class_list': sensor_class_list,
        'actuator_class_list': actuator_class_list,
        'virtual_enfironment_list':virtual_enfironment_list
    }

    return config_values
