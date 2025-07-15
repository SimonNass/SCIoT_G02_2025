"""Module specivies the creation of objects during the config reading process."""

import json
from typing import List, Dict, Union
import logging
from sensors.sensor import SensorInterface, AnalogSensor, DigitalSensor, DigitalMultipleSensor, VirtualSensor_numerical, VirtualSensor_binary
from sensors.ardoino_sensor import ArdoinoSensor
from actuators.actuator import ActuatorInterface, AnalogActuator, DigitalActuator, VirtualActuator_numerical
from actuators.display import DisplayActuator, VirtualActuator_textual
from actuators.ardoino_actuator import ArdoinoActuator
from virtual_environment import Virtual_environment
from enumdef import Connectortype, Notifyinterval
from networking.ardoino_reverse_proxy import ArdoinoReverseProxy
from networking.networking_domain import GatewayNetwork
from room_info import Room_Info
logger = logging.getLogger(__name__)

def configure_network_gateway(host: str,
                              port: int,
                              username: str,
                              password: str,
                              timeout: int,
                              base_topic: str,
                              room_info: Room_Info,
                              actuators: List[ActuatorInterface]):
    gateway_network = None
    try:
        gateway_network = GatewayNetwork(
            host=host,
            port=port,
            username=username,
            password=password,
            timeout=int(timeout),
            base_topic=base_topic,
            room_info=room_info,
            actuators=actuators
        )
    except Exception as e:
        print ("MQTT broker not connected.")
        print (e, flush=True)
        logger.error(f"MQTT broker not connected. {e}")
    return gateway_network

def configure_environment(sensors: List[SensorInterface], actuators: List[ActuatorInterface], virtual_enfironment_list: List[Dict[str,str]]):
    virtual_environment = None
    try:
        virtual_environment = Virtual_environment(
            sensors=sensors,
            actuators=actuators,
            mapping=virtual_enfironment_list
        )
    except Exception as e:
        print ("virtual_environment not initialised.")
        print (e, flush=True)
        logger.error(f"virtual_environment not initialised. {e}")
    return virtual_environment

def configure_room_info(floor_id: int, max_rooms_per_floor: int, room_id: int):
    return Room_Info(floor_id, max_rooms_per_floor, room_id)

def configure_ardoino_connection(message_end_signal: str, usb_channel_type: str, usb_channel_data_rate: int):
    ardoino_serial = None
    try:
        ardoino_serial = ArdoinoReverseProxy(message_end_signal=message_end_signal,usb_channel_type=usb_channel_type,usb_channel_data_rate=usb_channel_data_rate)
    except Exception as e:
        print (e, flush=True)
        logger.error(f"{e}")
    return ardoino_serial

def configure_environment_map(json_list: json):
    init_list = json.loads(json_list)
    return init_list

def configure_sensors(json_list: json, types: dict, ardoino_serial: ArdoinoReverseProxy):
    init_list = json.loads(json_list)
    sensors = []
    for s in init_list:
        name = str(s['name'])
        type_name = str(s['type_name'])
        room_position = str(s['room_position'])
        ai_planing_type = str(s['ai_planing_type'])
        connector = int(s['connector'])
        connector_types = types[type_name]['connector_types']
        min_value = types[type_name]['min']
        max_value = types[type_name]['max']
        datatype = types[type_name]['datatype']
        unit = types[type_name]['unit']
        read_interval = types[type_name]['read_interval']
        notify_interval = types[type_name]['notify_interval']
        notify_change_precision = types[type_name]['notify_change_precision']
        try:
            sensor_object = choose_sensor_class(name=name,
                                                type_name=type_name,
                                                room_position=room_position,
                                                ai_planing_type=ai_planing_type,
                                                connector=connector,
                                                connector_types=connector_types,
                                                min_value=min_value,
                                                max_value=max_value,
                                                datatype=datatype,
                                                unit=unit,
                                                read_interval=read_interval,
                                                notify_interval=notify_interval,
                                                notify_change_precision=notify_change_precision,
                                                ardoino_serial=ardoino_serial)

            sensors.append(sensor_object)
        except Exception as e:
            print (e, flush=True)
            logger.info(f"{e}")
    return sensors

def choose_sensor_class(name: str, type_name: str, room_position: str, ai_planing_type: str, connector: int, connector_types: Connectortype, min_value: int, max_value: int, datatype: str, unit: str, read_interval: int, notify_interval: Notifyinterval, notify_change_precision: int, ardoino_serial: ArdoinoReverseProxy):
    try:
        sensor_object = None
        if connector_types == Connectortype.Analog:
            sensor_object = AnalogSensor(name=name,type_name=type_name,room_position=room_position,ai_planing_type=ai_planing_type,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value, datatype=datatype,unit=unit,read_interval=read_interval,notify_interval=notify_interval,notify_change_precision=notify_change_precision)
        elif connector_types == Connectortype.Digital:
            sensor_object = DigitalSensor(name=name,type_name=type_name,room_position=room_position,ai_planing_type=ai_planing_type,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value, datatype=datatype,unit=unit,read_interval=read_interval,notify_interval=notify_interval,notify_change_precision=notify_change_precision)
        elif connector_types == Connectortype.Digital_multiple_0:
            sensor_object = DigitalMultipleSensor(name=name,type_name=type_name,room_position=room_position,ai_planing_type=ai_planing_type,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value, datatype=datatype,unit=unit,read_interval=read_interval,notify_interval=notify_interval,notify_change_precision=notify_change_precision,i=0)
        elif connector_types == Connectortype.Digital_multiple_1:
            sensor_object = DigitalMultipleSensor(name=name,type_name=type_name,room_position=room_position,ai_planing_type=ai_planing_type,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value, datatype=datatype,unit=unit,read_interval=read_interval,notify_interval=notify_interval,notify_change_precision=notify_change_precision,i=1)
        elif connector_types == Connectortype.Virtual_numerical:
            sensor_object = VirtualSensor_numerical(name=name,type_name=type_name,room_position=room_position,ai_planing_type=ai_planing_type,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value, datatype=datatype,unit=unit,read_interval=read_interval,notify_interval=notify_interval,notify_change_precision=notify_change_precision)
        elif connector_types == Connectortype.Virtual_binary:
            sensor_object = VirtualSensor_binary(name=name,type_name=type_name,room_position=room_position,ai_planing_type=ai_planing_type,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value, datatype=datatype,unit=unit,read_interval=read_interval,notify_interval=notify_interval,notify_change_precision=notify_change_precision)
        elif connector_types == Connectortype.Ardoino_temperature:
            sensor_object = ArdoinoSensor(name=name,type_name=type_name,room_position=room_position,ai_planing_type=ai_planing_type,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value, datatype=datatype,unit=unit,read_interval=read_interval,notify_interval=notify_interval,notify_change_precision=notify_change_precision,ardoino_serial=ardoino_serial,type_name_ardoino="temperature")
        elif connector_types == Connectortype.Ardoino_humidity:
            sensor_object = ArdoinoSensor(name=name,type_name=type_name,room_position=room_position,ai_planing_type=ai_planing_type,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value, datatype=datatype,unit=unit,read_interval=read_interval,notify_interval=notify_interval,notify_change_precision=notify_change_precision,ardoino_serial=ardoino_serial,type_name_ardoino="humidity")
        elif connector_types == Connectortype.Ardoino_soundlevel:
            sensor_object = ArdoinoSensor(name=name,type_name=type_name,room_position=room_position,ai_planing_type=ai_planing_type,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value, datatype=datatype,unit=unit,read_interval=read_interval,notify_interval=notify_interval,notify_change_precision=notify_change_precision,ardoino_serial=ardoino_serial,type_name_ardoino="soundlevel")
        elif connector_types == Connectortype.Ardoino_rfid:
            sensor_object = ArdoinoSensor(name=name,type_name=type_name,room_position=room_position,ai_planing_type=ai_planing_type,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value, datatype=datatype,unit=unit,read_interval=read_interval,notify_interval=notify_interval,notify_change_precision=notify_change_precision,ardoino_serial=ardoino_serial,type_name_ardoino="rfid")
        else:
            raise ValueError("Connector_type is not implemented.")
        return sensor_object
    except Exception as e:
        print (e, flush=True)
        logger.error(f"{e}")
    raise ValueError("Connector_type is not implemented.")

def configure_sensor_types(json_list: json):
    init_list = json.loads(json_list)
    types = {}
    for t in init_list:
        mame_key = str(t['type_name'])
        connector_types = getattr(Connectortype, str(t['connector_types']))
        min_value = int(t['min'])
        max_value = int(t['max'])
        datatype = str(t['datatype'])
        unit = str(t['unit'])
        read_interval = int(t['read_interval'])
        notify_interval = getattr(Notifyinterval, str(t['notify_interval']))
        notify_change_precision = int(t['notify_change_precision'])
        t_dict = {'mame_key':mame_key,'connector_types':connector_types,'min':min_value,'max':max_value,'datatype':datatype,'unit':unit,'read_interval':read_interval,'notify_interval':notify_interval,'notify_change_precision':notify_change_precision}
        types.update({mame_key:t_dict})
    return types

def configure_actuators(json_list: json, types: dict, ardoino_serial: ArdoinoReverseProxy):
    init_list = json.loads(json_list)
    actuators = []
    for a in init_list:
        name = str(a['name'])
        type_name = str(a['type_name'])
        room_position = str(a['room_position'])
        ai_planing_type = str(a['ai_planing_type'])
        connector = int(a['connector'])
        connector_types = types[type_name]['connector_types']
        min_value = types[type_name]['min']
        max_value = types[type_name]['max']
        datatype = types[type_name]['datatype']
        unit = types[type_name]['unit']
        initial_value = types[type_name]['initial_value']
        off_value = types[type_name]['off_value']
        try:
            actuator_object = choose_actuator_class(name=name,
                                                    type_name=type_name,
                                                    room_position=room_position,
                                                    ai_planing_type=ai_planing_type,
                                                    connector=connector,
                                                    connector_types=connector_types,
                                                    min_value=min_value,
                                                    max_value=max_value,
                                                    datatype=datatype,
                                                    unit=unit,
                                                    initial_value=initial_value,
                                                    off_value=off_value,
                                                    ardoino_serial=ardoino_serial)

            actuators.append(actuator_object)
        except Exception as e:
            print (e, flush=True)
            logger.error(f"{e}")
    return actuators

def choose_actuator_class(name: str,
                          type_name: str,
                          connector: int,
                          room_position: str,
                          ai_planing_type: str,
                          connector_types: Connectortype,
                          min_value: Union[int, str],
                          max_value: Union[int, str],
                          datatype: str,
                          unit: str,
                          initial_value: Union[int, str],
                          off_value: Union[int, str],
                          ardoino_serial: ArdoinoReverseProxy):
    try:
        actuator_object = None
        if connector_types == Connectortype.I2C_display:
            actuator_object = DisplayActuator(name=name,
                                   type_name=type_name,
                                   room_position=room_position,
                                   ai_planing_type=ai_planing_type,
                                   connector=connector,
                                   connector_types=connector_types,
                                   min_value=min_value,
                                   max_value=max_value,
                                   datatype=datatype,
                                   unit=unit,
                                   initial_value=initial_value,
                                   off_value=off_value)
        elif connector_types == Connectortype.Analog:
            actuator_object = AnalogActuator(name=name,
                                  type_name=type_name,
                                  room_position=room_position,
                                  ai_planing_type=ai_planing_type,
                                  connector=connector,
                                  connector_types=connector_types,
                                  min_value=min_value,
                                  max_value=max_value,
                                  datatype=datatype,
                                  unit=unit,
                                  initial_value=initial_value,
                                  off_value=off_value)
        elif connector_types == Connectortype.Digital:
            actuator_object = DigitalActuator(name=name,
                                   type_name=type_name,
                                   room_position=room_position,
                                   ai_planing_type=ai_planing_type,
                                   connector=connector,
                                   connector_types=connector_types,
                                   min_value=min_value,
                                   max_value=max_value,
                                   datatype=datatype,
                                   unit=unit,
                                   initial_value=initial_value,
                                   off_value=off_value)
        elif connector_types == Connectortype.Virtual_numerical:
            actuator_object = VirtualActuator_numerical(name=name,
                                   type_name=type_name,
                                   room_position=room_position,
                                   ai_planing_type=ai_planing_type,
                                   connector=connector,
                                   connector_types=connector_types,
                                   min_value=min_value,
                                   max_value=max_value,
                                   datatype=datatype,
                                   unit=unit,
                                   initial_value=initial_value,
                                   off_value=off_value)
        elif connector_types == Connectortype.Virtual_textual:
            actuator_object = VirtualActuator_textual(name=name,
                                   type_name=type_name,
                                   room_position=room_position,
                                   ai_planing_type=ai_planing_type,
                                   connector=connector,
                                   connector_types=connector_types,
                                   min_value=min_value,
                                   max_value=max_value,
                                   datatype=datatype,
                                   unit=unit,
                                   initial_value=initial_value,
                                   off_value=off_value)
        elif connector_types == Connectortype.Ardoino_motor:
            actuator_object = ArdoinoActuator(name=name,
                                   type_name=type_name,
                                   room_position=room_position,
                                   ai_planing_type=ai_planing_type,
                                   connector=connector,
                                   connector_types=connector_types,
                                   min_value=min_value,
                                   max_value=max_value,
                                   datatype=datatype,
                                   unit=unit,
                                   initial_value=initial_value,
                                   off_value=off_value,
                                   ardoino_serial=ardoino_serial,
                                   type_name_ardoino="motor")
        else:
            raise ValueError("Connector_type is not implemented.")
        return actuator_object
    except Exception as e:
        print (e, flush=True)
        logger.error(f"{e}")
    logger.warning("Connector_type is not implemented.")
    raise ValueError("Connector_type is not implemented.")

def configure_actuator_types(json_list: json):
    init_list = json.loads(json_list)
    types = {}
    for t in init_list:
        mame_key = str(t['type_name'])
        connector_types = getattr(Connectortype, str(t['connector_types']))
        datatype = str(t['datatype'])
        unit = str(t['unit'])
        if connector_types in [Connectortype.I2C_display, Connectortype.Virtual_textual]:
            min_value = str(t['min'])
            max_value = str(t['max'])
            initial_value = str(t['initial_value'])
            off_value = str(t['off_value'])
        else:
            min_value = int(t['min'])
            max_value = int(t['max'])
            initial_value = int(t['initial_value'])
            off_value = int(t['off_value'])
        t_dict = {'mame_key':mame_key,'connector_types':connector_types,'min':min_value,'max':max_value,'datatype':datatype,'unit':unit,'initial_value':initial_value,'off_value':off_value}
        types.update({mame_key:t_dict})
    return types
