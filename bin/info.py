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
import jq
import pkgutil

# Reference: https://stackoverflow.com/a/49724281
LOG_LEVEL_NAMES = [logging.getLevelName(v) for v in
                   sorted(getattr(logging, '_levelToName', None)
                          or logging._levelNames)
                   if getattr(v, "real", 0)]

log = structlog.get_logger()


from secondlife.cli.utils import selected_cells, add_cell_selection_args, add_backend_selection_args
from secondlife.plugins.api import v1, load_plugins


def main(config):
    
    if len(config.reports) == 0:
        log.info('nothing to do')
        return

    backend = v1.celldb_backends[args.backend](dsn=args.backend_dsn, config=args)

    # Build objects for all reports
    reports = [ v1.reports[codeword].handler_class(config=config) for codeword in config.reports ]

    for infoset in selected_cells(config=config, backend=backend):
        for report in reports:
            report.process_cell(infoset=infoset)

    for report in reports:
        report.report()

class load_more_plugins(argparse.Action):
    def __call__(self, parser, args, values, option_string=None):
        load_plugins(pkgutil.resolve_name(values))

if __name__ == "__main__":
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr)
    )

    load_plugins()

    parser = argparse.ArgumentParser(description='Report on cells')
    parser.add_argument('--loglevel', choices=LOG_LEVEL_NAMES, default='INFO', help='Change log level')
    parser.add_argument('--plugin-namespace', metavar='NAMESPACE', action=load_more_plugins, help='Load plugins from the specified namespace')

    add_cell_selection_args(parser)
    add_backend_selection_args(parser)

    # Then add arguments dependent on the loaded plugins
    parser.add_argument('-R', '--report', choices=v1.reports.keys(), action='append', dest='reports', help='Report codewords')

    args = parser.parse_args()

    if args.reports is None: # Set default reports only if none provided
        args.reports = [ rep.codeword for rep in v1.reports.values() if rep.default_enable ]

    # Restrict log message to be above selected level
    structlog.configure( wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, args.loglevel)) )

    log.debug('config', args=args)

    main(config=args)

