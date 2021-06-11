#!/usr/bin/env python3

# Allow module load from lib/python in main repo
import sys
from pathlib import Path
currentdir = Path(__file__).resolve(strict=True).parent
libdir = currentdir.parent.joinpath('lib/python')
sys.path.append(str(libdir))

import argparse
import os
import json
import logging
import structlog

from secondlife.plugins.api import v1, load_plugins
from secondlife.cli.utils import selected_cells, add_cell_selection_args
from secondlife.cli.utils import event_ts, change_properties, perform_measurement

# Reference: https://stackoverflow.com/a/49724281
LOG_LEVEL_NAMES = [logging.getLevelName(v) for v in
                   sorted(getattr(logging, '_levelToName', None)
                          or logging._levelNames)
                   if getattr(v, "real", 0)]

log = structlog.get_logger()

def main(config):

    for infoset in selected_cells(config=config):
        id = infoset.fetch('.props.id')
        if config.pause_before_cell:
            input(f"Press Enter to begin handling cell '{id}' >")

        # Adjust properties
        change_properties(infoset=infoset, config=config)

        # Log measurements
        for cw in config.measurements:
            if config.pause_before_measure:
                input(f"Press Enter to begin measurement '{cw}' for cell '{id}' >")

            perform_measurement(infoset=infoset, codeword=cw, config=config, timestamp = event_ts(config) if config.timestamp else None)

def store_as_property(property_path):
    class customAction(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            args.properties.append( (property_path, values) )
    return customAction

if __name__ == '__main__':
    load_plugins()

    parser = argparse.ArgumentParser(description='Log an action')
    parser.add_argument('--loglevel', choices=LOG_LEVEL_NAMES, default='INFO', help='Change log level')
    add_cell_selection_args(parser)

    parser.add_argument('-T', '--timestamp', const='now', nargs='?', help='Timestamp the log entry')
    parser.add_argument('--pause-before-cell', default=False, action='store_true', help='Pause for a keypress before each cell')
    parser.add_argument('--pause-before-measure', default=False, action='store_true', help='Pause for a keypress before each measurement')

    # Cell nameplate information
    parser.add_argument('-b', '--brand', action=store_as_property('.props.brand'), help='Set cell brand')
    parser.add_argument('-m', '--model', action=store_as_property('.props.model'), help='Set cell model')
    parser.add_argument('-c', '--capacity', action=store_as_property('.capacity.nom'), help='Set cell nominal capacity in mAh')

    parser.add_argument('-p', '--property', nargs=2, dest='properties', default=[], action='append', help='Set a property for cells')

    # Then add arguments dependent on the loaded plugins
    parser.add_argument('-M', '--measure', choices=v1.measurements.keys(), default=[], action='append', dest='measurements', help='Take measurements with the specified codewords')
    parser.add_argument('--event', dest='events', metavar='JSON', default=[], action='append', help='Store arbitrary events in the log')
    parser.add_argument('--rc3563-port', default=os.getenv('RC3563_PORT', '/dev/ttyUSB0'), help='Serial port connected to the RC3563 meter')
    parser.add_argument('--lii500-current-setting', choices=['500 mA', '1000 mA'], default='500 mA', help='Current setting of the Lii-500 charger')

    args = parser.parse_args()

    args.backend = v1.celldb_backends[args.backend](config=args)

    # Restrict log message to be above selected level
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, args.loglevel)),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr)
    )

    log.debug('config', args=args)

    main(config=args)