import serial as serial
import time
import logging
logger = logging.getLogger(__name__)

from networking.discovery import find_serial_port

class ArdoinoReverseProxy():
    def __init__(self, message_end_signal: str, usb_channel_type: str, usb_channel_data_rate: int):
        self.message_end_signal = message_end_signal
        self.usb_channel_type_default = usb_channel_type
        self.usb_channel_type_discovered = self.usb_channel_type_default
        try:
            # TODO iterate over discovered ones and find the right one
            self.usb_channel_type_discovered = find_serial_port()[0]
        except (Exception, IOError, TypeError, AttributeError) as e:
            logger.error("no serial port found {}".format(e))
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
            logger.error("connection to ardoino_serial was unsucesful {}".format(e))

    def __del__(self):
        try:
            self.remote_call(exit,0)
            self.ardoino_serial.close()
        except (Exception, IOError, TypeError, AttributeError) as e:
            print ("closing ardoino_serial was unsucesful")
            #print (e)
            logger.error("closing ardoino_serial was unsucesful {}".format(e))
    
    def remote_call(self, type_name: str, value):
        try:
            request_str = str(type_name) + ':' + str(value) + '\n'
            #print("Request > {} \n".format(request_str))
            self.ardoino_serial.write(request_str.encode('UTF-8'))
            time.sleep(1)
            data = b'Start'
            while (str(remove_line_ending(data.decode('utf-8'))) !=(str(self.message_end_signal))):
                data = self.ardoino_serial.readline()
                print (str(remove_line_ending(data.decode('utf-8'))))
            return 0
        except (Exception, KeyboardInterrupt) as e:
            print("Stopping")
            print(e)

def remove_line_ending(string: str):
    return string.strip()
    #return string.replace("\r","").replace("\n","")
    