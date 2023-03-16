#!/usr/bin/env python3

# Python 3.9 is needed to load additional plugins as the code uses
# https://docs.python.org/3/library/pkgutil.html#pkgutil.resolve_name

# Allow module load from lib/python in main repo
import sys
from pathlib import Path

currentdir = Path(__file__).resolve(strict=True).parent
libdir = currentdir.parent.joinpath('lib/python')
sys.path.append(str(libdir))

import structlog
import logging
import threading

# Reference: https://stackoverflow.com/a/49724281
LOG_LEVEL_NAMES = [logging.getLevelName(v) for v in
                   sorted(getattr(logging, '_levelToName', None) or logging._levelNames) if getattr(v, "real", 0)]

log = structlog.get_logger()

import argparse
import logging
import time
import fileinput
import random

import board
import busio
import adafruit_pca9685
from adafruit_servokit import ServoKit
from adafruit_motor.servo import Servo

bucket_config = [

    # bucket 0
    dict(servo_channel=0, min_pulse=500, max_pulse=2200, pass_angle=20, idle_angle=107, drop_angle=180),

    # bucket 1
    dict(servo_channel=1, min_pulse=650, max_pulse=2500, pass_angle=15, idle_angle=85, drop_angle=180),

    # bucket 2
    dict(servo_channel=2, min_pulse=500, max_pulse=2500, pass_angle=0, idle_angle=90, drop_angle=180),

    # bucket 3
    dict(servo_channel=3, min_pulse=500, max_pulse=2500, pass_angle=15, idle_angle=95, drop_angle=180),

    # bucket 4
    dict(servo_channel=4, min_pulse=400, max_pulse=2600, pass_angle=15, idle_angle=95, drop_angle=180),

    # bucket 5
    dict(servo_channel=5, min_pulse=400, max_pulse=2600, pass_angle=15, idle_angle=95, drop_angle=180),

    # bucket 6
    dict(servo_channel=6, min_pulse=500, max_pulse=2500, pass_angle=0, idle_angle=95, drop_angle=180),

    # bucket 7
    dict(servo_channel=7, min_pulse=500, max_pulse=2500, pass_angle=0, idle_angle=80, drop_angle=180),

    # bucket 8
    dict(servo_channel=8, min_pulse=500, max_pulse=2600, pass_angle=31, idle_angle=105, drop_angle=180),

    # bucket 9
    dict(servo_channel=9, min_pulse=400, max_pulse=2600, pass_angle=0, idle_angle=90, drop_angle=180),

]


from secondlife.cli.utils import add_plugin_args, selected_cells
from secondlife.cli.utils import add_cell_selection_args, add_backend_selection_args
from secondlife.plugins.api import v1, load_plugins


i2c = busio.I2C(board.SCL, board.SDA)
hat = adafruit_pca9685.PCA9685(i2c)
kit = ServoKit(channels=16)


def target_bucket(config, cell):
    return cell.fetch('.path')


buckets = [ f'BUCKET~{idx}' for idx in range(10) ]
slots = [None] * 10


def slot_idle(idx, steps=20, duration=0.2):
    slot_move(idx, bucket_config[idx]['idle_angle'], steps=steps, duration=duration)


def slot_drop(idx, steps=20, duration=0.2):
    slot_move(idx, bucket_config[idx]['drop_angle'], steps=steps, duration=duration)


def slot_pass(idx, steps=20, duration=0.2):
    slot_move(idx, bucket_config[idx]['pass_angle'], steps=steps, duration=duration)


def slot_acquire(idx):
    kit.servo[idx].lock.acquire()


def slot_release(idx):
    kit.servo[idx].lock.release()


def slot_move(idx, angle, steps=20, duration=0.2):
    log.debug('moving slot', idx=idx, angle=angle)

    # Calculate step size
    step = ( angle - kit.servo[idx].angle) // steps
    for i in range(steps):
        if step < 0:
            kit.servo[idx].angle = max(kit.servo[idx].angle + step, angle)
        elif step > 0:
            kit.servo[idx].angle = min(kit.servo[idx].angle + step, 180)
        else:
            break  # Step == 0 means we don't move at all

        if duration > 0:
            # Delay so that all the movement takes `duration` seconds
            time.sleep(duration / steps)

    # Final move to make sure we hit the target angle
    kit.servo[idx].angle = angle


def cell_thread(config, cell, buckets):

    cell_id = cell.fetch('.id')
    log.info('thread start', cell=cell_id, buckets=buckets)

    if config.random_bucket:
        bkt = random.choice(buckets)
    else:
        bkt = target_bucket(config, cell)

    log.info('bucket', cell_id=cell_id, bucket=bkt)

    slots[0] = cell_id  # Cell always starts as the first (highest) slot
    slot_acquire(0)

    for idx in range(10):

        if bkt == buckets[idx]:  # The bucket matches, drop cell
            log.info('dropping', cell_id=cell_id, slot=idx, bucket=bkt)
            slot_drop(idx)
            time.sleep(0.5)
            slot_idle(idx, steps=1)

            slots[idx] = None
            slot_release(idx)
            break

        else:  # The bucket doesn't match, pass cell to next slot
            slot_pass(idx)
            time.sleep(0.5)
            slot_idle(idx, steps=1)
            slot_release(idx)
            slots[idx] = None

            if idx < len(slots) - 1:
                log.info('passing on', cell_id=cell_id, slot=idx, new_slot=idx + 1)
                slots[idx + 1] = slots[idx]
                slot_acquire(idx + 1)
            else:
                log.info('no bucket', cell_id=cell_id, slot=idx)


def cmd_sort(config):

    for (idx, path) in config.bucket_path:
        log.debug('bucket path', index=idx, path=path)
        buckets[int(idx)] = path

    for (num, bucket) in enumerate(bucket_config):
        kit._items[num] = Servo(kit._pca.channels[ bucket['servo_channel'] ], min_pulse=bucket['min_pulse'], max_pulse=bucket['max_pulse'])
        kit._items[num].lock = threading.Lock()
        slot_idle(num, steps=1)

    log.info('tumbler initialized', num_buckets=len(bucket_config))

    backend = v1.celldb_backends[args.backend](dsn=args.backend_dsn, config=args)

    for cell in selected_cells(config=config, backend=backend):
        t = threading.Thread(target=cell_thread, kwargs=dict(cell=cell, config=config, buckets=buckets))
        t.start()


if __name__ == "__main__":
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr)
    )
    load_plugins()

    parser = argparse.ArgumentParser(description='Sort cells into buckets using a cell-tumbler')
    parser.add_argument('--loglevel', choices=LOG_LEVEL_NAMES, default='DEBUG', help='Change log level')
    parser.add_argument('--bucket-path', nargs=2, action='append', help='Assign celldb path to bucket number')
    parser.add_argument('--random-bucket', default=False, action='store_true', help='Choose a random bucket for each cell (useful in testing)')

    add_plugin_args(parser)

    # Then add argument configuration argument groups dependent on the loaded plugins, include only:
    # - state var plugins
    # - celldb backend plugins
    included_plugins = v1.state_vars.keys() | v1.celldb_backends.keys()
    for codeword in filter(lambda codeword: codeword in v1.config_groups.keys(), included_plugins):
        v1.config_groups[codeword](parser)

    add_backend_selection_args(parser)
    add_cell_selection_args(parser)

    args = parser.parse_args()

    # Restrict log message to be above selected level
    structlog.configure( wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, args.loglevel)) )

    log.debug('config', args=args)

    cmd_sort(config=args)
