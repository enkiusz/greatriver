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

log = structlog.get_logger()


def _check_log_units(log):
    for entry in log:
        if 'results' in entry:
            for result in entry['results'].values():
                if hasattr(result, 'keys'):
                    if 'unit' in result:
                        return False
    return True


def _check_log_ts(log):
    for entry in log:
        if 'ts' not in entry:
            return False
    return True


def _check_log_event(log):
    for entry in log:
        if 'event' not in entry:
            return False
    return True


# Each check returns True on OK and False on FAIL
checks = {
    'null_brand_model': lambda infoset: not (
        infoset.fetch('.props.brand') is None and infoset.fetch('.props.model') is None and infoset.fetch('.props.tags.noname') is not True
    ),
    'only_brand': lambda infoset: not (
        infoset.fetch('.props.brand') is not None and infoset.fetch('.props.model') is None and infoset.fetch('.props.tags.likely_fake') is not True
    ),
    'unit_instead_of_u': lambda infoset: _check_log_units(infoset.fetch('.log')),
    'log_entries_without_ts': lambda infoset: _check_log_ts(infoset.fetch('.log')),
    'log_entries_without_event': lambda infoset: _check_log_event(infoset.fetch('.log')),
}


class CheckerReport(object):

    def __init__(self, **kwargs):
        self.config = kwargs['config']
        self.log = get_logger(name=__class__.__name__)
        self.cells = defaultdict(list)
        self.codewords = self.config.checker_codewords

        if self.codewords is None:
            self.codewords = checks.keys()

    def process_cell(self, infoset):
        cell_id = infoset.fetch('.id')
        log = self.log.bind(id=cell_id)
        log.debug('processing cell', check_codewords=self.codewords)

        for codeword in self.codewords:
            if checks[codeword](infoset) is False:
                self.cells[cell_id].append(codeword)

    def report(self, format='ascii'):
        if format != 'ascii':
            log.error('unknown report format', format=format)
            return

        if len(self.cells.items()) == 0:
            self.log.warning('no data')
            return

        asciitable.write([ (id, ','.join(self.cells[id])) for id in sorted(self.cells.keys()) ],
            names=['Cell ID', 'Failed checks'], formats={ 'Cell ID': '%s', 'Failed checks': '%s' },
            Writer=asciitable.FixedWidth)


def _config_group(parser):
    group = parser.add_argument_group('checker report')
    group.add_argument('--checker-codeword', choices=checks.keys(), dest='checker_codewords', action='append',
        help='Only perform selected checks')


v1.register_report(v1.Report('checker', CheckerReport))
v1.register_config_group('checker', _config_group)
