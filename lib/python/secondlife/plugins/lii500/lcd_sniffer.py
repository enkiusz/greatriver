#!/usr/bin/env python3

# Allow module load from lib/python in main repo
import sys
from pathlib import Path
currentdir = Path(__file__).resolve(strict=True).parent
libdir = currentdir.parent.joinpath('lib/python')
sys.path.append(str(libdir))

import argparse
import logging
import structlog
import serial
import os
import json
from binascii import unhexlify
import struct
from itertools import dropwhile

log = structlog.get_logger()

def fb_bit(fb, i):
    return True if fb[i] == '1' else False

def seg7(fb, **kw):
    code = ''.join([ fb[ kw[seg] ] for seg in ('a','b','c','d','e','f','g')])

    seg7_numeric_codes = {
        '0000000': None, # No digit displayed
        '1111110': '0',
        '0110000': '1',
        '1101101': '2',
        '1111001': '3',
        '0110011': '4',
        '1011011': '5',
        '1011111': '6',
        '1110000': '7',
        '1111111': '8',
        '1111011': '9'
    }

    seg7_misc_codes = {
        '0000001': '-'
    }

    seg7_letters = {
        '0010101': 'n',
        '0011100': 'u',
        '0110110': 'll'
    }

    seg7_codes = {**seg7_numeric_codes, **seg7_misc_codes, **seg7_letters}
    
    if code not in seg7_codes:
        raise RuntimeError(f'Unrecognized 7-segment code {code}')
    
    return seg7_codes[code]

def seg7_join(items):
    # Remove leading empty items
    items = list(dropwhile(lambda d: d is None or len(d) == 0, iter(items)))

    if len(items) == 0:
        return None

    if len(list(filter(lambda d: d is None or len(d) == 0, items))) > 0:
        log.warn('unexpected holes', items=items)
        raise RuntimeError('cannot decode 7-seg value')

    return ''.join(items)

def sel_single_option(options):

    sel = [ option for (option, flag) in options.items() if flag is True ]
    if len(sel) > 1:
        log.error('unexpected multiple options', options=options)
        raise RuntimeError('unexpected multiple options')
    
    return next(iter(sel), None)


def parse_xsl_lii500A_B2_lcdframe(frame):
    log.debug('frame input', frame=frame)
    binary_string = ''.join(['{:08b}'.format(c) for c in frame])
    log.debug('binary string', s=binary_string)

    # Slice out the offset
    offset = binary_string[4:9]
    
    if offset != '00000':
        log.error('non-zero offset not supported', frame=frame)
        return None

    framebuffer = binary_string[9:]
    log.debug('fb', framebuffer=framebuffer, len=len(framebuffer))

    s = dict()

    # Decode the capacity first as it's used to mark the 'NULL' condition
    # on the display
    capacity = seg7_join([
        seg7(framebuffer, a=24,b=28,c=30,d=27,e=26,f=25,g=29),  # Digit 1
        seg7(framebuffer, a=32,b=36,c=38,d=35,e=34,f=33,g=37),  # Digit 2
        seg7(framebuffer, a=40,b=44,c=46,d=43,e=42,f=41,g=45),  # Digit 3
        seg7(framebuffer, a=48,b=52,c=54,d=51,e=50,f=49,g=53),  # Digit 4
    ])
    
    if capacity == 'null':
        # This is a special case, the display is empty
        s['null'] = True
        log.debug('display state', state=s)
        return s
        
    else:

        if capacity == '----':
            # This is the state where the cell has just been connected and charging / discharging has not yet
            # started

            s['capacity'] = None

        else:

            if capacity is not None and not (fb_bit(framebuffer, 55) and fb_bit(framebuffer, 47)):
                log.error('unexpected capacity unit', mA=fb_bit(framebuffer, 55), h=fb_bit(framebuffer, 47))
                raise RuntimeError('unexpected capacity unit')

            c_unit = ''.join([
                'mA' if fb_bit(framebuffer, 55) else '',
                'h' if fb_bit(framebuffer, 47) else ''
            ])

            s['capacity'] = f'{int(capacity)} {c_unit}'

    s['cell_select'] = sel_single_option({
        '1': fb_bit(framebuffer, 107),
        '2': fb_bit(framebuffer, 31),
        '3': fb_bit(framebuffer, 87),
        '4': fb_bit(framebuffer, 104)
    })

    s['mode'] = sel_single_option({
        'charge': fb_bit(framebuffer, 96),
        'fast test': fb_bit(framebuffer, 97),
        'nor test': fb_bit(framebuffer, 98)
    })

    s['end'] = fb_bit(framebuffer, 99)
    s['usb'] = fb_bit(framebuffer, 39)

    voltage = seg7_join([
        seg7(framebuffer, a=72,b=76,c=78,d=75,e=74,f=73,g=77), # Digit 1
        '.' if fb_bit(framebuffer, 79) else '', # Dot
        seg7(framebuffer, a=80,b=84,c=86,d=83,e=82,f=81,g=85), # Digit 2
        seg7(framebuffer, a=88,b=92,c=94,d=91,e=90,f=89,g=93),  # Digit 3
    ])

    if voltage is not None and fb_bit(framebuffer, 95) is False: # V unit
        log.error('no voltage unit', V=fb_bit(framebuffer, 95))
        raise RuntimeError('no voltage unit')
    
    s['voltage'] = f'{float(voltage)} V'

    s['current_select'] = sel_single_option({
        '300 mA': fb_bit(framebuffer, 100),
        '500 mA': fb_bit(framebuffer, 101),
        '700 mA': fb_bit(framebuffer, 102),
        '1000 mA': fb_bit(framebuffer, 103)
    })
    
    time_hours = seg7_join([
        '1' if fb_bit(framebuffer, 15) is True else '',  # Digit 1
        seg7(framebuffer, a=0,b=4,c=6,d=3,e=2,f=1,g=5)    # Digit 2
    ])

    time_minutes = seg7_join([
        seg7(framebuffer, a=8,b=12,c=14,d=11,e=10,f=9,g=13),   # Digit 3
        seg7(framebuffer, a=16,b=20,c=22,d=19,e=18,f=17,g=21)  # Digit 4
    ])

    s['time'] = dict(hours=int(time_hours), 
        minutes=int(time_minutes),
        tick=fb_bit(framebuffer, 7),
        h=fb_bit(framebuffer, 23))
    
    ir = seg7_join([
        '1' if fb_bit(framebuffer, 63) is True else '',                  # Digit 1
        seg7(framebuffer, a=56,b=60,c=62,d=59,e=58,f=57,g=61),    # Digit 2
        seg7(framebuffer, a=64,b=68,c=70,d=67,e=66,f=65,g=69),    # Digit 3
    ])
    
    if ir == '--':
        # The IR is being measured

        s['ir'] = None
    
    else:

        if ir is not None and fb_bit(framebuffer, 71) is False:
            log.error('no IR unit', mR=fb_bit(framebuffer, 71))
            raise RuntimeError('no IR unit')

        s['ir'] = f'{int(ir)} mΩ'

    log.debug('display state', state=s)

    return s

def byte_count(bits):
    if bits % 8 == 0:
        return int(bits / 8)
    else:
        return int(bits / 8) + 1

def fetch_charger_lcd(port):

    with serial.Serial(port, 115200) as ser:
        log.debug('using serial port', port=ser)

        while True:

            marker1 = ser.read(1)
            
            if marker1 != b'\xF0':
                continue
        
            bit_count = struct.unpack('B', ser.read(1))[0]
            data = ser.read( byte_count(bit_count) )

            marker2 = ser.read(1)
            if marker2 != b'\x0F':
                continue

            log.debug('pkt', bit_count=bit_count, data=data)

            if data[0] & 0xF0 != 0xA0:
                    log.debug('unknown frame', packet=data)
                    continue

            try:

                s = parse_xsl_lii500A_B2_lcdframe(data)
                log.info('lcd state', state=s)

                return s

            except Exception as e:
                log.error('cannot parse lcd frame', frame=data, _exc_info=e)
                continue
