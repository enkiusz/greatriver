#!/usr/bin/env python3

import sys
import argparse
from structlog import get_logger
from pathlib import Path
import io
import json


log = get_logger()

def load_metadata(filename):
    with open(filename) as f:

        version_token = f.readline().rstrip()
        log.debug('loading metadata', filename=filename, version=version_token)
        if version_token != 'V0':
            raise RuntimeError(f"Version '{version_token}' not supported")
        
        j = json.loads(f.read())
        return j

def save_metadata(metadata, filename):
    with open(filename, "w") as f:
        f.write(f"V{metadata['v']}\n")
        f.write(json.dumps(metadata, indent=2))

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

def setprop(id, config, log):
    
    path, metadata = find_cell(id)
    log.debug('cell found', id=id, path=path, metadata=metadata)
    if not path:
        log.warn('cell not found', id=id)
        return
    
    for prop in config.properties:
        metadata[prop[0]] = prop[1]
    
    if config.tags:
        if 'tags' not in metadata:
            metadata['tags'] = []
            
        metadata['tags'].extend(config.tags)

    save_metadata(metadata, path)

def main(config, log):

    for id in config.identifiers:

        if id == '-':
            for line in sys.stdin:
                line = line.rstrip()

                log = log.bind(id=line)
                setprop(id=line, config=config, log=log)
        else:
            log = log.bind(id=id)
            setprop(id=id, config=config, log=log)
        
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Create new cells')
    parser.add_argument('-t', '--tag', dest='tags', action='append', help='Tag cells')
    parser.add_argument('-p', '--property', nargs=2, dest='properties', action='append', help='Set a property for cells')
    parser.add_argument('identifiers', nargs='*', help='Cell identifiers, use - to read from stdin')

    args = parser.parse_args()
    log.debug('config', args=args)

    main(config=args, log=log)


