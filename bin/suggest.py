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

from xdg import XDG_CACHE_HOME
import pickle

from secondlife.plugins.api import v1, load_plugins
from secondlife.cli.utils import selected_cells, add_plugin_args, add_cell_selection_args, add_backend_selection_args
from secondlife.cli.utils import perform_measurement

# Reference: https://stackoverflow.com/a/49724281
LOG_LEVEL_NAMES = [logging.getLevelName(v) for v in
                   sorted(getattr(logging, '_levelToName', None) or logging._levelNames) if getattr(v, "real", 0)]

log = structlog.get_logger()


def main(config):

    cache_filename = XDG_CACHE_HOME / 'secondlife' / 'suggestion-cache' / 'cache.pickle'

    try:
        log.debug('loading cache', cache_filename=cache_filename)
        with open(cache_filename, 'rb') as f:
            cache_data = pickle.load(f)
        log.debug('cache loaded', cache_data=cache_data)
    except Exception as e:
        log.error('cannot load suggestion cache', cache_filename=cache_filename, _exc_info=e)
        sys.exit(1)

    if config.tag is not None:
        print('\n'.join([ tag for tag in cache_data['tags'] if tag.startswith(config.tag)]) )

    elif config.property_name is not None:
        print('\n'.join([ name for name in cache_data['prop_names'] if name.startswith(config.property_name)]) )

    elif config.brand is not None:
        print('\n'.join([ name for name in cache_data['brands'] if name.startswith(config.brand)]) )

    elif config.model is not None:
        print('\n'.join([ name for name in cache_data['models'] if name.startswith(config.model)]) )


if __name__ == '__main__':
    # Restrict log message to be above selected level
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr)
    )

    parser = argparse.ArgumentParser(description='Log an action')
    parser.add_argument('--loglevel', choices=LOG_LEVEL_NAMES, default='INFO', help='Change log level')

    # Cell nameplate information
    group = parser.add_argument_group('cell properties')
    group.add_argument('-b', '--brand', nargs='?', const='', help='Suggest a cell brand')
    group.add_argument('-m', '--model', nargs='?', const='', help='Suggest a cell model')
    group.add_argument('--property-name', nargs='?', const='', help='Suggest a property name')
    group.add_argument('--tag', nargs='?', const='', help='Suggest a tag')

    args = parser.parse_args()

    # Restrict log message to be above selected level
    structlog.configure( wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, args.loglevel)) )

    log.debug('config', args=args)

    main(config=args)
