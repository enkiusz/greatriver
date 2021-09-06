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

        sd_check_res = infoset.fetch('.state.self_discharge.sd_check_result')
        if sd_check_res is not None:
            self.data[infoset.fetch('.id')] = sd_check_res
        else:
            log.debug('no self-discharge check result')

    def report(self, format='ascii'):
        if format == 'ascii':
            if len(self.data.keys()) > 0:
                asciitable.write([ (id, sd_check_result) for (id, sd_check_result) in self.data.items() ],
                    names=['Cell ID', 'Check result'],
                    formats={ 'Cell ID': '%s', 'Check result': '%s'},
                    Writer=asciitable.FixedWidth)
            else:
                self.log.warning('no data')
        else:
            log.error('unknown report format', format=format)

class SelfDischargeCheckResult(object):
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
                filter( lambda idx: SelfDischargeCheckResult._capacity_measurement(measurement_log[idx]), reversed(range(0, len(measurement_log))) ),
                None)
            if last_capacity_measurement_idx is None:
                log.debug('no timestamped capacity measurement', id=self._cell.fetch('.id'))
                return None
            last_capacity_measurement = measurement_log[last_capacity_measurement_idx]

            # Now search for the OCV measurements after capacity measurement
            # (assume the cell was charged up to 100% during the capacity measurement)
            ocv_measurements = list(
                filter( lambda m: SelfDischargeCheckResult._ocv_measurement(m), measurement_log[last_capacity_measurement_idx:] )
            )

            if len(ocv_measurements) == 0:
                log.debug('no OCV measurement after capacity measurement', id=self._cell.fetch('.id'))
                return None

            log.debug('capacity measurement', m=last_capacity_measurement)
            log.debug('ocv measurements', m=ocv_measurements)

            result = None
            for ocv_measurement in ocv_measurements:
                T = (ocv_measurement['ts'] - last_capacity_measurement.get('ts', 0)) / (3600 * 24)
                if T < 21:
                    log.debug('not enough days between capacity and OCV measurement', id=self._cell.fetch('.id'), T=T, ocv_measurement=ocv_measurement)
                    continue
            
                if ocv_measurement['results']['OCV']['v'] < 3.9:
                    result = 'FAIL'
                else:
                    result = 'PASS'

            log.debug('self-discharge check', id=self._cell.fetch('.id'), result=result)

            return result

        except Exception as e:
            log.error('exception', _exc_info=e)
            return None


v1.register_state_var('self_discharge.assessment', SelfDischargeCheckResult)
v1.register_report(v1.Report('self_discharge', SelfDischargeReport))
