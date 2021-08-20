#!/usr/bin/env python3

from secondlife.plugins.api import v1
from structlog import get_logger
import asciitable
import json

from secondlife.cli.utils import CompileJQ

class InfosetReport(object):

    def __init__(self, **kwargs):
        self.config = kwargs['config']
        self.log = get_logger(name=__class__.__name__)
        self.cells = dict()

    def process_cell(self, infoset):
        log = self.log.bind(id=infoset.fetch('.id'))
        log.debug('processing cell')

        json_text = infoset.to_json(indent=2)

        if self.config.infoset_query:
            # Apply the jq query if defined
            json_text = self.config.infoset_query.input(text=json_text).text()
            log.debug('jq query result', id=infoset.fetch('.id'), result=json_text, query=self.config.infoset_query)

        self.cells[infoset.fetch('.id')] = json_text

    def report(self, format='ascii'):
        if format == 'ascii':
            if len(self.cells.items()) > 0:
                for (id, infoset) in self.cells.items():
                    print(f"=== Infoset for {id}")
                    print(infoset)
            else:
                self.log.warning('no data')
        else:
            log.error('unknown report format', format=format)

def _config_group(parser):
    group = parser.add_argument_group('infoset report')
    group.add_argument('--infoset-query', action=CompileJQ, help='Apply a JQ query to the infoset and print the result, use https://stedolan.github.io/jq/ syntax.')

v1.register_report(v1.Report('infoset', InfosetReport))
v1.register_config_group('infoset', _config_group)
