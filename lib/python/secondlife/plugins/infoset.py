#!/usr/bin/env python3

from secondlife.plugins.api import v1
from structlog import get_logger
import asciitable
import json
from collections import defaultdict
import structlog
import sys
import jq
import argparse

from secondlife.cli.utils import CompileJQ

log = structlog.get_logger()

class InfosetReport(object):

    def __init__(self, **kwargs):
        self.config = kwargs['config']
        self.log = get_logger(name=__class__.__name__)
        self.cells = defaultdict(list)

    def process_cell(self, infoset):
        log = self.log.bind(id=infoset.fetch('.id'))
        log.debug('processing cell')

        json_text = infoset.to_json(indent=2)

        if len(self.config.infoset_queries) > 0:
            # Apply the jq queries if defined
            for query in self.config.infoset_queries:
                result = query.input(text=json_text).text()
                self.cells[infoset.fetch('.id')].append( result )
                log.debug('jq query result', id=infoset.fetch('.id'), result=result, query=query)
        else:
            self.cells[infoset.fetch('.id')] = [ json_text ]

    def report(self, format='ascii'):
        if format != 'ascii':
            log.error('unknown report format', format=format)
            return

        if len(self.cells.items()) == 0:
            self.log.warning('no data')
            return

        if len(self.config.infoset_queries) > 0:
            asciitable.write([ [id] + [ result for result in self.cells[id] ] for id in self.cells.keys() ],
                names=['Cell ID'] + [ query.program_string for query in self.config.infoset_queries ],
                formats={ 'Cell ID': '%s' },
                Writer=asciitable.FixedWidth)
        else:
            for (id, item) in self.cells.items():
                print(f"=== Infoset for {id}")
                print(item[0])

class CompileJQAndAppend(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        try:
            getattr(namespace, self.dest).append(jq.compile(values))
        except Exception as e:
            log.error('cannot compile query', query=values, _exc_info=e)
            sys.exit(1)

def _config_group(parser):
    group = parser.add_argument_group('infoset report')
    group.add_argument('--infoset-query', default=[], dest='infoset_queries', action=CompileJQAndAppend, help='Apply a JQ query to the infoset and print the result, use https://stedolan.github.io/jq/ syntax.')

v1.register_report(v1.Report('infoset', InfosetReport))
v1.register_config_group('infoset', _config_group)
