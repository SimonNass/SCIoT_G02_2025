import json
import logging
logger = logging.getLogger(__name__)

from sensors.sensor import AnalogSensor, DigitalSensor, DigitalMultipleSensor, VirtualSensor
from sensors.ardoino_sensor import ArdoinoSensor

from actuators.actuator import AnalogActuator, DigitalActuator
from actuators.display import DisplayActuator
from actuators.ardoino_actuator import ArdoinoActuator

from enumdef import Connectortype, Notifyinterval
from networking.ardoino_reverse_proxy import ArdoinoReverseProxy

def configure_ardoino_connection(message_end_signal: str, usb_channel_type: str, usb_channel_data_rate: int):  
    try:
        ardoino_serial = ArdoinoReverseProxy(message_end_signal=message_end_signal,usb_channel_type=usb_channel_type,usb_channel_data_rate=usb_channel_data_rate)
    except Exception as e:
        print (e, flush=True)
        logger.info("{}".format(e))
    return ardoino_serial

def configure_sensors(json_list: json, types: dict, ardoino_serial: ArdoinoReverseProxy):
    init_list = json.loads(json_list)
    sensors = []
    for s in init_list:
        name = str(s['name'])
        type_name = str(s['type_name'])
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
            sensor_object = choose_sensor_class(name=name,type_name=type_name,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value, datatype=datatype,unit=unit,read_interval=read_interval,notify_interval=notify_interval,notify_change_precision=notify_change_precision,ardoino_serial=ardoino_serial)
            
            sensors.append(sensor_object)
        except Exception as e:
            print (e, flush=True)
            logger.info("{}".format(e))
    return sensors

def choose_sensor_class(name: str, type_name: str, connector: int, connector_types: Connectortype, min_value: int, max_value: int, datatype: str, unit: str, read_interval: int, notify_interval: Notifyinterval, notify_change_precision: int, ardoino_serial: ArdoinoReverseProxy):
    try:
        if connector_types == Connectortype.Analog:
            return AnalogSensor(name=name,type_name=type_name,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value, datatype=datatype,unit=unit,read_interval=read_interval,notify_interval=notify_interval,notify_change_precision=notify_change_precision)
        elif connector_types == Connectortype.Digital:
            return DigitalSensor(name=name,type_name=type_name,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value, datatype=datatype,unit=unit,read_interval=read_interval,notify_interval=notify_interval,notify_change_precision=notify_change_precision)
        elif connector_types == Connectortype.Digital_multiple_0:
            return DigitalMultipleSensor(name=name,type_name=type_name,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value, datatype=datatype,unit=unit,read_interval=read_interval,notify_interval=notify_interval,notify_change_precision=notify_change_precision,i=0)
        elif connector_types == Connectortype.Digital_multiple_1:
            return DigitalMultipleSensor(name=name,type_name=type_name,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value, datatype=datatype,unit=unit,read_interval=read_interval,notify_interval=notify_interval,notify_change_precision=notify_change_precision,i=1)
        elif connector_types == Connectortype.Virtual:
            return VirtualSensor(name=name,type_name=type_name,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value, datatype=datatype,unit=unit,read_interval=read_interval,notify_interval=notify_interval,notify_change_precision=notify_change_precision)
        elif connector_types == Connectortype.Ardoino:
            return ArdoinoSensor(name=name,type_name=type_name,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value, datatype=datatype,unit=unit,read_interval=read_interval,notify_interval=notify_interval,notify_change_precision=notify_change_precision,ardoino_serial=ardoino_serial,type_name_ardoino="test")
        else:
            raise ValueError("Connector_type is not implemented.")
    except Exception as e:
        print (e, flush=True)
        logger.info("{}".format(e))
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
        connector = int(a['connector'])
        connector_types = types[type_name]['connector_types']
        min_value = types[type_name]['min']
        max_value = types[type_name]['max']
        datatype = types[type_name]['datatype']
        unit = types[type_name]['unit']
        initial_value = types[type_name]['initial_value']
        off_value = types[type_name]['off_value']
        try:
            actuator_object = choose_actuator_class(name=name,type_name=type_name,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value,datatype=datatype,unit=unit,initial_value=initial_value,off_value=off_value,ardoino_serial=ardoino_serial)

            actuators.append(actuator_object)
        except Exception as e:
            print (e, flush=True)
            logger.info("{}".format(e))
    return actuators

def choose_actuator_class(name: str, type_name: str, connector: int, connector_types: Connectortype, min_value: int, max_value: int, datatype: str, unit: str, initial_value: int, off_value: int, ardoino_serial: ArdoinoReverseProxy):
    try:
        if connector_types == Connectortype.I2C_display:
            return DisplayActuator(name=name,type_name=type_name,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value,datatype=datatype,unit=unit,initial_value=initial_value,off_value=off_value)
        elif connector_types == Connectortype.Analog:
            return AnalogActuator(name=name,type_name=type_name,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value,datatype=datatype,unit=unit,initial_value=initial_value,off_value=off_value)
        elif connector_types == Connectortype.Digital:
            return DigitalActuator(name=name,type_name=type_name,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value,datatype=datatype,unit=unit,initial_value=initial_value,off_value=off_value)
        elif connector_types == Connectortype.Ardoino_temperature:
            return ArdoinoActuator(name=name,type_name=type_name,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value,datatype=datatype,unit=unit,initial_value=initial_value,off_value=off_value,ardoino_serial=ardoino_serial,type_name_ardoino="temperature")
        elif connector_types == Connectortype.Ardoino_humidity:
            return ArdoinoActuator(name=name,type_name=type_name,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value,datatype=datatype,unit=unit,initial_value=initial_value,off_value=off_value,ardoino_serial=ardoino_serial,type_name_ardoino="humidity")
        elif connector_types == Connectortype.Ardoino_soundlevel:
            return ArdoinoActuator(name=name,type_name=type_name,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value,datatype=datatype,unit=unit,initial_value=initial_value,off_value=off_value,ardoino_serial=ardoino_serial,type_name_ardoino="soundlevel")
        else:
            raise ValueError("Connector_type is not implemented.")
    except Exception as e:
        print (e, flush=True)
        logger.info("{}".format(e))
    raise ValueError("Connector_type is not implemented.")

def configure_actuator_types(json_list: json):
    init_list = json.loads(json_list)
    types = {}
    for t in init_list:
        mame_key = str(t['type_name'])
        connector_types = getattr(Connectortype, str(t['connector_types']))
        datatype = str(t['datatype'])
        unit = str(t['unit'])
        if connector_types == Connectortype.I2C_display:
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
