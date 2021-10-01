#!/usr/bin/env python3

import struct
import time
from secondlife.plugins.api import v1
from structlog import get_logger
import os

from .lcd_sniffer import fetch_charger_lcd
from .charger_specs import lii500_current_setups

log = get_logger()


def load_charger_ports_file(filename):
    log.debug('loading charger ports', filename=filename)

    ports = dict()

    with open(filename) as f:
        for line in f.readlines():
            line = line.rstrip()
            if len(line) == 0:
                continue
            (id, port) = line.split(' ')
            log.debug('charger port', id=id, port=port)
            ports[id] = port

    log.info('charger ports loaded', filename=filename, port_count=len(ports.keys()) )

    return ports


class Lii500Meter(object):

    def __init__(self, **kwargs):
        self.config = kwargs['config']

    def measurement_from_charger(self, port, config):

        lcd_state = fetch_charger_lcd(port)

        if lcd_state.get('null', False) is True:
            log.error('no cell present', lcd=lcd_state)
            return None

        if lcd_state.get('mode', '') != 'nor test':
            log.error('invalid test mode', lcd=lcd_state)
            return None

        if not lcd_state.get('end'):
            log.error('test not finished', lcd=lcd_state)
            return None

        if lcd_state.get('capacity', None) is None:
            log.error('no capacity result', lcd=lcd_state)
            return None

        result = {
            'type': 'measurement', 'event': 'finished', 'ts': time.time(),
            'equipment': dict(brand='Liitokala', model='Engineer LI-500', port=port),
            'setup': dict(mode_setting='NOR TEST', slot=lcd_state['cell_select']),
            'results': {}
        }

        result['setup'].update( lii500_current_setups[lcd_state['current_select']] )

        (capa_v, capa_u) = lcd_state['capacity'].split()
        result['results']['capacity'] = dict(u=capa_u, v=float(capa_v))

        if lcd_state.get('ir', None) is not None:
            (ir_v, ir_u) = lcd_state['ir'].split()
            result['results']['ir'] = dict(u='mOhm', v=float(ir_v))

        return result

    def manual_result_entry(self, config):

        capa = None
        ir = None

        while capa is None or ir is None:

            if capa is None:
                try:
                    capa = float(input('Capacity [mAh] > '))
                except ValueError:
                    continue

            if ir is None:
                try:
                    ir = float(input('IR [mOhm] > '))
                except ValueError:
                    continue

        result = {
            'type': 'measurement', 'event': 'finished', 'ts': time.time(),
            'equipment': dict(brand='Liitokala', model='Engineer LI-500'),
            'setup': dict(mode_setting='NOR TEST'),
            'results': {
                'capacity': dict(u='mAh', v=capa),
                'IR': dict(u='mOhm', v=ir)
            }
        }

        result['setup'].update( lii500_current_setups[config.lii500_current_setting] )
        return result

    def measure(self, config):

        result = None
        charger_select = None

        lii500_port = config.lii500_port

        if lii500_port is None and config.lii500_ports_file is not None:
            ports = load_charger_ports_file(config.lii500_ports_file)

            charger_select = config.lii500_select

            if not charger_select:
                charger_select = input('Lii-500 Charger Select > ')

            if charger_select in ports:
                lii500_port = ports[charger_select]
            else:
                log.warn('unknown charger selector', select=charger_select)

        try:
            result = self.measurement_from_charger(lii500_port, config=config)
        except Exception as e:
            log.warn('exception while trying to fetch from charger', port=lii500_port, _exc_info=e)

        if result is None:
            log.warn('cannot fetch result from charger', port=lii500_port)
            result = self.manual_result_entry(config=config)

        # Always store charger selector
        if charger_select is not None:
            result['equipment']['selector'] = charger_select

        return result


def _config_group(parser):
    group = parser.add_argument_group('lii500')
    group.add_argument('--lii500-port', default=os.getenv('LII500_PORT', None),
        help='Serial port used by the Lii-500 charger USB interface')
    group.add_argument('--lii500-current-setting', choices=['300mA', '500 mA', '700 mA', '1000 mA'], default='500 mA',
        help='Current setting of the Lii-500 charger')
    group.add_argument('--lii500-select', default=None, metavar='ID', help='Select the specified charger from the ports file')
    group.add_argument('--lii500-ports-file', default=os.getenv('LII500_PORTS_FILE', None),
        help='The file specifying serial ports for particular chargers')


v1.register_measurement(v1.Measurement('capa', Lii500Meter))
v1.register_config_group('capa', _config_group)
