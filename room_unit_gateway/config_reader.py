#!/usr/bin/env python
"""Module reads in the configuration file."""

import configparser
import logging
import object_factory
logger = logging.getLogger(__name__)


def read_general_config(config):
    try:
        #print ("reading in general", flush=True)
        logger.info("reading in general")
        # General
        version = config.get('General', 'version', fallback=0)
        if version == 2:
            print ("Error wrong config version")
            logger.warning("Error wrong config version")
        max_cycle_time = config.get('General', 'max_cycle_time', fallback=100)
        sleeping_time = config.get('General', 'sleeping_time', fallback=1)
        return max_cycle_time, sleeping_time
    except Exception as e:
        logger.error(f"Reading config file was not succesfully in the General section {e}")
        return 100

def read_mqtt_config(config):
    try:
        #print ("reading in MQTT", flush=True)
        logger.info("reading in MQTT")
        mqtt_name = config.get('MQTT', 'name', fallback='MQTT')
        mqtt_host = config.get('MQTT', 'host', fallback='0.0.0.0')
        mqtt_port = config.getint('MQTT', 'port', fallback=1884)
        mqtt_username = config.get('MQTT', 'username', fallback='root')
        mqtt_base_topic = config.get('MQTT', 'base_topic', fallback='SCIoT_G02_2025')
        mqtt_timeout = config.get('MQTT', 'timeout', fallback=600)
        return mqtt_name, mqtt_host, mqtt_port, mqtt_username, mqtt_base_topic, mqtt_timeout
    except Exception as e:
        logger.error(f"Reading config file was not succesfully in the MQTT section {e}")
        return 'MQTT', '0.0.0.0', 1884, 'root', 'SCIoT_G02_2025', 600

def read_architecture_config(config):
    try:
        #print ("reading in Architecture", flush=True)
        logger.info("reading in Architecture")
        floor_id = config.get('Architecture', 'floor_ID', fallback=0)
        max_rooms_per_floor = config.get('MQArchitectureTT', 'max_rooms_per_floor', fallback=100)
        room_id = config.get('Architecture', 'room_ID', fallback=0)
        room_info = object_factory.configure_room_info(floor_id=floor_id,
                                                    max_rooms_per_floor=max_rooms_per_floor,
                                                    room_id=room_id)
        return room_info
    except Exception as e:
        logger.error(f"Reading config file was not succesfully in the Architecture section {e}")
        return object_factory.configure_room_info(floor_id=0, max_rooms_per_floor=100, room_id=0)

def read_ardoino_config(config):
    try:
        #print ("reading in ardoino", flush=True)
        logger.info("reading in ardoino")
        # Ardoino connection
        message_end_signal = config.get('Ardoino', 'message_end_signal', fallback='')
        usb_channel_type = config.get('Ardoino', 'usb_channel_type_default', fallback='/dev/ttyACM0')
        usb_channel_data_rate = config.get('Ardoino', 'usb_channel_data_rate', fallback=9600)
        ardoino_serial = object_factory.configure_ardoino_connection(message_end_signal=message_end_signal,
                                                                    usb_channel_type=usb_channel_type,
                                                                    usb_channel_data_rate=usb_channel_data_rate)
        return ardoino_serial
    except Exception as e:
        logger.error(f"Reading config file was not succesfully in the Ardoino section {e}")
        return None

def read_sensors_config(config, ardoino_serial):
    try:
        #print ("reading in sensors", flush=True)
        logger.info("reading in sensors")
        # Sensors
        sensor_types = object_factory.configure_sensor_types(config.get('Sensors','sensor_types', fallback="[]"))
        sensor_class_list = object_factory.configure_sensors(config.get('Sensors','sensor_list', fallback="[]"),
                                                            sensor_types,
                                                            ardoino_serial)
        return sensor_class_list
    except Exception as e:
        logger.error(f"Reading config file was not succesfully in the Sensors section {e}")
        return []

def read_actuators_config(config, ardoino_serial):
    try:
        #print ("reading in actuators", flush=True)
        logger.info("reading in actuators")
        # Actuators
        actuator_types = object_factory.configure_actuator_types(config.get('Actuators','actuator_types', fallback="[]"))
        actuator_class_list = object_factory.configure_actuators(config.get('Actuators','actuator_list', fallback="[]"),
                                                                actuator_types,
                                                                ardoino_serial)
        return actuator_class_list
    except Exception as e:
        logger.error(f"Reading config file was not succesfully in the Actuators section {e}")
        return []

def read_virtual_environment_config(config, sensor_class_list, actuator_class_list):
    try:
        #print ("reading in VirtualEnfironment mapping", flush=True)
        logger.info("reading in VirtualEnfironment mapping")
        # VirtualEnfironment
        virtual_enfironment_list = object_factory.configure_environment_map(config.get('VirtualEnfironment','virtual_enfironment_list', fallback="[]"))
        virtual_environment = object_factory.configure_environment(sensors=sensor_class_list,
                                                                actuators=actuator_class_list,
                                                                virtual_enfironment_list=virtual_enfironment_list)
        return virtual_environment
    except Exception as e:
        logger.error(f"Reading config file was not succesfully in the VirtualEnfironment section {e}")
        virtual_environment = object_factory.configure_environment(sensors=[], actuators=[], virtual_enfironment_list=[])
        print (virtual_environment)
        return virtual_environment

def read_config(config_file_name: str, password: str, host: str=None):
    print (f"reading in {config_file_name}", flush=True)
    try:
        config = configparser.ConfigParser(interpolation=None)
        config.read(config_file_name, encoding='utf-8')
    except Exception as e:
        logger.error(f"Reading config file {config_file_name} was not succesfull {e}")
        raise e

    max_cycle_time, sleeping_time = read_general_config(config)

    _, mqtt_host, mqtt_port, mqtt_username, mqtt_base_topic, mqtt_timeout = read_mqtt_config(config)
    if host != None:
        mqtt_host = host
    print(mqtt_host)
    room_info = read_architecture_config(config)

    ardoino_serial = read_ardoino_config(config)

    sensor_class_list = read_sensors_config(config, ardoino_serial)
    actuator_class_list = read_actuators_config(config, ardoino_serial)
    virtual_environment = read_virtual_environment_config(config, sensor_class_list, actuator_class_list)

    #print ("creating gateway_network", flush=True)
    logger.info("creating gateway_network")
    # GatewayNetwork
    gateway_network = object_factory.configure_network_gateway(host=mqtt_host,
                                                               port=mqtt_port,
                                                               username=mqtt_username,
                                                               password=password,
                                                               timeout=mqtt_timeout,
                                                               base_topic=mqtt_base_topic,
                                                               room_info=room_info,
                                                               sensors=sensor_class_list,
                                                               actuators=actuator_class_list)

    # returnobject
    config_values = {
        'max_cycle_time': max_cycle_time,
        'sleeping_time': sleeping_time,
        'ardoino_serial': ardoino_serial,
        'room_info': room_info,
        'sensor_class_list': sensor_class_list,
        'actuator_class_list': actuator_class_list,
        'virtual_environment':virtual_environment,
        'gateway_network':gateway_network
    }

    return config_values
