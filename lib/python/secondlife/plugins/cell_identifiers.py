#!/usr/bin/env python3

from secondlife.plugins.api import v1
from structlog import get_logger

class CellIdentifiers(object):

    def __init__(self, **kwargs):
        self.config = kwargs['config']
        self.log = get_logger(name=__class__.__name__)
        self.ids = []

    def process_cell(self, path, metadata):
        log = self.log.bind(path=path)
        log.debug('processing cell')

        self.ids.append(metadata.get('/id'))

    def report(self):

        print('\n'.join(self.ids))

v1.register_report(v1.Report('cell_ids', CellIdentifiers))
