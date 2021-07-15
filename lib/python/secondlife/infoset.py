#!/usr/bin/env python3

import json

class Infoset(object):
    def __init__(self, data=None, **kwargs):
        self._data = data or {}

    @property
    def data(self):
        return self._data

    def paths(self, path='.'):
        paths = [ path ]
        try:
            for (d, v) in self._find(path).items():
                if hasattr(v, 'paths'):
                    paths.extend( [ f'{path}.{d}.{p}'.replace('..', '.').rstrip('.') for p in v.paths() ] )
                else:
                    paths.extend( self.paths(f'{path}.{d}'.replace('..', '.').rstrip('.')) )
        except AttributeError: # Pass if we've reached a level we can't enumerate anymore
            pass
        return paths

    def _find(self, path, mkpath=False):
        r = self.data
        path = path.split('.')
        while len(path) > 0:
            if hasattr(r, '_find'):
                # Delegate if we reached another infoset
                return r._find('.'.join(path), mkpath=mkpath)

            item = path.pop(0)
            if not item: # Skip empty path elements
                continue

            if (not item in r) and mkpath:
                r[item] = {}

            r = r[item]

        return r

    def put(self, path, data):
        p = path.split('.')
        d = self._find('.'.join(p[:-1]), mkpath=True)

        if hasattr(d, 'put'):
            d.put(p[-1], data)
        else:
            d[ p[-1] ] = data

    def fetch(self, path, default=None):
        try:
            v = self._find(path)
            if hasattr(v, 'fetch'):
                return v.fetch('')
            else:
                return v
        except KeyError:
            return default

    def to_json(self, **kwargs):
        return json.dumps(self, default=_infoset_encoder, **kwargs)

def _infoset_encoder(v):
    if hasattr(v, 'fetch'):
        return v.fetch('.')
    elif isinstance(v, bytes):
        return f'bytes(len={len(v)})'
    else:
        raise TypeError(f"Object of type {v.__class__.__name__} is not serializable")
