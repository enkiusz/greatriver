#!/usr/bin/env python3

import sys
import argparse
from structlog import get_logger
from pathlib import Path
import json


log = get_logger()

def new_cell(id, config, log):
    log.debug('creating cell')

    cell_path = Path(id)
    cell_path.mkdir(exist_ok=True)

    metadata = dict(v=0, id=id)

    if config.brand:
        metadata['brand'] = config.brand

    if config.model:
        metadata['model'] = config.model

    if config.capacity:
        metadata['capacity'] = { 'nom': config.capacity }

    if config.tags:
        metadata['tags'] = config.tags

    with open(cell_path.joinpath('meta.json'), "w") as f:
        f.write("V0\n")
        f.write(json.dumps(metadata, indent=2))

def main(config, log):

    for id in config.identifiers:

        if id == '-':
            for line in sys.stdin:
                line = line.rstrip()

                log = log.bind(id=line)
                new_cell(id=line, config=config, log=log)
        else:
            log = log.bind(id=id)
            new_cell(id=id, config=config, log=log)
        
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Create new cells')
    parser.add_argument('-b', '--brand', help='Cell brand for all created cells')
    parser.add_argument('-m', '--model', help='Cell model for all created cells')
    parser.add_argument('-c', '--capacity', help='Capacity in mAh for all created cells')
    parser.add_argument('-t', '--tag', dest='tags', action='append', help='Tag all created cells')
    parser.add_argument('identifiers', nargs='*', default=['-'], help='Cell identifiers, read from stdin by default')

    args = parser.parse_args()
    log.debug('config', args=args)

    main(config=args, log=log)


