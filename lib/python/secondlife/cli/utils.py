#!/usr/bin/env python3

import time
import sys
from structlog import get_logger
from pathlib import Path
import jq
import argparse
import random
import json
import string
import os
import pkgutil

from secondlife.plugins.api import v1, load_plugins

log = get_logger()


def generate_id(prefix, k=10):
    return f"{prefix}~{''.join(random.choices(string.digits, k=k))}"


def cell_identifiers(config):

    for id in config.identifiers:
        if id == '-':
            for line in sys.stdin:
                line = line.strip()
                if len(line) == 0:
                    continue

                yield line
        else:
            yield id


def include_cell(infoset, config):
    # Check if cell is to be included based on configured criteria

    if config.jq_query:

        # The jq should return only a single value, use first() to get it
        res = config.jq_query.input(text=infoset.to_json()).first()
        log.debug('jq query result', id=infoset.fetch('.id'), result=res, query=config.jq_query)

        if res is not True:
            return False

    return True


def selected_cells(config, backend):
    cells_found_total = 0
    last_progress_report = time.time()

    if config.all_cells:
        log.info('searching for cells')

        for infoset in backend.find():
            cells_found_total += 1
            if cells_found_total % 1000 == 0 or time.time() - last_progress_report >= 2:
                last_progress_report = time.time()
                log.info('progress', cells_found_total=cells_found_total)

            if include_cell(infoset, config=config):
                yield infoset

    for id in cell_identifiers(config=config):

        # Find cell
        infoset = backend.fetch(id)
        if not infoset:
            if config.autocreate is True:
                infoset = backend.create(id=id, path=getattr(config, 'path', '/'))

                backend.put(infoset)

            else:
                log.error('cell not found', id=id)
                sys.exit(1)

        if infoset.fetch('.id'):
            log.info('cell found', id=id)

            # Progress report every 1000 cells or 2 seconds
            cells_found_total += 1
            if cells_found_total % 1000 == 0 or time.time() - last_progress_report >= 2:
                last_progress_report = time.time()
                log.info('progress', cells_found_total=cells_found_total)

            if include_cell(infoset, config=config):
                yield infoset

    # Final progress report
    log.info('progress', cells_found_total=cells_found_total)


def perform_measurement(infoset, codeword, config):
    log.info('measurement start', id=infoset.fetch('.id'), codeword=codeword)

    handler = v1.measurements[codeword].handler_class(config=config)

    m = handler.measure(config)
    if m:
        log.info('store measurement results', id=infoset.fetch('.id'), codeword=codeword, results=m)
        infoset.fetch('.log').append(m)
    else:
        log.error("measurement unsuccessful", id=infoset.fetch('.id'), codeword=codeword)


class CompileJQ(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        try:
            setattr(namespace, self.dest, jq.compile(values))
        except Exception as e:
            log.error('cannot compile query', query=values, _exc_info=e)
            sys.exit(1)


# Add arguments which are used by the selected_cells() function
def add_cell_selection_args(parser):
    group = parser.add_argument_group('cell selection')
    group.add_argument('--autocreate', default=False, action='store_true', help='Create cell IDs that are selected but not found')
    group.add_argument('--all', '-a', default=False, action='store_true', dest='all_cells', help='Process all cells')
    group.add_argument('--match', dest='jq_query', action=CompileJQ,
        help='Filter cells based on infoset content, use https://stedolan.github.io/jq/ syntax. \
            Matches when a "true" string is returned as a single output')
    group.add_argument('identifiers', nargs='*', default=[],
        help='Cell identifiers, use - to read from standard input')


def add_backend_selection_args(parser):
    group = parser.add_argument_group('backend selection')
    group.add_argument('--backend', default=os.getenv('CELLDB_BACKEND', 'json-files'), choices=v1.celldb_backends.keys(), help='Celldb backend')
    group.add_argument('--backend-dsn', default=os.getenv('CELLDB_BACKEND_DSN', None), help='The Data Source Name (URL)')


class load_more_plugins(argparse.Action):
    def __call__(self, parser, args, values, option_string=None):
        load_plugins(pkgutil.resolve_name(values))


def add_plugin_args(parser):
    group = parser.add_argument_group('plugins')
    group.add_argument('--plugin-namespace', metavar='NAMESPACE', action=load_more_plugins,
        help='Load plugins from the specified namespace')
