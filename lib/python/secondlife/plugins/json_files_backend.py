#!/usr/bin/env python3

from pathlib import Path
import json

from structlog import get_logger
from secondlife.plugins.api import v1
from secondlife.infoset import Infoset
from secondlife.celldb import CellDB

class JsonFiles(CellDB):
    def __init__(self, dsn=None, **kwargs):
        super().__init__()
        self.log = get_logger()

        if dsn is not None:
            self.basepath = Path(dsn).resolve(strict=True)
        else:
            self.basepath = Path().resolve(strict=True)
                
        self.log.debug('backend setup', basepath=self.basepath)

    def init(self):
        self.log.info('creating celldb', basepath=self.basepath)

        Path(self.basepath).mkdir(exist_ok=True)
    
    def __repr__(self):
        return f'JsonFiles/{repr(self.basepath)}'

    def _load_cell_infoset(self, location: Path) -> Infoset:
        infoset = Infoset()
        
        cell_id = location.parent.name

        # Load properties
        # In version V0 meta.json contains fixed data
        with open(location, "r") as f:

            version_token = f.readline().rstrip()
            if version_token != 'V0':
                raise RuntimeError(f"Version '{version_token}' not supported")

            j = json.load(f)

            infoset.put('.id', cell_id)

            # Synthesize container path for cell:
            # a/b/c/d/meta.json -> path is /a/b/c
            rp = location.resolve().relative_to(self.basepath).parents[1]
            if rp != Path():
                infoset.put('.path', f'/{rp}')
            else:
                infoset.put('.path', '/')

            infoset.put('.props', Infoset(data=j))

        # Try to load the log
        try:
            log_filename = location.with_name('log.json')
            j = json.loads(log_filename.read_text(encoding='utf8'))

            infoset.put('.log', j)

        except Exception as e:
            self.log.error('cannot read log', filename=log_filename, _exc_info=e)

        # Load non-JSON files (extra objects)
        infoset.put('.extra', [])
        for extra_filename in filter(lambda p: not p.match('*.json') and not p.is_dir(), location.parent.glob("*")):

            infoset.fetch('.extra').append({
                'name': extra_filename.name,
                'props': { 
                    'stat': {
                        'ctime': extra_filename.stat().st_ctime,
                        'mtime': extra_filename.stat().st_mtime
                    }
                },
                'ref': None, # Content is directly stored, not referenced
                'content': extra_filename.read_bytes()
            })

        # Bind the state variables
        for (path, statevar_class) in v1.state_vars.items():
            infoset.put(f'.state.{path}', statevar_class(cell=infoset))

        return infoset

    def fetch(self, id: str) -> Infoset:
        self.log.info('searching for cell', id=id)

        for path in self.basepath.glob('**/meta.json'):
            try:
                infoset = self._load_cell_infoset(path)
                if infoset.fetch('.id') == id:
                    return infoset
            except Exception as e:
                pass
        else:
            return None

    def put(self, infoset: Infoset):
        self.log.info('storing cell', cell_id=infoset.fetch('.id'), path=infoset.fetch('.path'))

        if infoset.fetch('.path') is not None and infoset.fetch('.path') != '/':
            path = infoset.fetch('.path').lstrip('/')
        else:
            path = ''

        location = Path(self.basepath).joinpath(path, infoset.fetch('.id'))

        location.mkdir(parents=True, exist_ok=True)

        self.log.debug('cell location', location=location)
        with open(location.joinpath('meta.json'), 'w') as f:
            f.write(f"V0\n")
            f.write(json.dumps(infoset.fetch('.props')))

        location.joinpath('log.json').write_text(json.dumps(infoset.fetch('.log')) )

        for extra in infoset.fetch('.extra'):
            # TODO: Restore file ctime and mtime from props
            location.joinpath(extra['name']).write_bytes(extra['content'])

    def find(self) -> Infoset: # Generator

        for path in self.basepath.glob('**/meta.json'):
            try:
                infoset = self._load_cell_infoset(path)
                if infoset.fetch('.id'):
                    self.log.debug('cell found', path=path)
                    yield infoset

            except Exception as e:
                self.log.error('cannot load cell', path=path, _exc_info=e)

v1.register_celldb_backend('json-files', JsonFiles)