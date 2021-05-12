#!/usr/bin/env python3

from pathlib import Path
import json

from structlog import get_logger
from secondlife.plugins.api import v1
from secondlife.utils import VFS
import time

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


def find_cell(cell_id, startpath=Path()):
    log.info('searching for cell', id=cell_id)
    for path in startpath.glob('**/meta.json'):
        try:
            metadata = load_metadata(path)
            if metadata.get('/id') == cell_id:
                return (path, metadata)
        except:
            pass
    else:
        return (None, None)


def new_cell(id):
    log.debug('creating cell', cell_id=id)

    cell_path = Path(id)
    cell_path.mkdir(exist_ok=True)

    metadata_path = cell_path.joinpath('meta.json')
    metadata = VFS(dict(v=0, id=id))

    save_metadata(metadata, metadata_path)

    # Store a lifecycle event
    log_append(metadata_path, dict(type='lifecycle', event='entry-created', ts=time.time()))

    return (metadata_path, metadata)

def log_append(path, entry):

    log_filename = path.parent.joinpath('log.json')
    log.info('adding log entry', log_filename=log_filename, entry=entry)

    if not log_filename.exists():
        log_filename.write_text('[]')

    j = json.loads(log_filename.read_text())
    j.append(entry)
    log_filename.write_text(json.dumps(j, indent=2))
