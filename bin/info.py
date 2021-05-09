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

# Reference: https://stackoverflow.com/a/49724281
LOG_LEVEL_NAMES = [logging.getLevelName(v) for v in
                   sorted(getattr(logging, '_levelToName', None)
                          or logging._levelNames)
                   if getattr(v, "real", 0)]

log = structlog.get_logger()


from secondlife.cli.utils import selected_cells, AddSet
from secondlife.plugins.api import v1, load_plugins


def main(config):
    
    if len(config.reports) == 0:
        log.info('nothing to do')
        return

    # Build objects for all reports
    reports = [ v1.reports[codeword].handler_class(config=config) for codeword in config.reports ]

    for (path, metadata) in selected_cells(config=config):
        for report in reports:
            report.process_cell(path=path, metadata=metadata)

    for report in reports:
        report.report()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Report on cells')
    parser.add_argument('--loglevel', choices=LOG_LEVEL_NAMES, default='INFO', help='Change log level')
    parser.add_argument('--all', '-a', default=False, action='store_true', dest='all_cells', help='Process all cells')
    parser.add_argument('identifiers', nargs='*', default=[], help='Cell identifiers, use - to read from stdin')
    parser.add_argument('--tag', '-T', dest='tags', action=AddSet, default=set(), help='Filter cells based on tags, all specified tags need to be present')

    load_plugins() # Needed here to populate v1.reports dict

    # Then add arguments dependent on the loaded plugins
    parser.add_argument('-R', '--report', choices=v1.reports.keys(), default=[], action='append', dest='reports', help='Report codewords')

    args = parser.parse_args()

    # Restrict log message to be above selected level
    structlog.configure( wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, args.loglevel)) )

    log.debug('config', args=args)

    main(config=args)

