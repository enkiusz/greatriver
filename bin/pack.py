#!/usr/bin/env python3

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

# Reference: https://stackoverflow.com/a/49724281
LOG_LEVEL_NAMES = [logging.getLevelName(v) for v in
                   sorted(getattr(logging, '_levelToName', None)
                          or logging._levelNames)
                   if getattr(v, "real", 0)]

log = structlog.get_logger()

from secondlife.cli.utils import generate_id, selected_cells, add_cell_selection_args, add_backend_selection_args
from secondlife.plugins.api import v1, load_plugins

def block_ir(block):
    return 1 / sum([ 1/cell.fetch('.state.internal_resistance')['v'] for cell in block['cells'] ])

def sum_stdev(blocks):
    return stdev([ b['sum'] for b in blocks])

def sum_mean(blocks):
    return mean([ b['sum'] for b in blocks])

def sum_stdev_ok(blocks):
    return sum_stdev(blocks) / sum_mean(blocks) < 0.01

def max_ir_stdev(blocks):
    return max([ b['ir']['stdev']/b['ir']['mean'] for b in blocks ])

def ir_stdev_ok(blocks):
    return max_ir_stdev(blocks) < 0.3

def total_capacity(blocks):
    return sum([ b['sum'] for b in blocks ])

def keep(blocks_before, blocks_after):
    block_count = len(blocks_before)

    b_sums_stdev_before = stdev([ b['sum'] for b in blocks_before ])
    b_sums_stdev_after = stdev([ b['sum'] for b in blocks_after ])
    b_sums_stdev_delta_improved = b_sums_stdev_after < b_sums_stdev_before

    b_ir_stdev_before = [ b['ir']['stdev'] for b in blocks_before ]
    b_ir_stdev_after = [ b['ir']['stdev'] for b in blocks_after ]
    b_ir_stdev_improved = [ b_ir_stdev_after < b_ir_stdev_before for (b_ir_stdev_after, b_ir_stdev_before) in zip(b_ir_stdev_after, b_ir_stdev_before) ]

    if b_sums_stdev_delta_improved and len(b_ir_stdev_improved) == block_count:
        return True
    else:
        return False

def blocks_info(blocks, config):
    log.info('pack layout', capacity_divergence=f'{sum_stdev(blocks):.2f} mAh', max_ir_divergence=f"{max_ir_stdev(blocks)*100:.2f} %", total_capacity=f"{total_capacity(blocks)/1000 * config.cell_voltage:.2f} Wh")
    if config.loglevel == 'DEBUG':
        blocks_details(blocks, config)

def blocks_details(blocks, config):
    print('\n'.join([ f"block {b['id']}\t{len(b['cells']):3d} cells, capa[sum {b['sum']:5.0f} mAh, mean {b['mean']:5.5f}, stdev {b['stdev']:3.5f} ({(b['stdev']/b['mean'])*100:3.2f} %)] IR[parallel {b['ir']['total']:.2f} mΩ, mean {b['ir']['mean']:5.3f} mΩ, stdev {b['ir']['stdev']:5.3f} mΩ ({(b['ir']['stdev']/b['ir']['mean'])*100:3.2f} %)]" for b in blocks ]))
    print(f"Capacity divergence (stdev between blocks): {sum_stdev(blocks):.2f} mAh ({(sum_stdev(blocks) / sum_mean(blocks)) * 100:.2f} %)")
    print(f"Total capacity {total_capacity(blocks)/1000:.2f} Ah * {config.cell_voltage} V = {(config.cell_voltage * (total_capacity(blocks)/1000)):.2f} Wh")

def stop(blocks):
    if sum_stdev_ok(blocks) and ir_stdev_ok(blocks):
        return True

    return False

def get_blocks(pool, S, P):
    pool = pool.copy()

    blocks = [ dict(id=generate_id('BL'), cells=[]) for i in range(S) ]
    block_size = 0
    max_block_size = P

    while len(pool) >= S:
        for block in blocks:
            block['cells'].append(pool.pop(0))

        block_size += 1
        if block_size == max_block_size:
            break

    for block in blocks:
        block['mean'] = mean([ c.fetch('.state.usable_capacity')['v'] for c in block['cells'] ])
        block['stdev'] = stdev([ c.fetch('.state.usable_capacity')['v'] for c in block['cells'] ])
        block['sum'] = sum([ c.fetch('.state.usable_capacity')['v'] for c in block['cells'] ])

        block['ir'] = {
            'total': block_ir(block),
            'mean': mean([ c.fetch('.state.internal_resistance')['v'] for c in block['cells'] ]),
            'stdev': stdev([ c.fetch('.state.internal_resistance')['v'] for c in block['cells'] ])
        }

    return blocks

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
    # Initial blocks

    blocks = get_blocks(pool, config.S, config.P)
    initial_blocks = copy.deepcopy(blocks)

    blocks_info(initial_blocks, config=config)

    iterations = 0
    last_progress_report = time.time()
    last_new_pack = time.time()

    while True:
        # Swap 2 random cells
        i1, i2 = random.sample(range(len(pool)), 2)
        pool[i1], pool[i2] = pool[i2], pool[i1]

        blocks_new = get_blocks(pool, config.S, config.P)

        if keep(blocks, blocks_new):
            blocks_info(blocks_new, config=config)

            last_new_pack = time.time()
            blocks = blocks_new
        else:
            # Reverse the swap
            pool[i1], pool[i2] = pool[i2], pool[i1]

        iterations += 1
        if iterations % 1000 == 0 or time.time() - last_progress_report >= 2:
            last_progress_report = time.time()
            log.info('progress', iterations=iterations)

        if stop(blocks) or time.time() - last_new_pack > config.optimizer_timeout:
            log.warn('optimizer timeout')
            break

    log.info('optimization finished')
    blocks_info(blocks, config=config)
    blocks_details(blocks, config=config)

if __name__ == "__main__":
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr)
    )
    load_plugins()

    parser = argparse.ArgumentParser(description='Select cells to build a pack having S series-connected blocks')
    parser.add_argument('--loglevel', choices=LOG_LEVEL_NAMES, default='INFO', help='Change log level')
    add_backend_selection_args(parser)
    add_cell_selection_args(parser)

    group = parser.add_argument_group('packer')
    group.add_argument('--cell-voltage', type=float, default=3.6, help='Nominal cell voltage used to calcualte capacity')
    group.add_argument('-S', dest='S', type=int, default=2, help='The amount of series-connected blocks in a string')
    group.add_argument('-P', dest='P', type=int, help='The amount of cells connected parallel in each block')
    group.add_argument('--optimizer-timeout', metavar='SEC', default=10, type=float, help='Finish optimizer when a better solution is not found in SEC seconds')

    args = parser.parse_args()

    # Restrict log message to be above selected level
    structlog.configure( wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, args.loglevel)) )

    log.debug('config', args=args)

    main(config=args)
