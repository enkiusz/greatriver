#!/usr/bin/env python3

import structlog
import re
from requests_toolbelt import sessions

from secondlife.infoset import Infoset
from .definitions import _megacell_settings_map, _megacell_cell_data_map, ActionCodes, Slots
from .utils import retry, _http_exc

log = structlog.get_logger()


def _get_status_and_state(cell_info):
    return dict(status_text=cell_info.fetch('status_text'), state_text=cell_info.fetch('.state'))


def _get_measurement_results(cell_info):
    outcome = dict(results={})

    # At this point not all cell info items can be available
    if cell_info.fetch('.voltage.v') > 0:
        outcome['results'].update({
            'OCV': cell_info.fetch('.voltage'),
        })
    if cell_info.fetch('.discharge.capacity.v') > 0:
        outcome['results'].update({
            'capacity': cell_info.fetch('.discharge.capacity')
        })
    if cell_info.fetch('.esr.v') > 0:
        outcome['results'].update({
            'IR': cell_info.fetch('.esr')
        })
    if cell_info.fetch('.charge.capacity.v') > 0:
        outcome['results'].update({
            'charge_capacity': cell_info.fetch('.charge.capacity')
        })
    if cell_info.fetch('.capacity_test.completed_cycles') > 0:
        outcome['capacity_test'] = {
            'completed_cycles': cell_info.fetch('.capacity_test.completed_cycles')
        }

    return outcome


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
    Pack a Infoset representing the charger settings object to a JSON dictionary which can be sent to the MegaCell API endpoint

    FIXME: Implement proper unit handling
    """
    data = dict()

    for (key, spec) in _megacell_settings_map.items():
        value = settings.fetch(spec['path'])
        if type(value) == dict:
            value = value['v']

        data[key] = value

    return data


def _megacell_cell_data_unpack(raw_data: dict) -> Infoset:
    cell_info = {}

    for cell in raw_data['cells']:
        # Reflect the marking on the charger cell slots and LCD display
        slot = Slots(cell['CiD'])
        cell_info[slot] = Infoset()

        for (key, spec) in _megacell_cell_data_map.items():
            raw_value = cell[key]
            # Value is equal to raw value from JSON by default
            value = raw_value

            if 'value_decode' in spec:
                # Store the original value before decoding
                cell_info[slot].put(f"_raw_{spec['path']}", raw_value)
                value = spec['value_decode'](key, raw_value)

            if 'unit' in spec:
                # The value has a unit
                value = dict(v=raw_value)
                if 'unit' in spec:
                    value.update({ 'u': spec['unit']})

            if 'value_kv' in spec:
                value['_raw_v'] = value['v']  # Store raw_value
                # The value has additional KVps
                value.update( spec['value_kv'](key, raw_value) )

            cell_info[slot].put(spec['path'], value)

    return cell_info


class MegaCellAPIV0Session(sessions.BaseUrlSession):

    def __init__(self, base_url, **kwargs):
        log.debug('creating session', session_class=__class__, base_url=base_url)
        super().__init__(base_url=base_url, **kwargs)
        self._max_retries = 20
        self._retry_delay = 10
        self._charger_id = 1  # This seems to be static for now

    def detect_fw_version(self):
        r = self.post('/api/who_am_i')
        r.raise_for_status()
        return r.json()['McC']

    def json_request(url, *args, **kwargs):
        raise NotImplemented()

    def request(self, method, url, *args, **kwargs):

        def __work():
            res = super(MegaCellAPIV0Session, self).request(method, url, *args, **kwargs)
            if res.headers['Content-Type'] == 'text/json':
                # Try to parse json, will raise and catch an exception if not possible
                res.json()
            return res

        return retry(delay=self._retry_delay, max_retries=self._max_retries, work=__work, exc=_http_exc)

    def get_charger_settings(self):
        log.debug('getting charger settings')

        def __work():
            r = self.post('/api/get_config_info')
            r.raise_for_status()
            return r.json()

        config_data = retry(self._retry_delay, self._max_retries, work=__work, exc=_http_exc)

        log.debug('charger settings data', config_data=config_data)
        return _megacell_settings_unpack(config_data)

    def set_charger_settings(self, new_config: Infoset):
        log.debug('setting charger settings', config=new_config.to_json())

        r = self.post('/api/set_config_info', json=_megacell_settings_pack(new_config))
        r.raise_for_status()

        log.debug('set config response', response=r.text)
        if r.text != 'Received':
            log.error('error setting charge settings', config=new_config, response=r.text)
            return False

        return True

    def get_cells_info(self) -> Infoset:
        log.debug('getting cells info')

        def __work():
            r = self.post('/api/get_cells_info', json=dict(settings={'charger_id': self._charger_id}))
            r.raise_for_status()
            return r.json()

        cells_data = retry(self._retry_delay, self._max_retries, work=__work)

        log.debug('cells data from charger', cells_info=cells_data)
        return _megacell_cell_data_unpack(cells_data)

    def multiple_slots_action(self, slots, action: ActionCodes):
        log.debug('sending action to slots', slots=slots, action=action)

        request = dict(cells=[ { "CiD": slot.value, "CmD": action.value } for slot in slots])
        log.debug('slot state change request', request=request)

        r = self.post('/api/set_cell', json=request)
        r.raise_for_status()

        log.debug('set state response', response=r.text)
        if r.text != 'Received':
            log.error('error sending action to slots', slots=slots, action=action, response=r.text)
            return False

        return True


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
