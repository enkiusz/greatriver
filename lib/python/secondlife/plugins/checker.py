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


def _count_mcc_workflows(log):
    count = 0
    for entry in log:
        if 'equipment' not in entry:
            continue

        if entry['equipment']['model'] == 'Megacell Charger':
            count += 1
    return count


def _check_paths(backend, infoset):
    for e in infoset.fetch('.log'):
        if 'path' in e:
            p = e['path']
            if p is None:
                return False

            if hasattr(p, 'values'):
                if 'old' in p:
                    if not backend.path_valid(p['old']):
                        return False
                if 'new' in p:
                    if not backend.path_valid(p['new']):
                        return False
            else:
                if not backend.path_valid(p):
                    return False
    return True


def _check_log_ir_spelling(infoset):
    for e in infoset.fetch('.log'):
        if 'results' not in e:
            continue

        r = e['results']
        if 'ir' in r:
            return False

    return True


# Each check returns True on OK and False on FAIL
checks = {
    'null_brand_model_not_noname': lambda backend, infoset: not (
        infoset.fetch('.props.brand') is None and infoset.fetch('.props.model') is None and infoset.fetch('.props.tags.noname') is not True
    ),
    'only_brand_and_not_likelyfake': lambda backend, infoset: not (
        infoset.fetch('.props.brand') is not None and infoset.fetch('.props.model') is None and infoset.fetch('.props.tags.likely_fake') is not True
    ),
    'unit_instead_of_u': lambda backend, infoset: _check_log_units(infoset.fetch('.log')),
    'log_entries_without_ts': lambda backend, infoset: _check_log_ts(infoset.fetch('.log')),
    'log_entries_without_event': lambda backend, infoset: _check_log_event(infoset.fetch('.log')),
    'multiple_mcc_workflows': lambda backend, infoset: _count_mcc_workflows(infoset.fetch('.log')) <= 1,
    'path_inconsistency': lambda backend, infoset: infoset.fetch('.path') == infoset.fetch('.log')[0]['path'],
    'paths_invalid': lambda backend, infoset: _check_paths(backend, infoset),
    'lowercase_ir_result': lambda backend, infoset: _check_log_ir_spelling(infoset),
}


class CheckerReport(object):

    def __init__(self, **kwargs):
        self.config = kwargs['config']
        self.backend = kwargs.get('backend', None)
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
            if checks[codeword](backend=self.backend, infoset=infoset) is False:
                self.cells[cell_id].append(codeword)

    def report(self, format='ascii'):
        if format != 'ascii':
            log.error('unknown report format', format=format)
            return

        if len(self.cells.items()) == 0:
            self.log.warning('no data')
            return

        print( tabulate.tabulate([ (id, ','.join(self.cells[id])) for id in sorted(self.cells.keys()) ],
                              headers=['Cell ID', 'Failed checks'],
                              tablefmt='fancy_grid') )


def _config_group(parser):
    group = parser.add_argument_group('checker report')
    group.add_argument('--checker-codeword', choices=checks.keys(), dest='checker_codewords', action='append',
        help='Only perform selected checks')


v1.register_report(v1.Report('checker', CheckerReport))
v1.register_config_group('checker', _config_group)
