#!/usr/bin/env python3

import parsedatetime
import time
import sys
from structlog import get_logger
from pathlib import Path
from secondlife.celldb import find_cell, load_metadata, new_cell

log = get_logger()

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

def include_cell(path, metadata, config):
    # Check if cell is to be included based on configured criteria

    if config.tags <= metadata.get('/tags', default=set()):
        return True
    else:
        return False

    return True

def selected_cells(config):

    if config.all_cells:
        path = Path()
        log.info('searching for cells', path=path)

        # Now look in subdirectories
        for path in path.glob('**/meta.json'):
            try:
                metadata = load_metadata(path)
                if metadata.get('/id'):
                    log.debug('cell found', id=metadata.get('/id'), path=path, meatadata=metadata)
                    if include_cell(path, metadata, config=config):
                        yield (path, metadata)
            except Exception as e:
                log.error('cannot load metadata', path=path, _exc_info=e)

    for id in cell_identifiers(config=config):

        # Find cell
        path, metadata = find_cell(id)
        if not path:
            path, metadata = new_cell(id=line)

        log.debug('cell found', id=metadata.get('/id'), path=path, meatadata=metadata)
        if include_cell(path, metadata, config=config):
            yield (path, metadata)

def measurement_ts(config):
    # Parse the timestamp argument
    cal = parsedatetime.Calendar()
    time_parsed, context = cal.parse(config.timestamp, version=parsedatetime.VERSION_CONTEXT_STYLE)
    log.debug('parsed timestamp', argument=config.timestamp, time_parsed=time_parsed, context=context)

    if not context.hasDate and context != parsedatetime.pdtContext(accuracy=parsedatetime.pdtContext.ACU_NOW):
        log.fatal('no date in timestamp', parsed=time_parsed, pdt_context=context)
        sys.exit(1)

    return time.mktime(time_parsed)

import argparse
class AddSet(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        getattr(namespace, self.dest).add(values)
