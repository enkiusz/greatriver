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
from xdg import XDG_CACHE_HOME
import pickle

from secondlife.plugins.api import v1, load_plugins
from secondlife.cli.utils import selected_cells, add_plugin_args, add_cell_selection_args, add_backend_selection_args

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
        for codeword in config.infoset_transforms:
            infoset = v1.infoset_transforms[codeword](infoset, config)

        dest_backend.put(infoset)

def suggest(config):
    log.info('suggest', action=config.action)
    if config.action == 'create':
        backend = v1.celldb_backends[args.backend](args.backend_dsn, config=args)
        
        cache_filename = XDG_CACHE_HOME / 'secondlife' / 'suggestion-cache' / 'cache.pickle'
        
        tags = set()
        prop_names = set()
        brands = set()
        models = set()

        for infoset in selected_cells(config=config, backend=backend):
            tags.update(infoset.fetch('.props.tags', []))

            if infoset.fetch('.props.brand'):
                brands.add(infoset.fetch('.props.brand'))

            if infoset.fetch('.props.model'):
                models.add(infoset.fetch('.props.model'))

            # Select property names excluding the following:
            # tags - these are handled seprately above
            # brand and model - these are handled separetely above
            # the version key - this is set by the cell db backend and cannot be manipulated directly
            #
            prop_paths = filter(lambda path: path.startswith('.props.') and 
                not path.startswith('.props.tags.') and 
                not path in ('.props.v', '.props.brand', '.props.model'), infoset.paths())
            prop_names.update( map(lambda path: path[7:], prop_paths) )
            

        cache_filename.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_filename, 'wb') as f:
            log.debug('storing cache', cache_filename=cache_filename)
            pickle.dump(dict(tags=tags, prop_names=prop_names, brands=brands, models=models), f, pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr)
    )    

    load_plugins()

    parser = argparse.ArgumentParser(description='Celldb-wide tasks')
    parser.add_argument('--loglevel', choices=LOG_LEVEL_NAMES, default='INFO', help='Change log level')
    add_plugin_args(parser)

    subparsers = parser.add_subparsers(help='sub-command help')

    parser_init = subparsers.add_parser('init', help='Create a new celldb')
    parser_init.set_defaults(cmd=init)
    add_backend_selection_args(parser_init)

    # Then add argument configuration argument groups dependent on the loaded plugins, include only:
    # - celldb backend plugins
    included_plugins = v1.celldb_backends.keys()
    for codeword in filter(lambda codeword: codeword in v1.config_groups.keys(), included_plugins):
        v1.config_groups[codeword](parser_init)

    parser_etl = subparsers.add_parser('etl', help='Migrate cells between databases')
    parser_etl.set_defaults(cmd=etl)    

    group = parser_etl.add_argument_group('source backend')
    group.add_argument('--src-backend', choices=v1.celldb_backends.keys(), help='Source database backend')
    group.add_argument('--src-dsn', help='The source Data Source Name (URL)')

    add_cell_selection_args(parser_etl)

    group = parser_etl.add_argument_group('transforms')
    group.add_argument('-T', '--transform', choices=v1.infoset_transforms.keys(), default=["copy"], action='append', dest='infoset_transforms', help='Apply the specified transforms (in order specified)')

    group = parser_etl.add_argument_group('destination backend')
    group.add_argument('--dest-backend', choices=v1.celldb_backends.keys(), help='Destination database backend')
    group.add_argument('--dest-dsn', help='The destination Data Source Name (URL)')

    # Then add argument configuration argument groups dependent on the loaded plugins, include only:
    # - state var plugins
    # - celldb backend plugins
    # - infoset tranform plugins
    included_plugins = v1.state_vars.keys() | v1.celldb_backends.keys() | v1.infoset_transforms.keys()
    for codeword in filter(lambda codeword: codeword in v1.config_groups.keys(), included_plugins):
        v1.config_groups[codeword](parser_etl)


    parser_suggest = subparsers.add_parser('suggest', help='Manage suggestion cache')
    parser_suggest.set_defaults(cmd=suggest)

    add_backend_selection_args(parser_suggest)
    add_cell_selection_args(parser_suggest)

    parser_suggest.add_argument('-A', '--action', choices=['create'], help='Specify action to perform on the suggestion cache')

    # Then add argument configuration argument groups dependent on the loaded plugins, include only:
    # - celldb backend plugins
    included_plugins = v1.celldb_backends.keys()
    for codeword in filter(lambda codeword: codeword in v1.config_groups.keys(), included_plugins):
        v1.config_groups[codeword](parser_suggest)

    args = parser.parse_args()

    structlog.configure( wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, args.loglevel)) )

    log.debug('config', args=args)

    if hasattr(args, 'cmd'):
        args.cmd(args)
