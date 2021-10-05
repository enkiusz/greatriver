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

from secondlife.cli.utils import CompileJQ, CompileJQAndAppend

log = structlog.get_logger()


class GroupsReport(object):

    def __init__(self, **kwargs):
        self.config = kwargs['config']
        self.log = get_logger(name=__class__.__name__)
        self.cells = defaultdict(int)

    def process_cell(self, infoset):
        log = self.log.bind(id=infoset.fetch('.id'))
        log.debug('processing cell')

        k = []
        json_text = infoset.to_json(indent=2)

        for query in self.config.key_queries:
            result = query.input(text=json_text).text()
            k.append( result )
            log.debug('jq query result', id=infoset.fetch('.id'), result=result, query=query)

        self.cells[tuple(k)] += 1

    def report(self, format='ascii'):
        if format != 'ascii':
            log.error('unknown report format', format=format)
            return

        if len(self.cells.items()) == 0:
            self.log.warning('no data')
            return

        asciitable.write([ ([ group for group in key ] + [self.cells[key]]) for key in sorted(self.cells.keys()) ],
            names=[ query.program_string for query in self.config.key_queries ] + ['Count'],
            Writer=asciitable.FixedWidth)


def _config_group(parser):
    group = parser.add_argument_group('groups report')
    group.add_argument('--key-query', default=[], dest='key_queries', action=CompileJQAndAppend,
        help='Apply a JQ query as the group key, use https://stedolan.github.io/jq/ syntax.')


v1.register_report(v1.Report('groups', GroupsReport))
v1.register_config_group('groups', _config_group)
