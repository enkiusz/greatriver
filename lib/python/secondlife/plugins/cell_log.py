#!/usr/bin/env python3

from secondlife.plugins.api import v1
from structlog import get_logger
from dateutil.relativedelta import relativedelta
import asciitable
import json
import time

# We care only about hour level accuracy
_attrs = ['years', 'months', 'days', 'hours']
def _human_readable(delta):
    try:
        return ' '.join([ '%d %ss' % (getattr(delta, attr), getattr(delta, attr) > 1 and attr or attr[:-1])
                for attr in _attrs if getattr(delta, attr) ])
    except:
        return ''

def _format_results(results):
    r = []
    for (name,value) in results.items():
        r.append(f"{name}={value['v']}{value.get('u', value.get('unit'))}")
    
    return ' '.join(r)

class LogReport(object):

    def __init__(self, **kwargs):
        self.config = kwargs['config']
        self.log = get_logger(name=__class__.__name__)
        self.cells = dict()

    def process_cell(self, infoset):
        log = self.log.bind(id=infoset.fetch('.id'))
        log.debug('processing cell')

        measurement_log = infoset.fetch('.log')
    
        log.debug('measurement log', log=measurement_log)

        self.cells[infoset.fetch('.id')] = [
            [
                _human_readable(relativedelta(seconds=m.get('ts')-time.time())) if 'ts' in m else '',
                _format_results(m.get('results')) if m.get('results') else str(m)
            ] for m in measurement_log
        ]

    def report(self):

        if len(self.cells.items()) > 0:
            for (id, rows) in self.cells.items():
                print(f"=== Log for {id}")
                asciitable.write(rows, names=['Timestamp', 'Results'], Writer=asciitable.FixedWidth)
        else:
            self.log.warning('no data')

v1.register_report(v1.Report('log', LogReport))
