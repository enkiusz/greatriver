#!/usr/bin/env python3

from pathlib import Path
import json

from structlog import get_logger
from secondlife.plugins.api import v1
from secondlife.utils import VFS

log = get_logger()

def load_metadata(filename):
    with open(filename) as f:

        version_token = f.readline().rstrip()
        if version_token != 'V0':
            raise RuntimeError(f"Version '{version_token}' not supported")
        
        j = json.loads(f.read())

        # The tags are a set
        if 'tags' in j:
            j['tags'] = set(j['tags'])

        return VFS(j)

def save_metadata(metadata, filename):
    with open(filename, "w") as f:
        f.write(f"V{metadata.get('/v')}\n")

        # Convert the tags set back to a list
        if metadata.get('/tags'):
            metadata.put('/tags', list(metadata.get('/tags')))

        f.write(json.dumps(metadata.data, indent=2))


def find_cell(cell_id):
    p = Path()
    for path in p.glob('**/meta.json'):
        try:
            metadata = load_metadata(path)
            if metadata.get('/id') == cell_id:
                return (path, metadata)
        except:
            pass
    else:
        return (None, None)


def new_cell(id):
    global log

    log.debug('new cell', cell_id=id)

    cell_path = Path(id)
    cell_path.mkdir(exist_ok=True)

    metadata_path = cell_path.joinpath('meta.json')
    metadata = VFS(dict(v=0, id=id))

    save_metadata(metadata, metadata_path)

    return (metadata_path, metadata)

def change_properties(path, metadata, config):
    global log

    for prop in config.properties:
        metadata.put(prop[0], prop[1])
    
    if config.tags:
        if '/tags' not in metadata.paths():
            metadata.put('/tags', set())

        tags = metadata.get('/tags')
        tags |= set(config.tags)

    save_metadata(metadata, path)

def store_measurement(path, metadata, codeword, config, timestamp=None):
    global log

    log = log.bind(codeword=codeword)
    
    handler = v1.measurements[codeword].handler_class(config=config)

    m = handler.measure(config)
    if m:
        if timestamp and 'ts' not in m:
            m['ts'] = timestamp

        log.debug('measurement data', data=m)

        log_filename = path.parent.joinpath('log.json')
        log.debug('saving to log', filename=log_filename)

        if not log_filename.exists():
            log_filename.write_text('[]')

        j = json.loads(log_filename.read_text())
        j.append(m)
        log_filename.write_text(json.dumps(j, indent=2))
    else:
        log.error("measurement unsuccessful")