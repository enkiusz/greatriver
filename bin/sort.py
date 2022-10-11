#!/usr/bin/env python3

# Python 3.9 is needed to load additional plugins as the code uses
# https://docs.python.org/3/library/pkgutil.html#pkgutil.resolve_name

# Allow module load from lib/python in main repo
import sys
from pathlib import Path

currentdir = Path(__file__).resolve(strict=True).parent
libdir = currentdir.parent.joinpath('lib/python')
sys.path.append(str(libdir))

import argparse
import logging
import structlog
import time
import serial

# Reference: https://stackoverflow.com/a/49724281
LOG_LEVEL_NAMES = [logging.getLevelName(v) for v in
                   sorted(getattr(logging, '_levelToName', None) or logging._levelNames) if getattr(v, "real", 0)]

log = structlog.get_logger()

from secondlife.cli.utils import add_plugin_args, cell_identifiers
from secondlife.cli.utils import add_cell_selection_args, add_backend_selection_args
from secondlife.plugins.api import v1, load_plugins


buckets = [ 'BUCKET~0', 'BUCKET~1' ]

slots = [ None, None ]


def target_bucket(config, cell):
    if cell.fetch('.id') == 'C~7221726799':
        return 'BUCKET~1'
    elif cell.fetch('.id') == 'C~5195400019':
        return 'BUCKET~0'
    else:
        return None


def cmd_sort(config):
    backend = v1.celldb_backends[args.backend](dsn=args.backend_dsn, config=args)
    with serial.serial_for_url(config.tumbler_port) as ser:

        for id in cell_identifiers(config=config):

            # Find cell
            infoset = backend.fetch(id)
            if not infoset:
                log.error('cell not found', id=id)
                sys.exit(1)

            bkt = target_bucket(config, infoset)
            log.debug('bucket', cell_id=id, bucket=bkt)

            slots[0] = id  # Cell always starts as the first (highest) slot

            while len(list(filter(lambda s: s is not None, slots))) > 0:

                for (idx, cell) in reversed(list(enumerate(slots))):
                    if cell is None:  # Nothing to be done if there is no cell in slot
                        continue

                    if bkt == buckets[idx]:  # The bucket matches, drop cell
                        log.info('dropping', cell_id=id, slot=idx, bucket=bkt)
                        ser.write(f'mov {idx} drop\n'.encode('ascii'))
                        time.sleep(1)
                        ser.write(f'mov {idx} idle\n'.encode('ascii'))

                        slots[idx] = None

                    else:  # The bucket doesn't match, pass cell to lower slot
                        ser.write(f'mov {idx} pass\n'.encode('ascii'))
                        time.sleep(1)
                        ser.write(f'mov {idx} idle\n'.encode('ascii'))

                        if idx < len(slots)-1:
                            log.info('passing on', cell_id=id, slot=idx, new_slot=idx+1)
                            slots[idx + 1] = slots[idx]
                        else:
                            log.info('no bucket', cell_id=id, slot=idx)

                        slots[idx] = None


if __name__ == "__main__":
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr)
    )
    load_plugins()

    parser = argparse.ArgumentParser(description='Sort cells using a cell-tumbler')
    parser.add_argument('--loglevel', choices=LOG_LEVEL_NAMES, default='INFO', help='Change log level')
    parser.add_argument('--tumbler-port', required=True, help='The serial port connected to the tumbler')

    add_plugin_args(parser)

    # Then add argument configuration argument groups dependent on the loaded plugins, include only:
    # - state var plugins
    # - celldb backend plugins
    included_plugins = v1.state_vars.keys() | v1.celldb_backends.keys()
    for codeword in filter(lambda codeword: codeword in v1.config_groups.keys(), included_plugins):
        v1.config_groups[codeword](parser)

    add_backend_selection_args(parser)
    add_cell_selection_args(parser)

    args = parser.parse_args()

    # Restrict log message to be above selected level
    structlog.configure( wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, args.loglevel)) )

    log.debug('config', args=args)

    cmd_sort(config=args)
