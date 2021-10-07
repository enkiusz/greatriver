#!/usr/bin/env python3

# Python 3.9 is needed to load additional plugins as the code uses
# https://docs.python.org/3/library/pkgutil.html#pkgutil.resolve_name

# Allow module load from lib/python in main repo
import sys
from pathlib import Path
currentdir = Path(__file__).resolve(strict=True).parent
libdir = currentdir.parent.joinpath('lib/python')
sys.path.append(str(libdir))

import argparse
import logging
import structlog
import copy
import random
from statistics import mean, stdev
import time
import os
from functools import cached_property
from itertools import zip_longest

# Reference: https://stackoverflow.com/a/49724281
LOG_LEVEL_NAMES = [logging.getLevelName(v) for v in
                   sorted(getattr(logging, '_levelToName', None) or logging._levelNames) if getattr(v, "real", 0)]

log = structlog.get_logger()

from secondlife.cli.utils import generate_id, selected_cells, add_plugin_args, add_cell_selection_args, add_backend_selection_args
from secondlife.plugins.api import v1, load_plugins


def _calculate_statistics(data: list) -> dict:
    d = dict(min=0, max=0, mean=0, stdev=0, stdev_pct=0, sum=sum(data))

    if len(data) > 0:
        d['mean'] = mean(data)
        d['min'] = min(data)
        d['max'] = max(data)

    if len(data) > 1:
        d['stdev'] = stdev(data)
        d['stdev_pct'] = (d['stdev'] / d['mean']) * 100

    return d


class Block(object):
    def __init__(self, **kwargs):
        self._id = kwargs.get('id', generate_id('BL'))
        self._cells = kwargs.get('cells', [])

    @property
    def id(self):
        return self._id

    @property
    def cells(self):
        return self._cells

    def add_cell(self, cell):
        try:
            del self.capa
        except AttributeError:
            pass

        try:
            del self.ir
        except AttributeError:
            pass

        return self.cells.append(cell)

    @cached_property
    def capa(self):
        return _calculate_statistics(list(map(lambda c: c.fetch('.state.usable_capacity')['v'], self.cells)))

    @cached_property
    def ir(self):
        d = _calculate_statistics(list(map(lambda c: c.fetch('.state.internal_resistance')['v'], self.cells)))
        if len(self.cells) > 0:
            d['parallel'] = 1 / sum([ 1 / cell.fetch('.state.internal_resistance')['v'] for cell in self.cells ])
        else:
            d['parallel'] = float('+Inf')
        return d

    def print_info(self, prefix=''):
        print(f"{prefix}{self.id}\t{len(self.cells)}P\tcapa[sum {self.capa['sum']:5.0f} mAh, mean {self.capa['mean']:5.2f} stdev {self.capa['stdev']:3.2f} ({self.capa['stdev_pct']:3.1f} %)]\tIR[parallel {self.ir['parallel']:3.2f} mΩ, mean {self.ir['mean']:5.2f}, stdev {self.ir['stdev']:5.2f} mΩ ({self.ir['stdev_pct']:3.1f} %)]")  # noqa


class String(object):
    def __init__(self, **kwargs):
        self._id = kwargs.get('id', generate_id('STR'))
        self._blocks = kwargs.get('blocks', [])
        self._config = kwargs['config']

    @property
    def id(self):
        return self._id

    @property
    def blocks(self):
        return self._blocks

    @property
    def config(self):
        return self._config

    @property
    def blocks_capa(self):
        return _calculate_statistics(list(map(lambda b: b.capa['sum'], self.blocks)))

    @property
    def blocks_ir(self):
        return _calculate_statistics(list(map(lambda b: b.ir['parallel'], self.blocks)))

    @property
    def energy_capacity(self):
        return (self.blocks_capa['sum'] / 1000 * self.config.cell_voltage) / 1000

    def print_info(self, prefix='', verbose=False):
        if verbose is True:
            print(f"{self.id}\tcapa[sum {self.blocks_capa['sum']/1000:5.0f} Ah, mean {self.blocks_capa['mean']/1000:3.2f}, stdev {self.blocks_capa['stdev']:3.5f} mAh ({self.blocks_capa['stdev_pct']:3.2f} %)]\tIR[max {self.blocks_ir['max']:2.2f} mΩ, mean {self.blocks_ir['mean']:2.2f}, stdev {self.blocks_ir['stdev']:2.5f} ({self.blocks_ir['stdev_pct']:3.2f} %)]")  # noqa
            for block in self.blocks:
                block.print_info("\t")

        log.info('pack layout', energy_capacity=f'{self.energy_capacity:3.1f} kWh',
            block_capacity_mean=f"{self.blocks_capa['mean']/1000:3.2f} Ah",
            block_capacity_divergence=f"{self.blocks_capa['stdev_pct']:3.2f} %",
            block_ir_mean=f"{self.blocks_ir['mean']:2.2f} mΩ",
            block_ir_divergence=f"{self.blocks_ir['stdev_pct']:3.2f} %")


def improved(string_before, string_after):
    """
    Return True if the string_after has parameters better than string_before
    """

    if string_before.blocks_capa['stdev_pct'] > 0.2:
        if string_after.blocks_capa['stdev_pct'] > string_before.blocks_capa['stdev_pct']:
            return False

    if string_after.blocks_ir['stdev_pct'] > string_before.blocks_ir['stdev_pct']:
        return False

    return True


def stop(string):
    """
    Return True if the string layout is good enough.
    """

    if string.blocks_capa['stdev_pct'] > 0.5:
        # Divergence between capacity of each block is > 0.5 %
        return False

    if string.blocks_ir['stdev_pct'] > 5:
        # Divergence between the internal resistance of each block is > 5 %
        return False

    return True


def build_string(pool, S, P, config):
    pool = pool.copy()

    string = String(config=config, blocks=[ Block() for i in range(S) ])
    max_block_size = P

    while len(pool) >= S and any([ len(block.cells) < max_block_size for block in string.blocks ]):

        # Simple round-robin assignment
        for block in string.blocks:
            block.add_cell(pool.pop(0))

        # Match based on IR:
        # Decide where to add the cell based on minimum difference between mean IR and cell IR
        #
        # cell = pool.pop(0)
        # cell_ir = cell.fetch('.state.internal_resistance')['v']

        # nonfull_blocks = filter(lambda block: len(block.cells) < max_block_size, string.blocks)
        # best_block = sorted(nonfull_blocks, key=lambda block: abs(block.ir['mean'] - cell_ir))[0]
        # best_block.add_cell(cell)

    return string


def grouper(iterable, n, fillvalue=None):
    "Collect data into non-overlapping fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


def main(config):

    backend = v1.celldb_backends[args.backend](dsn=args.backend_dsn, config=args)

    pool = []

    for infoset in selected_cells(config=config, backend=backend):
        if infoset.fetch('.state.usable_capacity') and infoset.fetch('.state.internal_resistance'):
            pool.append(infoset)

    # Add only cell IDs which have both an IR and capacity measurements
    log.info('cell pool', count=len(pool))

    pool.sort(reverse=True, key=lambda cell: cell.fetch('.state.usable_capacity')['v'])

    if config.P is None:
        # No P selected, try to use all cells available
        config.P = len(pool) // config.S
        log.warn('P not defined', autoselected_p=config.P)
    else:
        P = config.P

    log.info('selecting cells', pool_size=len(pool), S=config.S, P=config.P)
    if len(pool) < config.S * config.P:
        log.warning('pool is too small for fill out all cells', pool_size=len(pool), S=config.S, P=config.P)

    # Initial blocks
    string = build_string(pool, config.S, config.P, config)

    iterations = 0
    optimizer_start_time = time.time()
    last_progress_report = time.time()
    last_new_pack = time.time()
    last_new_pack_iter = 0

    while True:
        n = ((iterations - last_new_pack_iter) // 2000) + 1

        # Perform n swaps
        swaps = list(grouper(random.sample(range(len(pool)), 2*n), 2))
        for (i1, i2) in swaps:
            pool[i1], pool[i2] = pool[i2], pool[i1]

        new_string = build_string(pool, config.S, config.P, config)

        if improved(string, new_string):
            if config.loglevel == 'DEBUG':
                cls()
            string.print_info(verbose=True if config.loglevel == 'DEBUG' else False)

            last_new_pack = time.time()
            last_new_pack_iter = iterations
            string = new_string
        else:
            # Reverse swaps
            for (i1, i2) in swaps:
                pool[i1], pool[i2] = pool[i2], pool[i1]


        iterations += 1
        if iterations % 1000 == 0 or time.time() - last_progress_report >= 2:
            last_progress_report = time.time()
            log.info('progress', iterations=iterations)

        if stop(string):
            log.info('optimal solution found')
            break

        if (time.time() - last_new_pack > config.optimizer_timeout) or (time.time() - optimizer_start_time > config.total_timeout):
            log.warn('optimizer timeout')
            break

    log.info('optimization finished')
    string.print_info(verbose=True)


if __name__ == "__main__":
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr)
    )
    load_plugins()

    parser = argparse.ArgumentParser(description='Select cells to build a string of blocks connected in series. Monte-Carlo optimization.')
    parser.add_argument('--loglevel', choices=LOG_LEVEL_NAMES, default='INFO', help='Change log level')
    add_plugin_args(parser)
    add_backend_selection_args(parser)
    add_cell_selection_args(parser)

    group = parser.add_argument_group('packer')
    group.add_argument('--cell-voltage', type=float, default=3.6, help='Nominal cell voltage used to calcualte capacity')
    group.add_argument('-S', dest='S', type=int, default=2, help='The amount of series-connected blocks in a string')
    group.add_argument('-P', dest='P', type=int, help='The amount of cells connected parallel in each block')
    group.add_argument('--optimizer-timeout', metavar='SEC', default=60, type=float,
        help='Finish optimizer when a better solution is not found in SEC seconds')
    group.add_argument('--total-timeout', metavar='SEC', default=300, type=float,
        help='Finish optimizer after SEC seconds')

    # Then add argument configuration argument groups dependent on the loaded plugins, include only:
    # - state var plugins
    # - celldb backend plugins
    included_plugins = v1.state_vars.keys() | v1.celldb_backends.keys()
    for codeword in filter(lambda codeword: codeword in v1.config_groups.keys(), included_plugins):
        v1.config_groups[codeword](parser)

    args = parser.parse_args()

    # Restrict log message to be above selected level
    structlog.configure( wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, args.loglevel)) )

    log.debug('config', args=args)

    main(config=args)
