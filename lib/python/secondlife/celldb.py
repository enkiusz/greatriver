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

        infoset = Infoset()
        infoset.put('.id', id)
        infoset.put('.path', path)
        infoset.put('.props', Infoset())
        infoset.put('.log', [ dict(type='lifecycle', event='created', ts=time.time(), path=path) ])
        infoset.put('.extra', [])

        return infoset

    def fetch(self, id: str) -> Infoset:
        raise NotImplementedError()

    def put(self, infoset: Infoset):
        raise NotImplementedError()

    def find(self) -> Infoset: # Generator
        raise NotImplementedError()
