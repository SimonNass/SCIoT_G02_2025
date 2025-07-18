#!/usr/bin/env python
"""Module specifies the entry point of the program for the physical pi version.
It also defines the CLI argument reading."""

import sys
import logging
import help_methods
logger = logging.getLogger(__name__)

def main():
    """
    Usage:
      python main.py <config_folder>/<config_file.ini> [<mqtt_host>] <mqtt_password>
    """

    logging.basicConfig(filename='pi_room_gateway.log', level=logging.INFO)
    logger.info("xxxx Started new execution.")
    help_methods.system_info()

    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print ("Error CLI arguments incorrect")
        print("Usage: python main.py <config_folder>/<config_file.ini> [<mqtt_host>] <mqtt_password>")
        print (sys.argv)
        logger.warning(f"Error CLI arguments incorrect {sys.argv}")
        sys.exit(1)

    config_file_name = str(sys.argv[1])
    if len(sys.argv) == 3:
        password = str(sys.argv[2])
        host = None
    elif len(sys.argv) == 4:
        host = str(sys.argv[2])
        password = str(sys.argv[3])
    else:
        sys.exit(1)

    print ("", flush=True)
    help_methods.run_gateway_for_config(config_file_name, password, host)

# __name__
if __name__=="__main__":
    main()
