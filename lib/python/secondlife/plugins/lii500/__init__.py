#!/usr/bin/env python3

import struct
from secondlife.plugins.api import v1
from structlog import get_logger

log = get_logger()

class Lii500Meter(object):

    def __init__(self, **kwargs):
        self.config = kwargs['config']

    def measure(self, config):

        capa = float(input('Capacity [mAh] > '))
        ir = float(input('IR [mOhm] > '))
        
        #
        # Current settings from the manual: https://www.kupifonar.kz/upload/manuals/liitokala/liito-kala-lii-500-en.pdf
        #
        # When  you  choose  the  charging  current (300mah,500mah),  the  system  recognizes  the  discharging current is the 250mah automatically.
        # When you  choose  the  charging  current (700mah,1000mah),  the  system  recognize  the  discharging current is the 500mah automatically.
        #
        setups = {
            '300 mA':  dict(current_setting='300 mA',  charge_current='300 mA',  discharge_current='250 mA'),
            '500 mA':  dict(current_setting='500 mA',  charge_current='500 mA',  discharge_current='250 mA'),
            '700 mA':  dict(current_setting='700 mA',  charge_current='700 mA',  discharge_current='500 mA'),
            '1000 mA': dict(current_setting='1000 mA', charge_current='1000 mA', discharge_current='500 mA'),
        }
        
        result = {
            'action': 'measurement',
            'equipment': dict(brand='Liitokala', model='Engineer LI-500'),
            'setup': dict(mode_setting='NOR TEST'),
            'results': {
                'capacity': dict(u='mAh', v=capa),
                'IR': dict(u='mOhm', v=ir)
            }
        }

        result['setup'].update( setups[config.lii500_current_setting] )
        return result

v1.register_measurement(v1.Measurement('capa', Lii500Meter))