#!/usr/bin/env python3

from secondlife.utils import Infoset

class CellDB(object):
    def __init__(self):
        pass

    def create(self, id: str) -> Infoset:
        raise NotImplementedError()

    def fetch(self, id: str) -> Infoset:
        raise NotImplementedError()

    def put(self, infoset: Infoset):
        raise NotImplementedError()

    def find(self) -> Infoset: # Generator
        raise NotImplementedError()
