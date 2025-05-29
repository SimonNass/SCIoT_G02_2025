import json

from sensors.sensor import Sensor
from actuators.actuator import Actuator
from actuators.display import Display
from enumdef import Connectortype, Notifyinterval

def configure_sensors(json_list: json, types: dict):
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
            sensor_object = Sensor(name=name,type_name=type_name,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value, datatype=datatype,unit=unit,read_interval=read_interval,notify_interval=notify_interval,notify_change_precision=notify_change_precision)
            sensors.append(sensor_object)
        except Exception as e:
            print (e, flush=True)
    return sensors

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

def configure_actuators(json_list: json, types: dict):
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
            if connector_types == Connectortype.I2C_display:
                actuator_object = Display(name=name,type_name=type_name,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value,datatype=datatype,unit=unit,initial_value=initial_value,off_value=off_value)
            else:
                actuator_object = Actuator(name=name,type_name=type_name,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value,datatype=datatype,unit=unit,initial_value=initial_value,off_value=off_value)
            actuators.append(actuator_object)
        except Exception as e:
            print (e, flush=True)
    return actuators

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
