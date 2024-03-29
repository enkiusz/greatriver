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
import os
import json
import logging
import structlog
import time

from secondlife.plugins.api import v1, load_plugins
from secondlife.cli.utils import selected_cells, add_plugin_args, add_cell_selection_args, add_backend_selection_args
from secondlife.cli.utils import perform_measurement

# Reference: https://stackoverflow.com/a/49724281
LOG_LEVEL_NAMES = [logging.getLevelName(v) for v in
                   sorted(getattr(logging, '_levelToName', None) or logging._levelNames) if getattr(v, "real", 0)]

log = structlog.get_logger()


def main(config):

    backend = v1.celldb_backends[args.backend](dsn=args.backend_dsn, config=args)

    if config.all_cells and not config.allow_unsafe:
        ack = input("Applying changes to all cells is a dangerous operation, please type 'yes' to continue: ")
        if ack != 'yes':
            return

    for infoset in selected_cells(config=config, backend=backend):
        id = infoset.fetch('.id')
        if config.pause_before_cell:
            input(f"Press Enter to begin handling cell '{id}' >")

        for prop in config.properties:
            # Check if manual entry of property value is requested
            if prop[1] == '%s':
                value = ''
                while len(value) == 0:
                    value = input(f'[{id}] {prop[0]} = ')
                infoset.put(prop[0], value)
            else:
                infoset.put(prop[0], prop[1])

        # Store arbitrary events
        for evt in config.events:
            e = json.loads(evt)
            e.update(dict(ts=time.time()))
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
                'ref': None,  # Content is directly stored, not referenced
                'content': extra_filename.read_bytes()
            })

        # Log measurements
        for cw in config.measurements:
            if config.pause_before_measure:
                input(f"Press Enter to begin measurement '{cw}' for cell '{id}' >")

            perform_measurement(infoset=infoset, codeword=cw, config=config)

        # Cleanup tags where value is false
        tags_to_remove = [ tag for (tag, v) in infoset.fetch('.props.tags', {}).items() if v is False ]
        for tag in tags_to_remove:
            del infoset.fetch('.props.tags')[tag]

        backend.put(infoset)

        # Move cell if requested
        if config.path is not None and (infoset.fetch('.path') != config.path):
            backend.move(id, config.path)


def store_as_property(property_path):
    class customAction(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            args.properties.append( (property_path, values) )
    return customAction


def add_as_tag(tags_path, value):
    class customAction(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            args.properties.append( (f'{tags_path}.{values}', value) )
    return customAction


def add_property(props_path):
    class customAction(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            name = values[0]
            value = values[1]

            if value[0] == '@':
                # Load complex value from file and parse it as JSON
                try:
                    with open(value[1:]) as f:
                        value = json.load(f)
                except Exception as e:
                    log.error('cannot load complex value', filename=value[1:], _exc_info=e)
                    sys.exit(1)

            args.properties.append( (f'{props_path}.{name}', value) )
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
    add_plugin_args(parser)
    add_backend_selection_args(parser)
    add_cell_selection_args(parser)

    parser.add_argument('--allow-unsafe', default=False, action='store_true',
                        help='Allow modification of all cells without confirmation')
    parser.add_argument('--pause-before-cell', default=False, action='store_true',
        help='Pause for a keypress before each cell')
    parser.add_argument('--pause-before-measure', default=False, action='store_true',
        help='Pause for a keypress before each measurement')

    # Cell nameplate information
    group = parser.add_argument_group('update cell properties')
    group.add_argument('-b', '--brand', action=store_as_property('.props.brand'), help='Set cell brand')
    group.add_argument('-m', '--model', action=store_as_property('.props.model'), help='Set cell model')
    group.add_argument('-c', '--capacity', action=store_as_property('.props.capacity.nom'),
        help='Set cell nominal capacity in mAh')

    group.add_argument('--path', default=os.getenv('CELLDB_PATH'), help='Set cell path')
    group.add_argument('-p', '--property', nargs=2, dest='properties', default=[], action=add_property('.props'),
        help='Set a property for cells, use @file.json to load a complex property value')
    group.add_argument('--add-tag', action=add_as_tag('.props.tags', value=True), help='Add a tag')
    group.add_argument('--del-tag', action=add_as_tag('.props.tags', value=False), help='Remove a tag')
    group.add_argument('--extra-file', default=[], dest='extra_files', action='append',
        help='Import extra data from a file')

    group = parser.add_argument_group('update cell log')
    group.add_argument('-M', '--measure', choices=v1.measurements.keys(), default=[], action='append',
        dest='measurements', help='Take measurements with the specified codewords')
    group.add_argument('--event', dest='events', metavar='JSON', default=[], action='append',
        help='Store arbitrary events in the log')

    # Then add argument configuration argument groups dependent on the loaded plugins, include only:
    # - measurement plugins
    # - state var plugins
    # - celldb backend plugins
    included_plugins = v1.measurements.keys() | v1.state_vars.keys() | v1.celldb_backends.keys()
    for codeword in filter(lambda codeword: codeword in v1.config_groups.keys(), included_plugins):
        v1.config_groups[codeword](parser)

    args = parser.parse_args()

    # Restrict log message to be above selected level
    structlog.configure( wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, args.loglevel)) )

    log.debug('config', args=args)

    main(config=args)
