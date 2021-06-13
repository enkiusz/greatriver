#!/usr/bin/env python3

# Allow module load from lib/python in main repo
import sys
from pathlib import Path
currentdir = Path(__file__).resolve(strict=True).parent
libdir = currentdir.parent.joinpath('lib/python')
sys.path.append(str(libdir))

import argparse
import logging
import structlog

from secondlife.plugins.api import v1, load_plugins
from secondlife.cli.utils import selected_cells, add_cell_selection_args, add_backend_selection_args

# Reference: https://stackoverflow.com/a/49724281
LOG_LEVEL_NAMES = [logging.getLevelName(v) for v in
                   sorted(getattr(logging, '_levelToName', None)
                          or logging._levelNames)
                   if getattr(v, "real", 0)]

log = structlog.get_logger()

def init(config):

    backend = v1.celldb_backends[args.backend](args.backend_dsn, config=args)
    backend.init()

def etl(config):

    src_backend = v1.celldb_backends[config.src_backend](dsn=config.src_dsn, config=config)
    dest_backend = v1.celldb_backends[config.dest_backend](dsn=config.dest_dsn, config=config)

    log.info('backends', source=src_backend, dest=dest_backend)

    for infoset in selected_cells(backend=src_backend, config=config):
        dest_backend.put(infoset)

if __name__ == '__main__':
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr)
    )    

    load_plugins()

    parser = argparse.ArgumentParser(description='Log an action')
    parser.add_argument('--loglevel', choices=LOG_LEVEL_NAMES, default='INFO', help='Change log level')
    subparsers = parser.add_subparsers(help='sub-command help')

    parser_init = subparsers.add_parser('init', help='Create a new celldb')
    parser_init.set_defaults(cmd=init)
    add_backend_selection_args(parser_init)
    
    parser_etl = subparsers.add_parser('etl', help='Migrate cells between databases')
    parser_etl.set_defaults(cmd=etl)    
    add_cell_selection_args(parser_etl)

    parser_etl.add_argument('--src-backend', choices=v1.celldb_backends.keys(), help='Source database backend')
    parser_etl.add_argument('--src-dsn', help='The source Data Source Name (URL)')
    parser_etl.add_argument('--dest-backend', choices=v1.celldb_backends.keys(), help='Destination database backend')
    parser_etl.add_argument('--dest-dsn', help='The destination Data Source Name (URL)')

    args = parser.parse_args()

    structlog.configure( wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, args.loglevel)) )

    log.debug('config', args=args)

    if hasattr(args, 'cmd'):
        args.cmd(args)
