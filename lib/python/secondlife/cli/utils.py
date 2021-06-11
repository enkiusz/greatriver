#!/usr/bin/env python3

import parsedatetime
import time
import sys
from structlog import get_logger
from pathlib import Path
import jq
import argparse
import random
import json
import string 
    
from secondlife.plugins.api import v1

log = get_logger()

def generate_id(prefix, k=10):
    return f"{prefix}~{''.join(random.choices(string.digits, k=10))}"

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
        log.debug('jq query result', id=infoset.fetch('.props.id'), result=res, query=config.jq_query)

        if not res is True:
            return False

    return True

def selected_cells(config):
    cells_found_total = 0
    last_progress_report = time.time()

    if config.all_cells:
        log.info('searching for cells')

        for infoset in config.backend.find():
            yield infoset

    for id in cell_identifiers(config=config):

        # Find cell
        infoset = config.backend.fetch(id)
        if not infoset:
            if config.autocreate is True:
                infoset = config.backend.create(id=id)
            else:
                log.error('cell not found', id=id)
                sys.exit(1)

        if infoset.fetch('.props.id'):
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

def event_ts(config):
    # Parse the timestamp argument
    cal = parsedatetime.Calendar()
    time_parsed, context = cal.parse(config.timestamp, version=parsedatetime.VERSION_CONTEXT_STYLE)
    log.debug('parsed timestamp', argument=config.timestamp, time_parsed=time_parsed, context=context)

    if not context.hasDate and context != parsedatetime.pdtContext(accuracy=parsedatetime.pdtContext.ACU_NOW):
        log.fatal('no date in timestamp', parsed=time_parsed, pdt_context=context)
        sys.exit(1)

    return time.mktime(time_parsed)

def change_properties(infoset, config):
    global log

    for prop in config.properties:
        infoset.put(prop[0], prop[1])

    # Store arbitrary events
    for evt in config.events:
        e = json.loads(evt)
        if config.timestamp:
            e.update(dict(ts=event_ts(config)))
        infoset.fetch('.log').append(e)

    config.backend.put(infoset)

def perform_measurement(infoset, codeword, config, timestamp=None):
    log.info('measurement start', id=infoset.fetch('.props.id'), codeword=codeword)

    handler = v1.measurements[codeword].handler_class(config=config)

    m = handler.measure(config)
    if m:
        if timestamp and 'ts' not in m:
            m['ts'] = timestamp

        log.info('store measurement results', id=infoset.fetch('.props.id'), codeword=codeword, results=m)
        infoset.fetch('.log').append(m)
    else:
        log.error("measurement unsuccessful", id=infoset.fetch('.props.id'), codeword=codeword)

class AddSet(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        getattr(namespace, self.dest).add(values)

class CompileJQ(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        try:
            setattr(namespace, self.dest, jq.compile(values))
        except Exception as e:
            log.error('cannot compile query', query=values, _exc_info=e)
            sys.exit(1)

# Add arguments which are used by the selected_cells() function
def add_cell_selection_args(parser):
    parser.add_argument('--backend', default='json-files', choices=v1.celldb_backends.keys(), help='Select the celldb backend to use')
    parser.add_argument('--autocreate', default=False, action='store_true', help='Create cell IDs that are given but not found')
    parser.add_argument('--all', '-a', default=False, action='store_true', dest='all_cells', help='Process all cells')
    parser.add_argument('identifiers', nargs='*', default=[], help='Cell identifiers, specify - to read from standard input')
    parser.add_argument('--match', dest='jq_query', action=CompileJQ, help='Filter cells based on infoset content, use https://stedolan.github.io/jq/ syntax. Matches when a "true" string is returned as a single output')