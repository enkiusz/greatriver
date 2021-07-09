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
from secondlife.cli.utils import selected_cells, add_cell_selection_args, add_backend_selection_args
from secondlife.cli.utils import event_ts, perform_measurement

# Reference: https://stackoverflow.com/a/49724281
LOG_LEVEL_NAMES = [logging.getLevelName(v) for v in
                   sorted(getattr(logging, '_levelToName', None)
                          or logging._levelNames)
                   if getattr(v, "real", 0)]

log = structlog.get_logger()

def main(config):

    backend = v1.celldb_backends[args.backend](dsn=args.backend_dsn, config=args)

    for infoset in selected_cells(config=config, backend=backend):
        id = infoset.fetch('.id')
        if config.pause_before_cell:
            input(f"Press Enter to begin handling cell '{id}' >")

        for prop in config.properties:
            infoset.put(prop[0], prop[1])

        # Store arbitrary events
        for evt in config.events:
            e = json.loads(evt)
            if config.timestamp:
                e.update(dict(ts=event_ts(config)))
            infoset.fetch('.log').append(e)

        # Import extra files
        for extra_filename in [ Path(f) for f in config.extra_files ]:

            infoset.fetch('.extra').append({
                'name': extra_filename.name,
                'props': {
                    'stat': {
                        'ctime': extra_filename.stat().st_ctime,
                        'mtime': extra_filename.stat().st_mtime
                    }
                },
                'ref': None, # Content is directly stored, not referenced
                'content': extra_filename.read_bytes()
            })

        # Log measurements
        for cw in config.measurements:
            if config.pause_before_measure:
                input(f"Press Enter to begin measurement '{cw}' for cell '{id}' >")

            perform_measurement(infoset=infoset, codeword=cw, config=config, timestamp = event_ts(config) if config.timestamp else None)

        backend.put(infoset)

def store_as_property(property_path):
    class customAction(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            args.properties.append( (property_path, values) )
    return customAction

if __name__ == '__main__':
    # Restrict log message to be above selected level
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr)
    )

    load_plugins()

    parser = argparse.ArgumentParser(description='Log an action')
    parser.add_argument('--loglevel', choices=LOG_LEVEL_NAMES, default='INFO', help='Change log level')
    add_cell_selection_args(parser)
    add_backend_selection_args(parser)

    parser.add_argument('-T', '--timestamp', const='now', nargs='?', help='Timestamp the log entry')
    parser.add_argument('--pause-before-cell', default=False, action='store_true', help='Pause for a keypress before each cell')
    parser.add_argument('--pause-before-measure', default=False, action='store_true', help='Pause for a keypress before each measurement')

    # Cell nameplate information
    parser.add_argument('-b', '--brand', action=store_as_property('.props.brand'), help='Set cell brand')
    parser.add_argument('-m', '--model', action=store_as_property('.props.model'), help='Set cell model')
    parser.add_argument('-c', '--capacity', action=store_as_property('.capacity.nom'), help='Set cell nominal capacity in mAh')

    parser.add_argument('--path', default=os.getenv('CELLDB_PATH'), action=store_as_property('.path'), help='Set cell path')
    parser.add_argument('-p', '--property', nargs=2, dest='properties', default=[], action='append', help='Set a property for cells')
    parser.add_argument('--extra-file', default=[], dest='extra_files', action='append', help='Import extra data from a file')

    # Then add arguments dependent on the loaded plugins
    parser.add_argument('-M', '--measure', choices=v1.measurements.keys(), default=[], action='append', dest='measurements', help='Take measurements with the specified codewords')
    parser.add_argument('--event', dest='events', metavar='JSON', default=[], action='append', help='Store arbitrary events in the log')
    parser.add_argument('--rc3563-port', default=os.getenv('RC3563_PORT', '/dev/ttyUSB0'), help='Serial port connected to the RC3563 meter')
    parser.add_argument('--lii500-port', default=os.getenv('LII500_PORT', None), help='Serial port used by the Lii-500 charger USB interface')
    parser.add_argument('--lii500-current-setting', choices=['300mA', '500 mA', '700 mA', '1000 mA'], default='500 mA', help='Current setting of the Lii-500 charger')
    parser.add_argument('--lii500-select', default=None, metavar='ID', help='Select the specified charger from the ports file')
    parser.add_argument('--lii500-ports-file', default=os.getenv('LII500_PORTS_FILE', None), help='The file specifying serial ports for particular chargers')

    args = parser.parse_args()

    # Restrict log message to be above selected level
    structlog.configure( wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, args.loglevel)) )

    log.debug('config', args=args)

    main(config=args)