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
        return ' '.join([ '%d %s' % (getattr(delta, attr), getattr(delta, attr) > 1 and attr or attr[:-1])
                for attr in _attrs if getattr(delta, attr) ])
    except:
        return ''

def _format_results(results):
    r = []
    for (name,value) in results.items():
        r.append(f"{name}={value['v']}{value.get('u', value.get('unit'))}")
    
    return ' '.join(r)

class CapacityReport(object):

    def __init__(self, **kwargs):
        self.config = kwargs['config']
        self.log = get_logger(name=__class__.__name__)
        self.rows = []

    def process_cell(self, path, metadata):
        log = self.log.bind(path=path)
        log.debug('processing cell')

        try:
            log_path = path.with_name('log.json')
            measurement_log = json.loads(log_path.read_text(encoding='utf8'))
        except Exception as e:
            log.error('cannot read log', _exc_info=e)
            return
    

        # log.debug('measurement log', log=measurement_log)
    
        rows = []
        for m in measurement_log:
            rows.append([
                _human_readable(relativedelta(seconds=m.get('ts')-time.time())) if 'ts' in m else '',
                _format_results(m.get('results'))
            ])

        # print(f"Cell measurement log:")
        # asciitable.write(rows, names=['Timestamp', 'Results'], Writer=asciitable.FixedWidth)

        try:
            capacity_measurement = next(filter(lambda m: 'capacity' in m['results'], measurement_log))
            self.rows.append([ metadata.get('/id'), capacity_measurement['results']['capacity']['v'] ])
        except StopIteration:
            log.warn('no capacity measurement', metadata=metadata, path=path)
            pass

    def report(self):

        if len(self.rows) > 0:
            asciitable.write(self.rows, 
                names=['Cell ID', 'Capacity [mAh]'], 
                formats={ 'Cell ID': '%s', 'Capacity [mAh]': '%s'},
                Writer=asciitable.FixedWidth)
        else:
            self.log.warning('no data')

        print(','.join([ str(r[1]) for r in self.rows ]))

        print("TOTAL Capacity [mAh]:")
        print(sum([ float(r[1]) for r in self.rows ]))

v1.register_report(v1.Report('capacity', CapacityReport))
