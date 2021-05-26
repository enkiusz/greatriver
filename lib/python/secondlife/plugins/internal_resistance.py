#!/usr/bin/env python3

from secondlife.plugins.api import v1
from structlog import get_logger
from dateutil.relativedelta import relativedelta
import asciitable
import json

class InternalResistanceReport(object):

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
            ir_measurements = list(filter(lambda m: 'IR' in m.get('results',{}), measurement_log))

            # Search for RC3563, the the last IR measurement if this is not found
            rc3563_measurements = list(filter(lambda m: m['equipment']['model'] == 'RC3563', ir_measurements))
            if len(rc3563_measurements) > 0:
                ir_measurement = rc3563_measurements[-1] # Last measurement is the newest one
            else:
                ir_measurement = ir_measurements[-1] # Last measurement is the newest one

            self.data[metadata.get('/id')] = ir_measurement['results']['IR']['v']
        except Exception as e:
            log.warn('no IR measurement', path=path, _exc_info=e)
            pass

    def report(self):

        if len(self.data.keys()) > 0:
            asciitable.write([ (id, ir) for (id, ir) in self.data.items() ], 
                names=['Cell ID', 'IR [mΩ]'], 
                formats={ 'Cell ID': '%s', 'IR [mΩ]': '%s'},
                Writer=asciitable.FixedWidth)
        else:
            self.log.warning('no data')

v1.register_report(v1.Report('ir', InternalResistanceReport))
