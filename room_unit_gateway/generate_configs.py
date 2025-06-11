# generate_configs.py
# ------------------------------------------------------------
# Produces 10 INI files under ./configs, each with an empty Actuators section.
# Floor 1: rooms 1–6; Floor 2: rooms 1–4.
#
# Usage:
#   python generate_configs.py
# ------------------------------------------------------------

import os

BASE_DIR = os.path.join(os.getcwd(), "configs")
os.makedirs(BASE_DIR, exist_ok=True)

COMMON_HEADER_GENERAL = """[General]
version = 2

"""

COMMON_HEADER_MQTT = """[MQTT]
name       = "MascitoMQTT"
host       = "localhost"
port       = 1884
username   = "test"
base_topic = "SCIoT_G02_2025"

"""

COMMON_HEADER_ARDOINO = """[Ardoino]
message_end_signal = EndOfSerial
usb_channel_type = COM6
usb_channel_data_rate = 9600 

"""

COMMON_HEADER_ARCHITECTURE = """[Architecture]
max_rooms_per_floor = 100
"""

# Single-line JSON arrays for Sensors (notify_change_precision now integer)
SENSOR_TYPES_JSON = (
    '[ '
    '{"type_name":"temperature","connector_types":"Virtual","min":"15","max":"30","datatype":"float","unit":"°C","read_interval":"2","notify_interval":"on_change_timeout","notify_change_precision":"1"}, '
    '{"type_name":"humidity","connector_types":"Virtual","min":"30","max":"70","datatype":"float","unit":"%RH","read_interval":"3","notify_interval":"on_change_timeout","notify_change_precision":"1"}, '
    '{"type_name":"noise","connector_types":"Virtual","min":"30","max":"90","datatype":"float","unit":"dB","read_interval":"2","notify_interval":"on_change_timeout","notify_change_precision":"3"}, '
    '{"type_name":"occupancy","connector_types":"Virtual","min":"0","max":"1","datatype":"bool","unit":"On_Off","read_interval":"1","notify_interval":"on_rising_edge_stable_timeout","notify_change_precision":"1"}, '
    '{"type_name":"energy_virtual","connector_types":"Virtual","min":"0","max":"5000","datatype":"float","unit":"Wh","read_interval":"5","notify_interval":"on_change_timeout","notify_change_precision":"50"} '
    ']'
)

SENSOR_LIST_JSON = (
    '[ '
    '{"name":"temp","type_name":"temperature","connector":"100"}, '
    '{"name":"hum","type_name":"humidity","connector":"101"}, '
    '{"name":"dB","type_name":"noise","connector":"102"}, '
    '{"name":"occ","type_name":"occupancy","connector":"103"}, '
    '{"name":"kWh","type_name":"energy_virtual","connector":"104"} '
    ']'
)

# Empty JSON arrays for actuators:
EMPTY_ACTUATOR_TYPES_JSON = "[]"
EMPTY_ACTUATOR_LIST_JSON  = "[]"

def make_config(floor_id: int, room_id: int):
    header = COMMON_HEADER_ARCHITECTURE + f"floor_ID            = {floor_id}\nroom_ID             = {room_id}\n\n"

    sensors_section = (
        "[Sensors]\n"
        f"sensor_types = {SENSOR_TYPES_JSON}\n"
        f"sensor_list  = {SENSOR_LIST_JSON}\n\n"
    )

    # Actuators section now has two empty arrays
    actuators_section = (
        "[Actuators]\n"
        f"actuator_types = {EMPTY_ACTUATOR_TYPES_JSON}\n"
        f"actuator_list  = {EMPTY_ACTUATOR_LIST_JSON}\n"
    )

    content = COMMON_HEADER_GENERAL + COMMON_HEADER_MQTT + COMMON_HEADER_ARDOINO + header + sensors_section + actuators_section
    filename = f"config_room_f{floor_id}_r{room_id}.ini"
    path = os.path.join(BASE_DIR, filename)
    with open(path, "w") as f:
        f.write(content)
        print(f"Generated {filename}")
    #print(f"Generated {filename}")

def main():
    # Floor 1: rooms 1–6
    for r in range(1, 7):
        make_config(floor_id=1, room_id=r)
    # Floor 2: rooms 1–4
    for r in range(1, 5):
        make_config(floor_id=2, room_id=r)

if __name__ == "__main__":
    main()
