#!/usr/bin/env python
"""Module specifies the entry point of the program for the virtual room threading version.
It also defines the CLI argument reading."""

import time
import sys
import logging
import os
import threading

logger = logging.getLogger(__name__)

import help_methods

def main():
    """
    Usage:
      python main.py <config_folder> <mqtt_password>
    It will scan <config_folder> for all “*.ini” files and spawn one thread per file.
    """
    logging.basicConfig(filename='pi_room_gateway.log', level=logging.INFO)

    if len(sys.argv) != 3:
        print("Usage: python main.py <config_folder> <mqtt_password>")
        sys.exit(1)

    config_folder, password = sys.argv[1], sys.argv[2]

    if not os.path.isdir(config_folder):
        print(f"Error: '{config_folder}' is not a directory or does not exist.", file=sys.stderr)
        sys.exit(1)

    # Find all .ini files in the folder (non‐recursive)
    ini_files = [
        os.path.join(config_folder, f)
        for f in os.listdir(config_folder)
        if f.lower().endswith(".ini")
    ]

    if not ini_files:
        print(f"No .ini files found in '{config_folder}'.", file=sys.stderr)
        sys.exit(1)

    threads = []
    for cfg in ini_files:
        t = threading.Thread(
            target=help_methods.run_gateway_for_config,
            args=(cfg, password),
            daemon=True
        )
        t.start()
        threads.append(t)

    try:
        # Keep main thread alive while child threads run indefinitely
        while any(t.is_alive() for t in threads):
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down all gateway threads...")

if __name__ == "__main__":
    main()
