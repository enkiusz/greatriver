#!/usr/bin/env python3

from secondlife.plugins.api import v1
from structlog import get_logger
import asciitable
import json

class MetadataReport(object):

    def __init__(self, **kwargs):
        self.config = kwargs['config']
        self.log = get_logger(name=__class__.__name__)
        self.cells = dict()

    def process_cell(self, path, metadata):
        log = self.log.bind(path=path)
        log.debug('processing cell')

        self.cells[metadata.get('/id')] = metadata

    def report(self):

        if len(self.cells.items()) > 0:
            for (id, metadata) in self.cells.items():
                print(f"=== Metadata for {id}")
                print(json.dumps(metadata._data, indent=2))
        else:
            self.log.warning('no data')

v1.register_report(v1.Report('meta', MetadataReport))
