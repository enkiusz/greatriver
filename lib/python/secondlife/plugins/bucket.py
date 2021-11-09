#!/usr/bin/env python3

from secondlife.plugins.api import v1
import structlog

log = structlog.get_logger()


def _odd_even(d):
    return 'P' if d % 2 == 0 else 'N'


class Bucket(object):
    def __init__(self, **kwargs):
        self._cell = kwargs['cell']

    def fetch(self, path, default=None):
        try:
            (prefix, num) = self._cell.fetch('.id').split('~')

            if prefix is None or num is None:
                return None
            if len(num) < 3:
                return None

            return f'{num[0:2]}{_odd_even(int(num[2]))}'
        except ValueError as e:
            log.warn('cannot determine bucket', id=self._cell.fetch('.id'))
            return None


v1.register_state_var('bucket', Bucket)
