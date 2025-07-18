"""Module specifies all infos of the general IoT device."""
import uuid
from enumdef import Connectortype

class IoT_Info():
    def __init__(self, name: str, type_name: str, room_position: str, ai_planing_type: str, connector: int, connector_type: Connectortype, min_value: int, max_value: int, datatype: str, unit: str):
        self.id = uuid.uuid1()
        self.name = name
        self.type = type_name
        self.room_position = room_position
        self.ai_planing_type = ai_planing_type
        self.i2c_connector = connector #assert not used twice
        self.connector_type = connector_type
        self.min_value = min_value
        self.max_value = max_value
        if min_value > max_value:
            self.min_value = max_value
            self.max_value = min_value
        self.datatype = datatype
        self.unit = unit

    def __dict__(self):
        return {"id":str(self.id),"name":self.name,"type_name":self.type,"room_position":self.room_position,"ai_planing_type":self.ai_planing_type,"connector":self.i2c_connector,"connector_type":str(self.connector_type),"min":self.min_value, "max":self.max_value, "datatype":self.datatype, "unit":self.unit}
