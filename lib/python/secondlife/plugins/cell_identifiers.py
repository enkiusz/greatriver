#!/usr/bin/env python3

from secondlife.plugins.api import v1
from structlog import get_logger


class CellIdentifiers(object):

    def __init__(self, **kwargs):
        self.config = kwargs['config']
        self.log = get_logger(name=__class__.__name__)
        self.ids = []

    def process_cell(self, infoset):
        log = self.log.bind(id=infoset.fetch('.id'))
        log.debug('processing cell')

        self.ids.append(infoset.fetch('.id'))

    def report(self, format='ascii'):
        if format == 'ascii':
            print('\n'.join(self.ids))
        else:
            log.error('unknown report format', format=format)


v1.register_report(v1.Report('cell_ids', CellIdentifiers, default_enable=True))
