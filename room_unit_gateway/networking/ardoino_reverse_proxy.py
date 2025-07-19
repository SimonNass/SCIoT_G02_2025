"""Module specifies the arduino proxy for communication to the arduino."""

import logging
import time
import serial
from networking.discovery import find_serial_port
logger = logging.getLogger(__name__)

class ArdoinoReverseProxy():
    def __init__(self, message_end_signal: str, usb_channel_type: str, usb_channel_data_rate: int):
        self.message_end_signal = message_end_signal
        self.usb_channel_type_default = usb_channel_type
        self.usb_channel_type_discovered = self.usb_channel_type_default
        try:
            # TODO iterate over discovered ones and find the right one
            self.usb_channel_type_discovered = find_serial_port()[0]
        except (Exception, IOError, TypeError, AttributeError) as e:
            logger.error(f"no serial port found {e}")
        print (self.usb_channel_type_discovered)
        self.usb_channel_data_rate = usb_channel_data_rate
        # in bps
        self.ardoino_serial = None
        try:
            self.ardoino_serial = serial.Serial(self.usb_channel_type_discovered, self.usb_channel_data_rate, timeout=1)
            time.sleep(2)
        except (Exception, IOError, TypeError, AttributeError) as e:
            print ("connection to ardoino_serial was unsucesful")
            #print (e)
            logger.error(f"connection to ardoino_serial was unsucesful {e}")

    def __del__(self):
        try:
            self.remote_call(exit,0)
            self.ardoino_serial.close()
        except (Exception, IOError, TypeError, AttributeError) as e:
            print ("closing ardoino_serial was unsucesful")
            #print (e)
            logger.error(f"closing ardoino_serial was unsucesful {e}")

    def remote_call(self, type_name: str, value):
        try:
            request_str = str(type_name) + ':' + str(value) + '\n'
            #print("Request > {} \n".format(request_str))
            self.ardoino_serial.write(request_str.encode('UTF-8'))
            time.sleep(1)
            data_line = b'Start'
            data = ''
            while (str(remove_line_ending(data_line.decode('utf-8'))) !=(str(self.message_end_signal))):
                data_line = self.ardoino_serial.readline()
                data = data + remove_line_ending(data_line.decode('utf-8'))
            data = data.replace(str(self.message_end_signal),'')
            if ':' in data:
                data = data.split(':')[1]
                data = data.replace(' ','')
            else:
                data = '-1'
            data = float(remove_line_ending(data))
            #print (data)
            return data
        except (Exception, KeyboardInterrupt) as e:
            print("Stopping")
            print(e)
        raise KeyboardInterrupt("Ardoino remote call unsucessfull")

def remove_line_ending(string: str):
    return string.strip()
    #return string.replace("\r","").replace("\n","")
    