#!/usr/bin/env python3

from secondlife.plugins.api import v1
from structlog import get_logger
import asciitable
import json

class InfosetReport(object):

    def __init__(self, **kwargs):
        self.config = kwargs['config']
        self.log = get_logger(name=__class__.__name__)
        self.cells = dict()

    def process_cell(self, infoset):
        log = self.log.bind(id=infoset.fetch('.id'))
        log.debug('processing cell')

        self.cells[infoset.fetch('.id')] = infoset.to_json(indent=2)

    def report(self, format='ascii'):
        if format == 'ascii':
            if len(self.cells.items()) > 0:
                for (id, infoset) in self.cells.items():
                    print(f"=== Infoset for {id}")
                    print(infoset)
            else:
                self.log.warning('no data')
        else:
            log.error('unknown report format', format=format)

v1.register_report(v1.Report('infoset', InfosetReport))
