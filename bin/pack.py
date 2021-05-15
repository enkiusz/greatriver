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

from secondlife.cli.utils import selected_cells, add_cell_selection_args
from secondlife.plugins.api import v1, load_plugins

def sum_stdev(blocks):
    return stdev([ b['sum'] for b in blocks])

def sum_stdev_ok(blocks):
    # Acceptable relative stdev is < 1 mAh
    return sum_stdev(blocks) < 1

def total_capacity(blocks):
    return sum([ b['sum'] for b in blocks ])

def keep(blocks_before, blocks_after):

    b_sums_stdev_before = stdev([ b['sum'] for b in blocks_before ])
    b_sums_stdev_after = stdev([ b['sum'] for b in blocks_after ])
    b_sums_stdev_delta_improved = b_sums_stdev_after < b_sums_stdev_before

    if b_sums_stdev_delta_improved:
        return True
    else:
        return False

def blocks_info(blocks, config):
    log.info('pack layout', divergence=f'{sum_stdev(blocks):.2f} mAh', total_capacity=f"{total_capacity(blocks)/1000 * config.cell_voltage:.2f} kWh")
    if config.loglevel == 'DEBUG':
        print('\n'.join([ f"block {len(b['cells']):3d} cells, capa[sum {b['sum']:5.0f} mAh, mean {b['mean']:5.5f}, stdev {b['stdev']:3.5f} ({(b['stdev']/b['mean'])*100:3.2f} %)] IR[mean {0:5.3f} mΩ, stdev {0:5.3f} ({0:3.2f} %)]" for b in blocks ]))
        print(f"Total capacity {total_capacity(blocks)/1000:.2f} Ah * {config.cell_voltage} V = {config.cell_voltage * total_capacity(blocks)/1000:.2f} kWh")

def stop(blocks):
    if sum_stdev_ok(blocks):
        return True

    return False

def get_blocks(pool, S, P):
    pool = pool.copy()

    blocks = [ dict(cells=[]) for i in range(S) ]
    block_size = 0
    max_block_size = P

    while len(pool) >= S:
        for block in blocks:
            block['cells'].append(pool.pop(0))

        block_size += 1
        if block_size == max_block_size:
            break

    for block in blocks:
        block['mean'] = mean(block['cells'])
        block['stdev'] = stdev(block['cells'])
        block['sum'] = sum(block['cells'])

    return blocks

def main(config):

    # for (path, metadata) in selected_cells(config=config):
    #     print('cell: ', metadata.get('/id'))
    #     print(json.dumps(metadata.paths()))

    pool = [ float(s.strip()) for s in sys.stdin.readlines() ]
    pool.sort(reverse=True)

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

    os.system('clear')
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
            break

    blocks_info(blocks, config=config)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Select cells to build a pack having S series-connected blocks')
    parser.add_argument('--loglevel', choices=LOG_LEVEL_NAMES, default='INFO', help='Change log level')
    add_cell_selection_args(parser)
    
    parser.add_argument('--cell-voltage', type=float, default=3.6, help='Nominal cell voltage used to calcualte capacity')
    parser.add_argument('-S', dest='S', type=int, default=1, help='The amount of series-connected blocks in a string')
    parser.add_argument('-P', dest='P', type=int, help='The amount of cells connected parallel in each block')
    
    parser.add_argument('--optimizer-timeout', metavar='SEC', default=10, type=float, help='Finish optimizer when a better solution is not found in SEC seconds')
    args = parser.parse_args()

    # Restrict log message to be above selected level
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, args.loglevel)),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr)
    )

    log.debug('config', args=args)

    main(config=args)
