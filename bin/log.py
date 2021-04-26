#!/usr/bin/env python3

# Allow module load from lib/python in main repo
import sys
from pathlib import Path
currentdir = Path(__file__).resolve(strict=True).parent
libdir = currentdir.parent.joinpath('lib/python')
sys.path.append(str(libdir))

import argparse
from structlog import get_logger
from pathlib import Path
import io
import os
import json
import time
import serial
import struct

from secondlife.celldb import find_cell, load_metadata, new_cell

log = get_logger()

from secondlife.celldb import new_cell, store_measurement, change_properties
from secondlife.plugins.api import v1, load_plugins
from secondlife.cli.utils import cell_identifiers, measurement_ts


def main(config):
    global log

    for id in cell_identifiers(config):

        log = log.bind(id=id)

        if config.pause_before_cell:
            input(f"Press Enter to begin handling cell '{id}' >")
        
        # Find cell
        path, metadata = find_cell(id)
        if not path:
            path, metadata = new_cell(id=id)

        log.debug('cell found', path=path, metadata=metadata)

        # Adjust properties
        change_properties(path=path, metadata=metadata, config=config)

        # Log measurements
        for cw in config.measurements:
            if config.pause_before_measure:
                input(f"Press Enter to begin measurement '{cw}' for cell '{id}' >")

            store_measurement(path=path, metadata=metadata, codeword=cw, config=config, timestamp = measurement_ts(config) if config.timestamp else None)

def store_as_property(property_path):
    class customAction(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            args.properties.append( (property_path, values) )
    return customAction

if __name__ == '__main__':

    # First add common arguments    
    parser = argparse.ArgumentParser(description='Log an action')
    parser.add_argument('-T', '--timestamp', const='now', nargs='?', help='Timestamp the log entry')
    parser.add_argument('--pause-before-cell', default=False, action='store_true', help='Pause for a keypress before each cell')
    parser.add_argument('--pause-before-measure', default=False, action='store_true', help='Pause for a keypress before each measurement')
    parser.add_argument('identifiers', nargs='*', default=['-'], help='Cell identifiers, read from stdin by default')

    # Cell nameplate information
    parser.add_argument('-b', '--brand', action=store_as_property('/brand'), help='Set cell brand')
    parser.add_argument('-m', '--model', action=store_as_property('/model'), help='Set cell model')
    parser.add_argument('-c', '--capacity', action=store_as_property('/capacity/nom'), help='Set cell nominal capacity in mAh')

    parser.add_argument('-t', '--tag', dest='tags', action='append', help='Tag cells')
    parser.add_argument('-p', '--property', nargs=2, dest='properties', default=[], action='append', help='Set a property for cells')

    load_plugins()

    # Then add arguments dependent on the loaded plugins
    parser.add_argument('-M', '--measure', choices=v1.measurements.keys(), default=[], action='append', dest='measurements', help='Measurement codewords')
    parser.add_argument('--rc3563-port', default=os.getenv('RC3563_PORT', '/dev/ttyUSB0'), help='Serial port connected to the RC3563 meter')
    parser.add_argument('--lii500-current-setting', choices=['500 mA', '1000 mA'], default='500 mA', help='Current setting of the Lii-500 charger')

    args = parser.parse_args()
    log.debug('config', args=args)

    main(config=args)