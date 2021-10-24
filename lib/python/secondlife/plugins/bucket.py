#!/usr/bin/env python3

from secondlife.plugins.api import v1


def _odd_even(d):
    return 'P' if d % 2 == 0 else 'N'

class Bucket(object):
    def __init__(self, **kwargs):
        self._cell = kwargs['cell']

    def fetch(self, path, default=None):
        (prefix, num) = self._cell.fetch('.id').split('~')

        return f'{num[0:2]}{_odd_even(int(num[2]))}'


v1.register_state_var('bucket', Bucket)
