#!/usr/bin/env python3

from secondlife.plugins.api import v1
from structlog import get_logger
import asciitable

log = get_logger()

class SelfDischargeReport(object):

    def __init__(self, **kwargs):
        self.config = kwargs['config']
        self.log = get_logger()
        self.data = {}

    def process_cell(self, infoset):
        log = self.log.bind(id=infoset.fetch('.id'))
        log.debug('processing cell')

        sd_rate = infoset.fetch('.state.self_discharge')
        if sd_rate is not None:
            self.data[infoset.fetch('.id')] = sd_rate
        else:
            log.warn('no self-discharge estimation')

    def report(self, format='ascii'):
        if format == 'ascii':
            if len(self.data.keys()) > 0:
                asciitable.write([ (id, round(sd['v'], 3)) for (id, sd) in self.data.items() ],
                    names=['Cell ID', 'Self-discharge [mV / day]'],
                    formats={ 'Cell ID': '%s', 'Self-discharge [mV / day]': '%s'},
                    Writer=asciitable.FixedWidth)
            else:
                self.log.warning('no data')
        else:
            log.error('unknown report format', format=format)

class SelfDischargeRate(object):
    def __init__(self, **kwargs):
        self._cell = kwargs['cell']

    @staticmethod
    def _capacity_measurement(m):
        if 'capacity' in m['results']:
            return True
        else:
            return False

    @staticmethod
    def _ocv_measurement(m):
        if 'OCV' in m['results']:
            return True
        else:
            return False

    def fetch(self, path, default=None):
        try:
            event_log = self._cell.fetch('.log')
            measurement_log = list(filter(lambda m: 'results' in m, event_log))

            log.debug('measurements', entries=measurement_log)

            last_capacity_measurement_idx = next( 
                filter( lambda idx: SelfDischargeRate._capacity_measurement(measurement_log[idx]), reversed(range(0, len(measurement_log))) ), 
                None)
            if last_capacity_measurement_idx is None:
                log.warn('no timestamped capacity measurement', id=self._cell.fetch('.id'))
                return None
            last_capacity_measurement = measurement_log[last_capacity_measurement_idx]

            # Now search for the OCV measurement after capacity measurement
            # (assume the cell was charged up to 100% during the capacity measurement)
            ocv_measurement = next(
                filter( lambda m: SelfDischargeRate._ocv_measurement(m), measurement_log[last_capacity_measurement_idx:] ),
                None
            )
            if ocv_measurement is None:
                log.warn('no OCV measurement after capacity measurement', id=self._cell.fetch('.id'))
                return None

            log.debug('capacity measurement', m=last_capacity_measurement)
            log.debug('ocv measurement', m=ocv_measurement)

            T = (ocv_measurement['ts'] - last_capacity_measurement.get('ts', 0)) / (3600 * 24)
            if T < 21:
                log.warn('not enough days between capacity and OCV measurements', id=self._cell.fetch('.id'), T=T)
                return None
            
            # Assume the cell resting voltage is at 4.1V after charging
            deltaV = 4.1 - ocv_measurement['results']['OCV']['v']

            log.debug('self-discharge estimation', id=self._cell.fetch('.id'), T=T, deltaV=deltaV)

            return { 'v': (deltaV * 1000)/T, 'u': 'mV / day' }

        except Exception as e:
            log.error('exception', _exc_info=e)
            return None


v1.register_state_var('self_discharge', SelfDischargeRate)
v1.register_report(v1.Report('self_discharge', SelfDischargeReport))
