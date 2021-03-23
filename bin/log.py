#!/usr/bin/env python3

import sys
import argparse
from structlog import get_logger
from pathlib import Path
import os
import io
import json
import time
import serial
import struct

log = get_logger()

def load_metadata(filename):
    with open(filename) as f:

        version_token = f.readline().rstrip()
        if version_token != 'V0':
            raise RuntimeError(f"Version '{version_token}' not supported")
        
        j = json.loads(f.read())
        return j

def find_cell(cell_id):
    p = Path()
    for path in p.glob('**/meta.json'):
        try:
            metadata = load_metadata(path)
            if metadata['id'] == cell_id:
                return (path, metadata)
        except:
            pass
    else:
        return (None, None)

def parse_rc3546_packet(pkt):
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

    print(f"RESISTANCE range='{r_range}' {resistance} {r_unit}")
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

    #print(f"v_range_code='{v_range_code:#x}' v_range='{v_range}'")

    print(f"VOLTAGE range='{v_range}', {voltage} V")
    result['OCV'] = dict(range=v_range, unit='V', v=voltage)

    return result

def store_measurement(cell_id, config, log):
    log = log.bind(code=config.measure)
    log.info('measure')

    path, metadata = find_cell(cell_id)
    if not path:
        log.error('cell not found')
        return

    log.debug('cell found', path=path, metadata=metadata)

    if config.measure == 'rc':
        with serial.Serial(config.rc3563_port, 115200) as ser:
            mq = []
            result = None
            while True:
                pkt = ser.read(10)
                mq.append(parse_rc3546_packet(pkt))
                if len(mq) >= 3:
                    # Check if all measurements are identical
                    if mq[0]['OCV'] == mq[1]['OCV'] == mq[2]['OCV'] and mq[0]['IR'] == mq[1]['IR'] == mq[2]['IR']:
                        result = mq[0]
                        break;

                    # Maintain a rolling queue of last 3 measurements
                    mq.pop(0)
            if result:
                m = {
                    'action': 'measurement',
                    'equipment': dict(model='RC3563'),
                    'results': result
                }
    elif config.measure == 'capa':
        capa = input('Capacity [mAh] > ')
        ir = input('IR [mOhm] > ')
        m = {
            'action': 'measurement',
            'equipment': dict(brand='Liitokala', model='Engineer LI-500'),
            'setup': dict(mode='NOR TEST', current='500 mA'),
            'results': {
                'capacity': dict(u='mAh', v=capa),
                'IR': dict(u='mOhm', v=ir)
            }
        }
    else:
        log.error('bad measurement', code=config.measure)
        return

    if config.timestamp:
        m['ts'] = time.time()

    log.debug('measurement data', data=m)

    log_filename = path.parent.joinpath('log.json')
    log.debug('saving to logfile', logfile=log_filename)

    if not log_filename.exists():
        with open(log_filename, 'w') as f:
            f.write("[]")

    with open(log_filename, "r") as f:
        j = json.loads(f.read())

    j.append(m)

    with open(log_filename, "w") as f:
        f.write(json.dumps(j, indent=2))

def main(config, log):
    
    for id in config.identifiers:

        if id == '-':
            for line in sys.stdin:
                line = line.rstrip()
                log = log.bind(id=line)
                store_measurement(cell_id=line, config=config, log=log)
        else:
            log = log.bind(id=id)
            store_measurement(cell_id=id, config=config, log=log)

        if config.pause:
            input('Press Enter to continue')

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Log an action')
    parser.add_argument('-m', '--measure', required=True, choices=['rc', 'capa'], help='Measurement mode')
    parser.add_argument('-T', '--timestamp', const=time.time(), nargs='?', help='Timestamp the log entry')
    parser.add_argument('--pause', default=False, action='store_true', help='Pause for a keypress between measurements')
    parser.add_argument('--rc3563-port', default=os.getenv('RC3563_PORT', '/dev/ttyUSB0'), help="Serial port connected to the RC3563 meter")
    parser.add_argument('identifiers', nargs='*', help='Cell identifiers, use - to read from stdin')

    args = parser.parse_args()
    log.debug('config', args=args)

    main(config=args, log=log)

