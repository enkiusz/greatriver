#!/usr/bin/env python3

from pathlib import Path
import json
import time

from structlog import get_logger
from secondlife.plugins.api import v1
from secondlife.utils import Infoset
from secondlife.celldb import CellDB

class JsonFiles(CellDB):
    def __init__(self, **kwargs):
        super().__init__()
        self.log = get_logger(name=__class__.__name__)
        self.config = kwargs['config']
        self.basepath = kwargs.get('basepath', Path())
        self.log.info('creating backend', basepath=self.basepath)

    def _load_cell_infoset(self, location: Path) -> Infoset:
        infoset = Infoset()

        # Load properties
        # In version V0 meta.json contains fixed data
        with open(location, "r") as f:

            version_token = f.readline().rstrip()
            if version_token != 'V0':
                raise RuntimeError(f"Version '{version_token}' not supported")

            infoset.put('.version', version_token)
            infoset.put('.backend.location', str(location))

            j = json.load(f)

            infoset.put('.props', Infoset(data=j))

        # Try to load the log
        try:
            log_filename = location.with_name('log.json')
            j = json.loads(log_filename.read_text(encoding='utf8'))

            infoset.put('.log', j)

        except Exception as e:
            self.log.error('cannot read log', filename=log_filename, _exc_info=e)

        # Bind the state variables
        for (path, statevar_class) in v1.state_vars.items():
            infoset.put(f'.state.{path}', statevar_class(cell=infoset))

        return infoset

    def create(self, id: str) -> Infoset:

        self.log.debug('creating cell', cell_id=id)

        infoset = Infoset(data=dict(version='V0'))
        infoset.put('.props', Infoset(data=dict(id=id)))
        infoset.put('.log', [ dict(type='lifecycle', event='entry-created', ts=time.time()) ])

        cell_path = Path(id)
        cell_path.mkdir(exist_ok=True)

        location = cell_path.joinpath('meta.json')
        infoset.put('.backend.location', location)

        self.put(infoset)

        return infoset

    def fetch(self, id: str) -> Infoset:
        self.log.info('searching for cell', id=id)

        for path in self.basepath.glob('**/meta.json'):
            try:
                infoset = self._load_cell_infoset(path)
                print(infoset)
                if infoset.fetch('.props.id') == id:
                    return infoset
            except Exception as e:
                pass
        else:
            return None

    def put(self, infoset: Infoset) -> bool:
        location = infoset.fetch('.backend.location')

        with open(location, 'w') as f:
            f.write(f"{infoset.fetch('.version')}\n")
            f.write(json.dumps(infoset.fetch('.props')))

        location.with_name('log.json').write_text(json.dumps(infoset.fetch('.log')) )
        
        return True

    def find(self) -> Infoset: # Generator
        cells_found_total = 0
        last_progress_report = 0

        for path in self.basepath.glob('**/meta.json'):
            try:
                infoset = self._load_cell_infoset(path)
                if infoset.fetch('.props.id'):
                    self.log.debug('cell found', path=path)

                    # Progress report every 1000 cells or 2 seconds
                    cells_found_total += 1
                    if cells_found_total % 1000 == 0 or time.time() - last_progress_report >= 2:
                        last_progress_report = time.time()
                        self.log.info('progress', cells_found_total=cells_found_total)

                    yield infoset
            except Exception as e:
                self.log.error('cannot load cell', path=path, _exc_info=e)

v1.register_celldb_backend('json-files', JsonFiles)