#!/usr/bin/env python3

from secondlife.infoset import Infoset
import structlog
import time

log = structlog.get_logger()


class CellDB(object):
    def __init__(self):
        pass

    def init(self, dsn):
        raise NotImplementedError()

    def create(self, id: str, path: str) -> Infoset:
        log.debug('creating cell', cell_id=id)
        if not self.path_valid(path):
            log.error('path not valid', path=path)
            return None

        infoset = Infoset()
        infoset.put('.id', id)
        infoset.put('.path', path)
        infoset.put('.props', Infoset())
        infoset.put('.log', [ dict(type='lifecycle', event='created', ts=time.time(), path=path) ])
        infoset.put('.extra', [])

        return infoset

    def path_valid(self, path: str) -> bool:
        log.debug('checking path validity', path=path)

        if path[0] != '/':
            log.error('path needs to start with /', path=path)
            return False

        for part in path[1:].split('/'):  # Ignore first /
            if len(part) == 0:
                continue
            if self.fetch(part) is None:
                log.error('path part does not exist', path=path, part=part)
                return False
        return True

    def fetch(self, id: str) -> Infoset:
        raise NotImplementedError()

    def put(self, infoset: Infoset):
        raise NotImplementedError()

    def move(self, id: str, destination: str):
        raise NotImplementedError()

    def find(self) -> Infoset:  # Generator
        raise NotImplementedError()
