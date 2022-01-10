#!/usr/bin/env python3

from secondlife.plugins.api import v1
from structlog import get_logger
import asciitable

log = get_logger()


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

    # Self-discharge data:
    #
    # For fully charged cells:
    #
    # After a full charge (4.2V) a healthy cell's voltage first drops quickly from to 4.15 V within 8h. After that the voltage drop
    # is constant and around 7mV/day
    #
    # Reference: https://batteryuniversity.com/article/bu-802b-what-does-elevated-self-discharge-do
    #
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

            # If no OCV after capacity measurement assume 4.2V (full charge)
            #
            ocv1 = (4.2, last_capacity_measurement['ts'])
            if 'OCV' in last_capacity_measurement['results']:
                ocv1 = (last_capacity_measurement['results']['OCV']['v'], last_capacity_measurement['ts'])

            # If the cell has been fully charged after capacity measurement assume voltage drops to 4.15 V within 8h and
            # start from there
            if ocv1[0] >= 4.15:
                ocv1 = (4.15, ocv1[1] + 8 * 3600)

            # Now search for the OCV measurements after capacity measurement
            ocv_measurements = list(
                filter( lambda m: SelfDischargeCheckResult._ocv_measurement(m), measurement_log[last_capacity_measurement_idx + 1:] )
            )

            if len(ocv_measurements) == 0:
                log.debug('no OCV measurement after capacity measurement', id=self._cell.fetch('.id'))
                return None

            log.debug('capacity measurement', m=last_capacity_measurement, ocv1=ocv1)
            log.debug('ocv measurements', m=ocv_measurements)

            voltage_drop = None
            result = None
            for ocv_measurement in ocv_measurements:
                T = (ocv_measurement['ts'] - ocv1[1]) / (3600 * 24)
                if T < 21:
                    log.debug('not enough days between capacity and OCV measurement', id=self._cell.fetch('.id'), T=T,
                        ocv_measurement=ocv_measurement)

                    continue

                # Calculate voltage drop in mV / day
                voltage_drop = (ocv_measurement['results']['OCV']['v'] - ocv1[0]) * 1000
                voltage_drop = voltage_drop / T

                # Acceptable voltage drop is 8 mV / day
                if voltage_drop < -8:
                    result = 'FAIL'
                else:
                    result = 'PASS'

            log.debug('self-discharge check', id=self._cell.fetch('.id'), T=T, voltage_drop=f'{voltage_drop} mV/day', result=result)

            return dict(assessment=result, v=voltage_drop, u='mV/day')

        except Exception as e:
            log.error('exception', _exc_info=e)
            return None


v1.register_state_var('self_discharge', SelfDischargeCheckResult)
