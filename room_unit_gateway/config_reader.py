#!/usr/bin/env python

import configparser
import logging
logger = logging.getLogger(__name__)

import object_factory

def read_config(config_file_name, password: str):
    print (f"reading in {config_file_name}", flush=True)
    config = configparser.ConfigParser(interpolation=None)
    config.read(config_file_name, encoding='utf-8')
    #config.read('config.ini')

    #print ("reading in general", flush=True)
    logger.info("reading in general")
    # General
    version = config.get('General', 'version', fallback=0)
    if version == 2:
        print ("Error wrong config version")
        logger.warning("Error wrong config version")
    max_cycle_time = config.get('General', 'max_cycle_time', fallback=100)

    #print ("reading in MQTT", flush=True)
    logger.info("reading in MQTT")
    # MQTT
    mqtt_name = config.get('MQTT', 'name', fallback='MQTT')
    mqtt_host = config.get('MQTT', 'host', fallback='0.0.0.0')
    mqtt_port = config.getint('MQTT', 'port', fallback=1884)
    mqtt_username = config.get('MQTT', 'username', fallback='root')
    floor_id = config.get('Architecture', 'floor_ID', fallback=0)
    max_rooms_per_floor = config.get('MQArchitectureTT', 'max_rooms_per_floor', fallback=100)
    room_id = config.get('Architecture', 'room_ID', fallback=0)


    #print ("reading in ardoino", flush=True)
    logger.info("reading in ardoino")
    # Ardoino connection
    message_end_signal = config.get('Ardoino', 'message_end_signal', fallback='')
    usb_channel_type = config.get('Ardoino', 'usb_channel_type_default', fallback='/dev/ttyACM0')
    usb_channel_data_rate = config.get('Ardoino', 'usb_channel_data_rate', fallback=9600)
    ardoino_serial = object_factory.configure_ardoino_connection(message_end_signal=message_end_signal,
                                                                 usb_channel_type=usb_channel_type,
                                                                 usb_channel_data_rate=usb_channel_data_rate)

    #print ("reading in sensors", flush=True)
    logger.info("reading in sensors")
    # Sensors
    sensor_types = object_factory.configure_sensor_types(config.get('Sensors','sensor_types', fallback="[]"))
    sensor_class_list = object_factory.configure_sensors(config.get('Sensors','sensor_list', fallback="[]"), 
                                                         sensor_types, 
                                                         ardoino_serial)

    #print ("reading in actuators", flush=True)
    logger.info("reading in actuators")
    # Actuators
    actuator_types = object_factory.configure_actuator_types(config.get('Actuators','actuator_types', fallback="[]"))
    actuator_class_list = object_factory.configure_actuators(config.get('Actuators','actuator_list', fallback="[]"), 
                                                             actuator_types, 
                                                             ardoino_serial)

    #print ("reading in VirtualEnfironment mapping", flush=True)
    logger.info("reading in VirtualEnfironment mapping")
    # VirtualEnfironment
    virtual_enfironment_list = object_factory.configure_environment_map(config.get('VirtualEnfironment','virtual_enfironment_list', fallback="[]"))
    virtual_environment = object_factory.configure_environment(sensors=sensor_class_list,
                                                               actuators=actuator_class_list,
                                                               virtual_enfironment_list=virtual_enfironment_list)

    #print ("creating gateway_network", flush=True)
    logger.info("creating gateway_network")
    # GatewayNetwork
    room_info = object_factory.configure_room_inof(floor_id=floor_id,
                                                   max_rooms_per_floor=max_rooms_per_floor,
                                                   room_id=room_id)
    gateway_network = object_factory.configure_network_gateway(host=mqtt_host,
                                                               port=mqtt_port,
                                                               username=mqtt_username,
                                                               password=password,
                                                               room_info=room_info,
                                                               actuators=actuator_class_list)

    # returnobject
    config_values = {
        'max_cycle_time': max_cycle_time,
        'ardoino_serial': ardoino_serial,
        'room_info': room_info,
        'sensor_class_list': sensor_class_list,
        'actuator_class_list': actuator_class_list,
        'virtual_environment':virtual_environment,
        'gateway_network':gateway_network
    }

    return config_values
