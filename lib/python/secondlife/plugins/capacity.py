#!/usr/bin/env python3

from secondlife.plugins.api import v1
from structlog import get_logger
from dateutil.relativedelta import relativedelta
import asciitable
import json
import time

class CapacityReport(object):

    def __init__(self, **kwargs):
        self.config = kwargs['config']
        self.log = get_logger(name=__class__.__name__)
        self.data = {}

    def process_cell(self, path, metadata):
        log = self.log.bind(path=path)
        log.debug('processing cell')

        try:
            log_path = path.with_name('log.json')
            measurement_log = json.loads(log_path.read_text(encoding='utf8'))
        except Exception as e:
            log.error('cannot read log', _exc_info=e)
            return
        try:
            capacity_measurement = next(filter(lambda m: 'capacity' in m.get('results',{}), measurement_log))
            self.data[metadata.get('/id')] = capacity_measurement['results']['capacity']['v']
        except StopIteration:
            log.warn('no capacity measurement', path=path)
            pass

    def report(self):

        if len(self.data.keys()) > 0:
            asciitable.write([ (id, capacity) for (id, capacity) in self.data.items() ],
                names=['Cell ID', 'Capacity [mAh]'], 
                formats={ 'Cell ID': '%s', 'Capacity [mAh]': '%s'},
                Writer=asciitable.FixedWidth)
        else:
            self.log.warning('no data')

v1.register_report(v1.Report('capacity', CapacityReport))
