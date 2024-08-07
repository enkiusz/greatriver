#!/usr/bin/env python3

from secondlife.plugins.api import v1
from structlog import get_logger
import tabulate
import json
from collections import defaultdict
import structlog
import sys
import jq
import argparse

from secondlife.cli.utils import CompileJQAndAppend

log = structlog.get_logger()


class InfosetReport(object):

    def __init__(self, **kwargs):
        self.config = kwargs['config']
        self.log = get_logger(name=__class__.__name__)
        self.cells = defaultdict(list)
        self.sort_results = dict()
        if len(self.config.sort_queries) > 0:
            self.sort_queries = self.config.sort_queries
        else:
            self.sort_queries = [ jq.compile('.id') ]

    def process_cell(self, infoset):
        cell_id = infoset.fetch('.id')
        log = self.log.bind(id=cell_id)
        log.debug('processing cell')

        json_text = infoset.to_json(indent=2)
        self.sort_results[ cell_id ] = [ sort_query.input(text=json_text).first() for sort_query in self.sort_queries ]

        if len(self.config.infoset_queries) > 0:
            # Apply the jq queries if defined
            for query in self.config.infoset_queries:
                result = query.input(text=json_text).first()
                if result is None:
                    result = 'null'
                self.cells[ cell_id ].append( result )
                log.debug('jq query result', id=cell_id, result=result, query=query)
        else:
            self.cells[ cell_id ] = [ json_text ]

    def report(self, format='ascii'):
        if format != 'ascii':
            log.error('unknown report format', format=format)
            return

        if len(self.cells.items()) == 0:
            self.log.warning('no data')
            return

        if len(self.config.infoset_queries) > 0:
            print(
                tabulate.tabulate([ [id] + [ str(result) for result in self.cells[id] ] for id in sorted(self.cells.keys(), key=lambda key: self.sort_results[key]) ],  # noqa
                                  headers=['.id'] + [ query.program_string for query in self.config.infoset_queries ],
                                  tablefmt='fancy_grid')
            )
        else:
            for (id, item) in self.cells.items():
                print(f"=== Infoset for {id}")
                print(item[0])


def _config_group(parser):
    group = parser.add_argument_group('infoset report')
    group.add_argument('--sort-query', default=[], dest='sort_queries', action=CompileJQAndAppend,
        help='Select query used as sorting value')
    group.add_argument('--infoset-query', default=[], dest='infoset_queries', action=CompileJQAndAppend,
        help='Apply a JQ query to the infoset and print the result, use https://stedolan.github.io/jq/ syntax.')


v1.register_report(v1.Report('infoset', InfosetReport))
v1.register_config_group('infoset', _config_group)
