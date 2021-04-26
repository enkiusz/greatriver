#!/usr/bin/env python3

import os

class VFS(object):
    def __init__(self, data=None, **kwargs):
        self._data = data or {}

    @property
    def data(self):
        return self._data

    def paths(self, path='/'):
        paths = [ path ]
        try:
            for d in self._find(path).keys():
                paths.extend( self.paths( os.path.join(path, d) ))
        except AttributeError: # Pass if we've reached a level we can't enumerate anymore
            pass
        return paths

    def _find(self, path, mkpath=False):
        r = self._data
        for item in path.split('/'):
            if not item: # Skip empty path elements
                continue
            if not item in r:
                if not mkpath:
                    return None
                else:
                    r[item] = {}

            r = r.get(item)
        return r

    def put(self, path, data):
        p = path.split('/')

        d = self._find('/'.join(p[:-1]), mkpath=True)
        d[ p[-1] ] = data

    def get(self, path):
        return self._find(path)