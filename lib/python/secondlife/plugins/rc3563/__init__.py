#!/usr/bin/env python3

import serial
import time
import struct
from secondlife.plugins.api import v1
import os

from structlog import get_logger

log = get_logger()

class RC3563Meter(object):

    def __init__(self, **kwargs):
        self.config = kwargs['config']

    def _parse_rc3546_packet(self, pkt):
        global log

        log.debug('pkt', pkt=pkt)        
        
        status_disp, r_range_code, r_disp, sign_code, v_range_code, v_disp = struct.unpack('BB3s BB3s', pkt)
        result = {}

        #print(f"status_disp='{status_disp:#x}'")

        r_disp = struct.unpack('I', r_disp + b'\x00')[0]
        resistance = float(r_disp) / 1e4

        r_disp_code = (status_disp & 0xF0) >> 4

        if r_disp_code == 0x05:
            r_unit_disp = 'mOhm'
        elif r_disp_code == 0x06:
            r_unit_disp = 'mOhm'
            resistance = 'OL'
        elif r_disp_code == 0x09:
            r_unit_disp = 'Ohm'
        elif r_disp_code == 0x0a:
            r_unit_disp = 'Ohm'
            resistance = 'OL'
        else:
            print(f"Unknown display code '{r_status_disp_code:#x}'")

        #print(f"r_disp_code='{r_disp_code:#x}' r_unit_disp='{r_unit_disp}'")

        r_unit = r_unit_disp

        if r_range_code == 1:
            r_range = '0-20 mΩ'
            r_range_unit = 'mΩ'
        elif r_range_code == 2:
            r_range = '0-200 mΩ'
            r_range_unit = 'mΩ'
        elif r_range_code == 3:
            r_range = '0-2 Ω'
            r_range_unit = 'Ω'
        elif r_range_code == 4:
            r_range = '0-20 Ω'
            r_range_unit = 'Ω'
        elif r_range_code == 5:
            r_range = '0-200 Ω'
            r_range_unit = 'Ω'
        elif r_range_code == 6:
            r_range = 'AUTO'
            r_range_unit = None
        else:
            r_range = None
            r_range_unit = None
            print(f"Unknown resistance range code '{r_range_code:#x}'")

        if r_range_unit and r_unit_disp != r_range_unit:
            print(f"Display unit '{r_unit_disp}' override by range unit '{r_range_unit}' for selected range '{r_range}'")

            # Range unit has preference
            r_unit = r_range_unit

        log.debug('ir', range=r_range, v=resistance, u=r_unit)
        result['IR'] = dict(range=r_range, v=resistance, u=r_unit)

        sign_multiplier = None
        if sign_code == 1:
            sign_multiplier = 1.0
        elif sign_code == 0:
            sign_multiplier = -1.0
        else:
            print(f"Unknown sign code '{sign_code:#x}'")

        v_disp = struct.unpack('I', v_disp + b'\x00')[0]
        voltage = sign_multiplier * float(v_disp) / 1e4

        v_disp_code = ( status_disp & 0x0F )
        if v_disp_code == 0x04:
            pass # Nop, everything is OK
        elif v_disp_code == 0x08:
            voltage = 'OL'

        if v_range_code == 1:
            v_range = '0-20 V'
        elif v_range_code == 2:
            v_range = '0-100 V'
        elif v_range_code == 3:
            v_range = 'AUTO'
        else:
            v_range = 'Unknown'
            print(f"Unknown voltage range code '{v_range_code:#x}'")

        log.debug('ocv', range=v_range, v=voltage, unit='V')
        result['OCV'] = dict(range=v_range, unit='V', v=voltage)

        return result


    def measure(self, config):

        with serial.Serial(config.rc3563_port, 115200) as ser:
            mq = []
            result = None
            while True:
                pkt = ser.read(10)
                mq.append(self._parse_rc3546_packet(pkt))
                if len(mq) >= 3:
                    # Check if all measurements are identical
                    if mq[0]['OCV'] == mq[1]['OCV'] == mq[2]['OCV'] and mq[0]['IR'] == mq[1]['IR'] == mq[2]['IR']:
                        result = mq[0]

                        if result['IR']['v'] == 'OL':
                            # Repeat if open loop condition is detected, likely no cell has been inserted
                            log.warn("no cell inserted", result=result)
                            mq = []
                            continue
                        else:
                            # We have a valid measurement
                            break

                    # Maintain a rolling queue of last 3 measurements
                    mq.pop(0)

            if result:
                log.info('measurement results', results=result)
                return dict(action='measurement', ts=time.time(), equipment=dict(model='RC3563'), results=result)
            else:
                return None

def _config_group(parser):
    group = parser.add_argument_group('rc3563')
    group.add_argument('--rc3563-port', default=os.getenv('RC3563_PORT', '/dev/ttyUSB0'), help='Serial port connected to the RC3563 meter')

v1.register_measurement(v1.Measurement('rc', RC3563Meter))
v1.register_config_group('rc', _config_group)