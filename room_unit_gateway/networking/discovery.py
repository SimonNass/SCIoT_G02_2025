import serial.tools.list_ports
import httpx
import socket
import logging
logger = logging.getLogger(__name__)

def find_serial_port():
    ports = serial.tools.list_ports.comports()
    logger.info(f"{len(ports)}, ports found")
    for p in ports:
        logger.info(f"Serial port: {p.device}: {p.description}")
    return list((str(p.device) for p in ports))

def find_mqtt_broker_ip():
    prefix = 'http://'
    host = 'MSI'
    path = '/health'
    url = prefix + host + path
    response = httpx.get(url)
    response.raise_for_status()
    if not response.is_success:
        # TODO andle some errors
        pass
    data = response.content
    if data != b'healthy\n':
        print (data)
        # TODO andle some errors
    ip_address = socket.gethostbyname(host)
    print (ip_address)
    return str(ip_address)