#!/usr/bin/env python3

from secondlife.plugins.api import v1
from structlog import get_logger
from dateutil.relativedelta import relativedelta
import asciitable
import json
import pint

ureg = pint.UnitRegistry(case_sensitive=False)


class InternalResistanceReport(object):

    def __init__(self, **kwargs):
        self.config = kwargs['config']
        self.log = get_logger(name=__class__.__name__)
        self.data = {}

    def process_cell(self, infoset):
        log = self.log.bind(id=infoset.fetch('.id'))
        log.debug('processing cell')

        internal_resistance = infoset.fetch('.state.internal_resistance')
        if internal_resistance is not None:
            self.data[infoset.fetch('.id')] = internal_resistance
        else:
            log.debug('no IR measurement')

    def report(self, format='ascii'):
        if format == 'ascii':
            if len(self.data.keys()) > 0:
                asciitable.write([ (id, float(ir['v'])) for (id, ir) in self.data.items() ],
                    names=['Cell ID', 'IR [mΩ]'],
                    formats={ 'Cell ID': '%s', 'IR [mΩ]': '%s'},
                    Writer=asciitable.FixedWidth)
            else:
                self.log.warning('no data')
        else:
            log.error('unknown report format', format=format)


class InternalResistance(object):
    def __init__(self, **kwargs):
        self._cell = kwargs['cell']

    def fetch(self, path, default=None):
        try:
            measurement_log = self._cell.fetch('.log')

            ir_measurements = list(filter(lambda m: 'IR' in m.get('results', {}), measurement_log))

            # Search for RC3563, the the last IR measurement if this is not found
            rc3563_measurements = list(filter(lambda m: m['equipment']['model'] == 'RC3563', ir_measurements))
            if len(rc3563_measurements) > 0:
                last_measurement = rc3563_measurements[-1]  # Last measurement is the newest one
            else:
                last_measurement = ir_measurements[-1]  # Last measurement is the newest one

            # Convert to alway be represented in milliohms
            ir_measurement = last_measurement['results']['IR']
            ir_quantity = ir_measurement['v'] * ureg.parse_units(ir_measurement['u'])
            ir_measurement['u'] = 'mOhm'
            ir_measurement['v'] = ir_quantity.to('mOhm').magnitude

            return ir_measurement
        except Exception as e:
            return None


v1.register_state_var('internal_resistance', InternalResistance)
v1.register_report(v1.Report('ir', InternalResistanceReport))
