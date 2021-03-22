#!/usr/bin/env python3

import sys
import argparse
from structlog import get_logger
from pathlib import Path
import os
import io
import json
import time

log = get_logger()

def load_metadata(filename):
    with open(filename) as f:

        version_token = f.readline().rstrip()
        if version_token != 'V0':
            raise RuntimeError(f"Version '{version_token}' not supported")
        
        j = json.loads(f.read())
        return j

def find_cell(cell_id):
    p = Path()
    for path in p.glob('**/meta.json'):
        try:
            metadata = load_metadata(path)
            if metadata['id'] == cell_id:
                return (path, metadata)
        except:
            pass
    else:
        return (None, None)

def store_measurement(cell_id, config, log):
    log = log.bind(code=config.measure)
    log.info('measure')

    path, metadata = find_cell(cell_id)
    if not path:
        log.error('cell not found')
        return

    log.debug('cell found', path=path, metadata=metadata)

    if config.measure == 'rc':
        raise NotImplementedError()
    elif config.measure == 'capa':
        capa = input('Capacity [mAh] > ')
        ir = input('IR [mOhm] > ')
        m = {
            'equipment': dict(brand='Liitokala', model='Engineer LI-500'),
            'setup': dict(mode='NOR TEST', current='500 mA'),
            'results': {
                'capacity': dict(u='mAh', v=capa),
                'ir': dict(u='mOhm', v=ir)
            }
        }
    else:
        log.error('bad measurement', code=config.measure)
        return

    if config.timestamp:
        m['ts'] = time.time()

    log.debug('measurement data', data=m)

def main(config, log):
    
    for id in config.identifiers:

        if id == '-':
            for line in sys.stdin:
                line = line.rstrip()
                log = log.bind(id=line)
                store_measurement(cell_id=line, config=config, log=log)
        else:
            log = log.bind(id=id)
            store_measurement(cell_id=id, config=config, log=log)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Log an action')
    parser.add_argument('-m', '--measure', required=True, choices=['rc', 'capa'], help='Measurement mode')
    parser.add_argument('-T', '--timestamp', nargs='?', help='Timestamp the log entry')
    parser.add_argument('identifiers', nargs='*', help='Cell identifiers, use - to read from stdin')

    args = parser.parse_args()
    log.debug('config', args=args)

    main(config=args, log=log)

