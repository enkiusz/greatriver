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
from enum import Enum, auto

# Reference: https://stackoverflow.com/a/49724281
LOG_LEVEL_NAMES = [logging.getLevelName(v) for v in
                   sorted(getattr(logging, '_levelToName', None) or logging._levelNames) if getattr(v, "real", 0)]

log = structlog.get_logger()

from secondlife.cli.utils import generate_id, selected_cells, all_cells, add_plugin_args, cell_identifiers
from secondlife.cli.utils import add_cell_selection_args, add_all_cells_match_args, add_backend_selection_args
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
            print(f"{self.id}\t{len(self.blocks)}S\tcapa[sum {self.blocks_capa['sum']/1000:5.0f} Ah, mean {self.blocks_capa['mean']/1000:3.2f}, stdev {self.blocks_capa['stdev']:3.5f} mAh ({self.blocks_capa['stdev_pct']:3.2f} %)]\tIR[max {self.blocks_ir['max']:2.2f} mΩ, mean {self.blocks_ir['mean']:2.2f}, stdev {self.blocks_ir['stdev']:2.5f} ({self.blocks_ir['stdev_pct']:3.2f} %)]")  # noqa
            for block in self.blocks:
                block.print_info("\t")

        log.info('string layout', cells=sum([ len(b.cells) for b in self.blocks ]),
            S=len(self.blocks), P=[ len(b.cells) for b in self.blocks ],
            energy_capacity=f'{self.energy_capacity:3.1f} kWh',
            block_capacity_mean=f"{self.blocks_capa['mean']/1000:3.2f} Ah",
            interblock_capacity_stdev=f"{self.blocks_capa['stdev_pct']:3.2f} %",
            block_ir_mean=f"{self.blocks_ir['mean']:2.2f} mΩ",
            interblock_ir_stdev=f"{self.blocks_ir['stdev_pct']:3.2f} %",
            intrablock_ir_stdev_max=f"{max([block.ir['stdev_pct'] for block in self.blocks]):3.2f} %")


def improved(string_before, string_after):
    """
    Return True if the string_after has parameters better than string_before
    """

    block_ir_stdevs_before = [ block.ir['stdev_pct'] for block in string_before.blocks ]
    block_ir_stdevs_after = [ block.ir['stdev_pct'] for block in string_after.blocks ]

    if max(block_ir_stdevs_before) > 15:
        if max(block_ir_stdevs_after) < max(block_ir_stdevs_before):
            log.debug('max ir stdev for all blocks improved',
                before=max(block_ir_stdevs_before), after=max(block_ir_stdevs_after))
            return True

    if string_before.blocks_capa['stdev_pct'] > 2:
        if string_after.blocks_capa['stdev_pct'] < string_before.blocks_capa['stdev_pct']:
            log.debug('capa stdev between blocks improved',
                before=string_before.blocks_capa['stdev_pct'], after=string_after.blocks_capa['stdev_pct'])
            return True

    return False


def stop(string):
    """
    Return True if the string layout is good enough.
    """

    if any([ block.ir['stdev_pct'] > 10 for block in string.blocks ]):
        # IR stdev in any block is > 10%
        return False

    if string.blocks_capa['stdev_pct'] > 1:
        # Divergence between capacity of each block is > 1 %
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


def build_pool(backend, config):
    pool = [ infoset for infoset in selected_cells(config=config, backend=backend)
        if infoset.fetch('.state.usable_capacity') and infoset.fetch('.state.internal_resistance') ]

    # Add only cell IDs which have both an IR and capacity measurements
    log.info('cell pool', count=len(pool))

    pool.sort(reverse=True, key=lambda cell: cell.fetch('.state.usable_capacity')['v'])
    return pool


def assemble_string(pool, config):

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
    last_new_string = time.time()
    last_new_string_iter = 0

    while True:
        n = iterations // 100 + 1

        # Perform n swaps
        log.debug('swapping cells', n=n)
        swaps = list(grouper(random.sample(range(len(pool)), min(2 * n, len(pool))), 2))
        for (i1, i2) in swaps:
            if i1 is not None and i2 is not None:
                pool[i1], pool[i2] = pool[i2], pool[i1]

        new_string = build_string(pool, config.S, config.P, config)

        if improved(string, new_string):
            log.info('improved string found', iterations=iterations)

            # if config.loglevel == 'DEBUG':
            #     cls()
            string.print_info(verbose=True if config.loglevel == 'DEBUG' else False)

            last_new_string = time.time()
            iterations = 0
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

        if (time.time() - last_new_string > config.optimizer_timeout) or (time.time() - optimizer_start_time > config.total_timeout):
            log.warn('optimizer timeout')
            break

    log.info('optimization finished')
    return string


def _layout_args(parser):
    group = parser.add_argument_group('layout')
    group.add_argument('-S', dest='S', type=int, default=2, help='The amount of series-connected blocks in a string')
    group.add_argument('-P', dest='P', type=int, help='The amount of cells connected parallel in each block')


def _optimizer_args(parser):
    group = parser.add_argument_group('optimizer')
    group.add_argument('--optimizer-timeout', metavar='SEC', default=60, type=float,
        help='Finish optimizer when a better solution is not found in SEC seconds')
    group.add_argument('--total-timeout', metavar='SEC', default=1200, type=float,
        help='Unconditionally finish the optimizer after SEC seconds')


def cmd_preview(config):
    backend = v1.celldb_backends[args.backend](dsn=args.backend_dsn, config=args)

    pool = build_pool(backend, config)

    s = assemble_string(pool, config)
    s.print_info(verbose=True)


def cmd_assemble(config):
    backend = v1.celldb_backends[args.backend](dsn=args.backend_dsn, config=args)

    pool = build_pool(backend, config)

    s = assemble_string(pool, config)
    s.print_info(verbose=True)

    log.info('assembling string', path=config.path)
    string_infoset = backend.create(id=s.id, path=config.path or '/')
    backend.put(string_infoset)

    string_path = str(Path(string_infoset.fetch('.path')).joinpath(string_infoset.fetch('.id')))

    for block in s.blocks:
        block_infoset = backend.create(id=block.id, path=string_path)
        backend.put(block_infoset)

        block_path = str(Path(block_infoset.fetch('.path')).joinpath(block_infoset.fetch('.id')))
        for cell in block.cells:
            backend.move(id=cell.fetch('.id'), destination=block_path)


def cmd_replace(config):
    backend = v1.celldb_backends[args.backend](dsn=args.backend_dsn, config=args)

    pool = [ infoset for infoset in all_cells(config=config, backend=backend)
        if infoset.fetch('.state.usable_capacity') and infoset.fetch('.state.internal_resistance') ]

    # Add only cell IDs which have both an IR and capacity measurements
    log.info('cell pool', count=len(pool))

    for id in cell_identifiers(config=config):

        # Find cell
        infoset = backend.fetch(id)
        if not infoset:
            log.error('cell not found', id=id)
            sys.exit(1)

        capacity = infoset.fetch('.state.usable_capacity')
        ir = infoset.fetch('.state.internal_resistance')
        path = infoset.fetch('.path')
        log.info('replacing cell', id=id, path=path, capacity=capacity, ir=ir)

        pool.sort(reverse=False, key=lambda cell:
            abs(capacity['v'] - cell.fetch('.state.usable_capacity')['v']) +
            abs(ir['v'] - cell.fetch('.state.internal_resistance')['v'])
        )

        replacement_cell = pool[0]
        if replacement_cell.fetch('.id') == id:
            log.error('replaced cell found in pool', id=id)
            continue

        replacement_capacity = replacement_cell.fetch('.state.usable_capacity')
        replacement_ir = replacement_cell.fetch('.state.internal_resistance')
        log.info('replacement cell found', id=replacement_cell.fetch('.id'),
            capacity=replacement_capacity, ir=replacement_ir)

        if config.dump_path:
            pool = pool[1:]  # Remove the replacement cell from the pool
            backend.move(id=replacement_cell.fetch('.id'), destination=path)
            backend.move(id=id, destination=config.dump_path)


if __name__ == "__main__":
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr)
    )
    load_plugins()

    parser = argparse.ArgumentParser(description='Select cells to build a string of blocks connected in series. Monte-Carlo optimization.')
    parser.add_argument('--loglevel', choices=LOG_LEVEL_NAMES, default='INFO', help='Change log level')

    add_plugin_args(parser)

    # Then add argument configuration argument groups dependent on the loaded plugins, include only:
    # - state var plugins
    # - celldb backend plugins
    included_plugins = v1.state_vars.keys() | v1.celldb_backends.keys()
    for codeword in filter(lambda codeword: codeword in v1.config_groups.keys(), included_plugins):
        v1.config_groups[codeword](parser)

    subparsers = parser.add_subparsers(help='commands')

    preview_parser = subparsers.add_parser('preview', help="Choose cells which would go into a string but don't assemble it")
    preview_parser.set_defaults(cmd=cmd_preview)
    preview_parser.add_argument('--cell-voltage', type=float, default=3.6, help='Nominal cell voltage used to calcualte capacity')
    add_backend_selection_args(preview_parser)
    add_cell_selection_args(preview_parser)
    _layout_args(preview_parser)
    _optimizer_args(preview_parser)

    assemble_parser = subparsers.add_parser('assemble', help="Assemble a new string moving the chosen cells from the pool to individual blocks")
    assemble_parser.set_defaults(cmd=cmd_assemble)
    assemble_parser.add_argument('--cell-voltage', type=float, default=3.6, help='Nominal cell voltage used to calcualte capacity')
    assemble_parser.add_argument('--path', required=True, metavar='PATH', default='/', help='Set PATH for the assembled string')
    add_backend_selection_args(assemble_parser)
    add_cell_selection_args(assemble_parser)
    _layout_args(assemble_parser)
    _optimizer_args(assemble_parser)

    replace_parser = subparsers.add_parser('replace', help="Replace specified cells")
    replace_parser.set_defaults(cmd=cmd_replace)
    add_backend_selection_args(replace_parser)
    add_all_cells_match_args(replace_parser)
    replace_parser.add_argument('--dump-path', help="The path where the old cell will be moved to")
    replace_parser.add_argument('identifiers', nargs='*', default=[], help='Cell identifiers to replace, use - to read from standard input')

    args = parser.parse_args()

    # Restrict log message to be above selected level
    structlog.configure( wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, args.loglevel)) )

    log.debug('config', args=args)

    args.cmd(config=args)
