import serial.tools.list_ports
import logging
logger = logging.getLogger(__name__)

def find_serial_port():
    ports = serial.tools.list_ports.comports()
    logger.info(f"{len(ports)}, ports found")
    for p in ports:
        logger.info(f"Serial port: {p.device}: {p.description}")
    return list((str(p.device) for p in ports))