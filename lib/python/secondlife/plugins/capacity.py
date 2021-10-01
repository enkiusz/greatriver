#!/usr/bin/env python3

from secondlife.plugins.api import v1
from structlog import get_logger
import asciitable


class CapacityReport(object):

    def __init__(self, **kwargs):
        self.config = kwargs['config']
        self.log = get_logger(name=__class__.__name__)
        self.data = {}

    def process_cell(self, infoset):
        log = self.log.bind(id=infoset.fetch('.id'))
        log.debug('processing cell')

        usable_capacity = infoset.fetch('.state.usable_capacity')
        if usable_capacity is not None:
            self.data[infoset.fetch('.id')] = usable_capacity
        else:
            log.debug('no capacity measurement')

    def report(self, format='ascii'):
        if format == 'ascii':
            if len(self.data.keys()) > 0:
                asciitable.write([ (id, float(capacity['v'])) for (id, capacity) in self.data.items() ],
                    names=['Cell ID', 'Capacity [mAh]'],
                    formats={ 'Cell ID': '%s', 'Capacity [mAh]': '%s'},
                    Writer=asciitable.FixedWidth)
            else:
                self.log.warning('no data')
        else:
            log.error('unknown report format', format=format)


class UsableCapacity(object):
    def __init__(self, **kwargs):
        self._cell = kwargs['cell']

    def fetch(self, path, default=None):
        try:
            measurement_log = self._cell.fetch('.log')

            capacity_measurement = next(filter(lambda m: 'capacity' in m.get('results', {}), measurement_log))
            return capacity_measurement['results']['capacity']
        except StopIteration:
            return None


v1.register_state_var('usable_capacity', UsableCapacity)
v1.register_report(v1.Report('capacity', CapacityReport))
