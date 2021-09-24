#!/usr/bin/env python3

# Python 3.9 is needed to load additional plugins as the code uses
# https://docs.python.org/3/library/pkgutil.html#pkgutil.resolve_name

# Allow module load from lib/python in main repo
import sys
from pathlib import Path
currentdir = Path(__file__).resolve(strict=True).parent
libdir = currentdir.parent.joinpath('lib/python')
sys.path.append(str(libdir))

import argparse
import logging
import structlog
import re
import os
from enum import Enum
from collections import defaultdict

from requests_toolbelt import sessions
from secondlife.infoset import Infoset

# Reference: https://stackoverflow.com/a/49724281
LOG_LEVEL_NAMES = [logging.getLevelName(v) for v in
                   sorted(getattr(logging, '_levelToName', None)
                          or logging._levelNames)
                   if getattr(v, "real", 0)]

log = structlog.get_logger()

class ActionCodes(Enum):
    START_LVC_RECOVERY = 'alr'
    START_CHARGING = 'ach'
    STOP_CHARGING = 'sc'
    START_DISCHARGING = 'adc'
    STOP_DISCHARGING = 'odc'
    START_CAPACITY_TEST = 'act'
    STOP_CAPACITY_TEST = 'omc'
    HALT = ''


_megacell_settings_map = {
    'MaV': dict(path='charge.voltage.max', unit='V'),
    'StV': dict(path='charge.voltage.storage', unit='V'),
    'MiV': dict(path='charge.voltage.min', unit='V'),
    'DiR': dict(path='discharge.current.max', unit='mA'),
    'MaT': dict(path='charge.temp.max', unit='degC'),
    'DiC': dict(path='capacity_test.cycles'),
    # 'FwV' This is an ordinary string
    # 'ChC' This flag is not part of settings
    'LmV': dict(path='lcv.voltage.min', unit='V'),
    'LcV': dict(path='lcv.voltage.end', unit='V'),
    'LmD': dict(path='bad_cell_rejection.lcv.max_voltage_drop', unit='V'),
    'LmR': dict(path='lcv.time.max', unit='minute'),
    'McH': dict(path='charge.time.max', unit='minute'),
    'LcR': dict(path='bad_cell_reject.capacity.min', unit='mAh'),
    'CcO': dict(path='charge.correction_factor', unit='1/1'),
    'DcO': dict(path='discharge.correction_factor', unit='1/1'),
    'MsR': dict(path='bad_cell_reject.esr.max', unit='mOhm'),
    #
    # settings.put('charge.current.max', dict(v=1, u='A')) # This is static and cannot be changed with the API
    #
    # This parameter is unknown, always 0
    # 'MuL'
}


def _megacell_settings_unpack(megacell_settings) -> Infoset:
    """
    Unpack the JSON from MegaCell API endpoint to something more manageable

    Reference: https://pop.fsck.pl/hardware/megacell-charger.html
    """
    settings = Infoset()

    settings.put('.fw_version', megacell_settings['FwV'])

    for (key, spec) in _megacell_settings_map.items():
        if 'unit' in spec:
            value = dict(v=megacell_settings[key], u=spec['unit'])
        else:
            value = megacell_settings[key]

        settings.put(spec['path'], value)

    return settings

def _megacell_settings_pack(settings: Infoset) -> dict:
    """
    Pack a generic charger settings object to a JSON dictionary which can
    be sent to the MegaCell API endpoint

    FIXME: Implement proper unit handling
    """
    data = dict()

    for (key, spec) in _megacell_settings_map.items():
        value = settings.fetch(spec['path'])
        if type(value) == dict:
            value = value['v']
        
        data[key] = value

    return data
    
_megacell_cell_data_map = {
    'voltage': dict(path='voltage', unit='V'),
    'amps': dict(path='current', unit='mA', kv=lambda key, raw_value: dict(v=abs(raw_value), direction='charging' if raw_value > 0 else 'discharging' if raw_value < 0 else None)),
    'capacity': dict(path='discharge.capacity', unit='mAh'),
    'chargeCapacity': dict(path='charge.capacity', unit='mAh'),
    'status': dict(path='status_text'),
    'esr': dict(path='esr.current', unit='mOhm'),
    'action_length': dict(path='action.time_elapsed', unit='second'),
    'DiC': dict(path='capacity_test.target_cycles'),
    'complete_cycles': dict(path='capacity_test.completed_cycles'),
    'temperature': dict(path='temperature.current', unit='degC'),
    'ChC': dict(path='busy'),
    'State': dict(path='state')
}

def _megacell_cell_data_unpack(raw_data: dict) -> Infoset:
    cell_info = {}

    for cell in raw_data['cells']:
        # Reflect the marking on the charger cell slots and LCD display
        slot = f"C{cell['CiD'] + 1}"
        cell_info[slot] = Infoset()

        for (key, spec) in _megacell_cell_data_map.items():
            raw_value = cell[key]

            if 'unit' in spec or 'kv' in spec:

                value = dict(v=raw_value)
                if 'unit' in spec:
                    value.update({ 'u': spec['unit']})

                if 'kv' in spec:
                    value.update( spec['kv'](key, raw_value) )

            else:
                value = raw_value

            cell_info[slot].put(spec['path'], value)
        
    return cell_info

class MegaCellAPIV0Session(sessions.BaseUrlSession):

    def __init__(self, base_url, **kwargs):
        log.debug('creating session', session_class=__class__, base_url=base_url)
        super().__init__(base_url=base_url, **kwargs)

    def detect_fw_version(self):
        r = self.post('/api/who_am_i')
        r.raise_for_status()
        return r.json()['McC']

    def get_charger_config(self):
        log.debug('getting charger config')

        r = self.post('/api/get_config_info')
        r.raise_for_status()

        self.charger_config = r.json()
        log.debug('charger config', charger_config=self.charger_config)

        return self.charger_config

    def set_charger_config(self, new_config):
        log.debug('setting charger config', config=new_config)

        r = self.post('/api/set_config_info', json=new_config)
        r.raise_for_status()

        log.debug('set config response', response=r.text)
        if r.text != 'Received':
            log.error('error setting charge config', config=new_config, response=r.text)
            return False

        return True

    def get_cell_data(self):
        log.debug('getting cell data')

        r = self.post('/api/get_cells_info', json=dict(settings={'charger_id': 1}))
        r.raise_for_status()

        cell_data = r.json()
        log.debug('cell info', cell_info=cell_data)
        return cell_data

    def multiple_slots_action(self, slots, action: ActionCodes):
        log.debug('sending action to slots', slots=slots, action=action)

        request = dict(cells=[ { "CiD": slot, "CmD": action.value } for slot in slots])
        log.debug('slot state change request', request=request)

        r = self.post('/api/set_cell', json=request)
        r.raise_for_status()

        log.debug('set state response', response=r.text)
        if r.text != 'Received':
            log.error('error sending action to slots', slots=slots, action=action, response=r.text)
            return False

        return True

    def start_lvc_recovery(self, slots):
        log.debug('')

def megacell_api_session(base_url):
    s = sessions.BaseUrlSession(base_url=base_url)
    log.info('detecting firmware version', base_url=base_url)

    r = s.post('/api/who_am_i')
    r.raise_for_status()
    fw_version = r.json()['McC']
    log.info('charger online', base_url=base_url, fw_version=fw_version)

    fw_versions = [
        (re.compile(r'^Firmware V4\.3\.0\.11$'), MegaCellAPIV0Session)
    ]
        
    for (fw_regex, session_class) in fw_versions:
        if re.match(fw_regex, fw_version):
            return session_class(base_url=base_url)

    return None

def main(config):
    sess = megacell_api_session(config.baseurl)
    
    # Get and set charger config
    charger_config = sess.get_charger_config()
    
    infoset = _megacell_settings_unpack(charger_config)
    print(infoset.to_json())
    packed = _megacell_settings_pack(infoset)
    print('PACKED')
    print(packed)
    #sess.set_charger_config(config)

    raw = sess.get_cell_data()

    cell_data = sess.get_cell_data()
    print("RAW")
    print(cell_data)
    cell_info = _megacell_cell_data_unpack(cell_data)
    print("PROCESSED")
    print('\n'.join( [ci.to_json() for ci in cell_info.values()] ))

    if config.new_cells:
        new_cell_slots = [ slot for slot in cell_info.keys() if cell_info[slot].fetch('status_text') == "New cell inserted" ]
        log.info('cells with new slots', new_cell_slots=new_cell_slots)

        slot_numbers = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]

        sess.multiple_slots_action(slot_numbers, ActionCodes[config.action])


def _config_group(parser):
    group = parser.add_argument_group('megacell charger')
    group.add_argument('--mcc-baseurl', default=os.getenv('MCC_BASEURL', None), help='URL used for the API endpoint of the Megacell Charger')
    group.add_argument('--mcc-select', default=None, metavar='ID', help='Select the specified charger from the urls file')
    group.add_argument('--mcc-urls-file', default=os.getenv('MCC_URLS_FILE', None), help='The file specifying API endpoint URLs for particular chargers')


if __name__ == '__main__':
    # Restrict log message to be above selected level
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr)
    )

    parser = argparse.ArgumentParser(description='Megacell charger')
    parser.add_argument('--loglevel', choices=LOG_LEVEL_NAMES, default='INFO', help='Change log level')
    parser.add_argument('--baseurl', help='Megacell charger endpoint URL')
    parser.add_argument('--action', choices=[ac.name for ac in ActionCodes], help="Select the action to be performed by the charger")

    parser.add_argument('--lii500-select', default=None, metavar='ID', help='Select the specified charger from the ports file')
    parser.add_argument('--lii500-ports-file', default=os.getenv('LII500_PORTS_FILE', None), help='The file specifying serial ports for particular chargers')
   
    parser.add_argument('-n', '--new-cells', dest='new_cells', default=False, action='store_true', help='Perform action on all new cells')
    parser.add_argument('slot', nargs='*', action='append', help='Perform action on specified slots')

    _config_group(parser)

    args = parser.parse_args()

    # Restrict log message to be above selected level
    structlog.configure( wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, args.loglevel)) )

    log.debug('config', args=args)

    main(config=args)

