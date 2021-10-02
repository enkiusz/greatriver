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
import json
from enum import Enum
from collections import defaultdict
import time
from queue import Queue
from threading import Thread
import threading
from structlog.threadlocal import bind_threadlocal, clear_threadlocal
from structlog.contextvars import bind_contextvars, clear_contextvars
import asciitable

from requests_toolbelt import sessions

from secondlife.infoset import Infoset
from secondlife.plugins.api import v1, load_plugins
from secondlife.cli.utils import selected_cells, add_plugin_args, add_cell_selection_args, add_backend_selection_args
from secondlife.cli.utils import perform_measurement

from secondlife.cli.utils import CompileJQAndAppend

# Reference: https://stackoverflow.com/a/49724281
LOG_LEVEL_NAMES = [logging.getLevelName(v) for v in
                   sorted(getattr(logging, '_levelToName', None) or logging._levelNames) if getattr(v, "real", 0)]

log = structlog.get_logger()


class ActionCodes(str, Enum):
    START_LVC_RECOVERY = 'alr'
    START_CHARGING = 'ach'
    STOP_CHARGING = 'sc'
    START_DISCHARGING = 'adc'
    STOP_DISCHARGING = 'odc'
    START_CAPACITY_TEST = 'act'
    STOP_CAPACITY_TEST = 'omc'


class StatusStrings(str, Enum):
    NOT_INSERTED = 'Not Inserted'
    NEW_CELL_INSERTED = 'New cell inserted'

    LVC_START_CHARGING = 'LVC start charging'
    LVC_CHARGING = 'LVC Charging'
    LVC_CHARGED = 'LVC Charged'
    LVC_CELL_REST = 'Cell rest 5 Min'
    LVC_COMPLETED = 'LVC Completed'

    STARTED_CHARGING = 'Started Charging'
    STOPPED_CHARGING = 'Stopped Charging'
    HOT_CHARGED = 'Hot Charged'

    STARTED_DISCHARGING = 'Started Discharging'
    DISCHARGED = 'Discharged'
    HOT_DISCHARGED = 'Hot Discharged'

    INITIATING_MCAP = 'Initiating mCap'
    MCAP_STARTED_CHARGING = 'mCap Started Charging'
    WAIT_FOR_ESR_TEST = 'Wait For ESR Test'
    MCAP_STARTED_DISCHARGING = 'mCap Started Discharging'
    MCAP_STORE_CHARGING = 'mCap Store Charging'
    STORE_CHARGED = 'Store Charged'

    BAD_CELL = 'Bad Cell'  # StateStrings describes in detail what are the problems with the cell


#
# This is a bit more useless as it doesn't update when actions have started. For example it's possible to have:
# 'status': 'mCap Started Charging',
# and
# 'State': 'HOT charged'
# which makes no sense.
#
class StateStrings(str, Enum):
    # Seen together with 'status': 'New cell inserted' or 'LVC Charging'
    LOW_VOLTAGE_CELL = 'Low voltage cell'

    # Seen together with 'status': 'New cell inserted'
    HEALTHY = 'Healthy'

    # Seen together with 'status': 'Bad Cell' when ESR is higher than maximum during capacity test
    HIGH_ESR_ERROR = 'High ESR Error'

    # Seen together with 'status': 'Bad Cell' when temperature exceeds maximum during capacity test
    HOT_CHARGED = 'HOT charged'
    HOT_DISCHARGED = 'HOT discharged'

    # Seen together with 'status': 'Bad Cell' when capacity is less than minimum during capacity measurement
    LOW_CAPACITY_ERROR = 'Low capacity Error'

    # Seen together with 'status': 'Bad Cell' when voltage drops more than maximum during low voltage recovery
    HIGH_VOLT_DROP_ERROR = 'High volt drop Error'

    # Seen together with 'status': 'Bad Cell' when max LVC time elapses
    LVC_RECOVERY_FAILED = 'LVC recovery failed'


class Slots(int, Enum):
    C1 = 0
    C2 = 1
    C3 = 2
    C4 = 3
    C5 = 4
    C6 = 5
    C7 = 6
    C8 = 7
    C9 = 8
    C10 = 9
    C11 = 10
    C12 = 11
    C13 = 12
    C14 = 13
    C15 = 14
    C16 = 15


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
    'LmR': dict(path='lcv.time.max', unit='minutes'),
    'McH': dict(path='charge.time.max', unit='minutes'),
    'LcR': dict(path='bad_cell_rejection.capacity.min', unit='mAh'),
    'CcO': dict(path='charge.correction_factor', unit='1/1'),
    'DcO': dict(path='discharge.correction_factor', unit='1/1'),
    'MsR': dict(path='bad_cell_rejection.esr.max', unit='mOhm'),
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


_megacell_cell_data_map = {
    'voltage': dict(path='voltage', unit='V'),
    'amps': dict(path='current', unit='mA', value_kv=lambda key,
        raw_value: dict(v=abs(raw_value), direction='charging' if raw_value > 0 else 'discharging' if raw_value < 0 else None)),
    'capacity': dict(path='discharge.capacity', unit='mAh'),
    'chargeCapacity': dict(path='charge.capacity', unit='mAh'),
    'status': dict(path='status_text', value_decode=lambda key, raw_value: StatusStrings(raw_value)),
    'esr': dict(path='esr', unit='Ohm'),
    'action_length': dict(path='action.time_elapsed', unit='second'),
    'DiC': dict(path='capacity_test.target_cycles'),
    'complete_cycles': dict(path='capacity_test.completed_cycles'),
    'temperature': dict(path='temperature', unit='degC'),
    'ChC': dict(path='busy'),
    'State': dict(path='state', value_decode=lambda key, raw_value: StateStrings(raw_value))
}


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


def retry(delay, max_retries, work, exc=None):
    retry_count = 0
    result = None
    while result is None:
        try:
            result = work()
            return result
        except Exception as e:
            if exc is not None:
                exc(e, result)

            retry_count += 1
            if retry_count == max_retries:
                raise(e)
            time.sleep(delay)
            log.warning('retrying', delay=delay, retry_count=retry_count, max_retries=max_retries)


def _http_exc(e, res):
    log.warning('exception', _exc_info=e)
    if res is not None:
        log.debug('exception in http request', method=res.request.method, url=res.request.url)
        log.debug('http response', code=res.status_code, resource_url=res.url, headers=res.headers, content=res.text)


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

    return outcome


def low_voltage_recovery(sess, slot: Slots, queue: Queue):
    log.info('performing low voltage recovery')
    outcome = dict(ok=False)

    cell_info = sess.get_cells_info()[slot]
    outcome.update(_get_status_and_state(cell_info))
    status_text = cell_info.fetch('status_text')

    if status_text == StatusStrings.NOT_INSERTED:
        # If cell is not inserted LVC cannot be started
        log.error('cell not inserted')
        return outcome

    if status_text == StatusStrings.BAD_CELL:
        # The cell is already marked as bad
        log.error('bad cell')
        return outcome

    if status_text == StatusStrings.LVC_COMPLETED:
        log.warn('lvc already completed')
        outcome['ok'] = True
        return outcome

    res = sess.multiple_slots_action([slot], ActionCodes.START_LVC_RECOVERY)
    if not res:
        log.error('cannot start low voltage recovery')
        return outcome

    log.info('low voltage recovery started')

    cell_info = queue.get()[slot]
    outcome.update(_get_status_and_state(cell_info))
    outcome.update(_get_measurement_results(cell_info))
    queue.task_done()
    while cell_info.fetch('status_text') != StatusStrings.LVC_COMPLETED:
        log.debug('waiting for low voltage recovery to finish', cell_info=cell_info.to_json())
        cell_info = queue.get()[slot]
        outcome.update(_get_status_and_state(cell_info))
        outcome.update(_get_measurement_results(cell_info))
        queue.task_done()

        status_text = cell_info.fetch('status_text')

        if status_text == StatusStrings.NOT_INSERTED:
            # Break the loop if cell is removed
            log.error('cell removed')
            return outcome

        if status_text == StatusStrings.BAD_CELL:
            # The cell has been marked as bad by the charger
            log.error('bad cell')

            return outcome

    log.info('low voltage recovery finished', outcome=cell_info.fetch('status_text'))

    outcome['ok'] = True

    return outcome


def measure_capacity(sess, slot: Slots, queue: Queue):
    log.info('performing capacity measurement')
    outcome = dict(ok=False)

    cell_info = sess.get_cells_info()[slot]
    outcome.update(_get_status_and_state(cell_info))

    status_text = cell_info.fetch('status_text')

    if status_text == StatusStrings.NOT_INSERTED:
        # If cell is not inserted capacity measurement cannot be started
        log.error('cell not inserted')
        return outcome

    if status_text == StatusStrings.BAD_CELL:
        # The cell has been already marked as bad by the charger
        outcome.update(_get_measurement_results(cell_info))
        log.error('bad cell')
        return outcome

    if status_text == StatusStrings.STORE_CHARGED:
        # The capacity measurement has been completed already
        log.warn('capacity measurement already finished')
        outcome.update(_get_measurement_results(cell_info))
        outcome['ok'] = True
        return outcome

    res = sess.multiple_slots_action([slot], ActionCodes.START_CAPACITY_TEST)
    if not res:
        log.error('cannot start capacity measurement')
        return outcome

    log.info('capacity measurement started')

    cell_info = queue.get()[slot]
    outcome.update(_get_status_and_state(cell_info))
    queue.task_done()
    while cell_info.fetch('status_text') != StatusStrings.STORE_CHARGED:
        log.debug('waiting for capacity measurement to finish', cell_info=cell_info.to_json())
        cell_info = queue.get()[slot]
        outcome.update(_get_status_and_state(cell_info))
        queue.task_done()

        status_text = cell_info.fetch('status_text')

        if status_text == StatusStrings.NOT_INSERTED:
            # Break the loop if cell is removed while capacity is being measured
            log.error('cell removed')
            return outcome

        if status_text == StatusStrings.HOT_CHARGED or status_text == StatusStrings.HOT_DISCHARGED:
            outcome.update(_get_measurement_results(cell_info))
            log.error('temperature exceeded limit')
            return outcome

        if status_text == StatusStrings.BAD_CELL:
            outcome.update(_get_measurement_results(cell_info))
            log.error('bad cell')
            return outcome

    outcome.update(_get_measurement_results(cell_info))
    outcome['ok'] = True

    log.info('capacity measurement finished', outcome=outcome)
    return outcome


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


class WorkflowLog(object):
    def __init__(self, parent_log, main_event):
        self._parent_log = parent_log
        self._main_event = main_event
        self._main_event['workflow'] = dict(log=[])

    @property
    def parent_log(self):
        return self._parent_log

    @property
    def main_event(self):
        return self._main_event

    def __enter__(self):
        self.parent_log.append(self.main_event)
        return self

    def append(self, e):
        self.main_event['workflow']['log'].append(e)
        # The main event timestamp reflects the last added worklog entry
        self.main_event['ts'] = time.time()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass


class LoadJson(argparse.Action):
    def __call__(self, parser, args, value, option_string=None):
        if value[0] == '@':
            # Load complex value from file and parse it as JSON
            try:
                with open(value[1:]) as f:
                    value = Infoset(data=json.load(f))
                    args.write_settings = value
            except Exception as e:
                log.error('cannot load JSON from file', filename=value[1:], _exc_info=e)
                sys.exit(1)
        else:
            log.fatal('argument must be a filename starting with @')
            sys.exit(1)


class DefaultWorkflow(Thread):
    def __init__(self, **kwargs):
        self._sess = kwargs['api_session']
        self._config = kwargs['config']
        self._slot = kwargs['slot']
        self._queue = kwargs['queue']
        self._cell_infoset = kwargs['cell_infoset']
        self._workflow_log = kwargs['workflow_log']
        super().__init__()

    def run(self):
        clear_threadlocal()
        bind_threadlocal(slot=self._slot, cell_id=self._cell_infoset.fetch('.id'))
        workflow_log = self._workflow_log

        log.info('launching workflow')

        workflow_log.append( dict(action='lvc recovery', event='start', ts=time.time()) )
        lvc_outcome = low_voltage_recovery(self._sess, self._slot, self._queue)
        workflow_log.append( dict(action='lvc recovery', event='end', outcome=lvc_outcome, ts=time.time()) )

        if lvc_outcome['ok']:
            # Take the results from the LVC (if there are any)
            workflow_log.main_event['results'].update( lvc_outcome.get('results', {}) )

            workflow_log.append( dict(action='capacity measure', event='start', ts=time.time()) )
            mcap_outcome = measure_capacity(self._sess, self._slot, self._queue)
            workflow_log.append( dict(action='capacity measure', event='end', outcome=mcap_outcome, ts=time.time()) )

            if mcap_outcome['ok']:

                # Take the results from the capacity measurement (if there are any)
                workflow_log.main_event['results'].update( mcap_outcome.get('results', {}) )

                workflow_log.main_event['setup']['charge_discharge_cycles'] = mcap_outcome['capacity_test']['completed_cycles']

            else:
                log.warning('failed capacity measurement', outcome=mcap_outcome)

                status_text = mcap_outcome['status_text']
                if status_text == StatusStrings.HOT_CHARGED or status_text == StatusStrings.HOT_DISCHARGED:
                    self._cell_infoset.put('.props.tags.excessive_heat', True)

        else:
            log.warning('failed low voltage recovery attempt', outcome=lvc_outcome)

            self._cell_infoset.put('.props.tags.precharge_fail', True)

        log.info('workflow finished')


def _config_group(parser):
    group = parser.add_argument_group('megacell charger')
    group.add_argument('--mcc-baseurl', default=os.getenv('MCC_BASEURL', None),
        help='URL used for the API endpoint of the Megacell Charger')
    group.add_argument('--mcc-select', required=True, default=None, metavar='ID',
        help='Select the specified charger from the urls file')
    group.add_argument('--mcc-urls-file', default=os.getenv('MCC_URLS_FILE', None),
        help='The file specifying API endpoint URLs for particular chargers')


def SlotType(s):
    try:
        return Slots[s]
    except KeyError:
        raise argparse.ArgumentError()


def _slot_group(parser):
    parser.add_argument('--new-cells', default=False, action='store_true', help='Select slots which contain new cells')
    parser.add_argument('--all-slots', default=False, action='store_true', help='Select all slots in the charger')
    parser.add_argument('slots', nargs='*', type=SlotType, choices=[].extend([ slot for slot in Slots ]), help='Specify slots')


def charger(config):

    sess = megacell_api_session(config.mcc_baseurl)

    if config.read_settings:
        charger_settings = sess.get_charger_settings()
        print(charger_settings.to_json())
        return

    if config.write_settings:
        log.info('configuring charger')
        sess.set_charger_settings(config.write_settings)
        return


def slot(config):

    sess = megacell_api_session(config.mcc_baseurl)

    if config.all_slots:
        config.slots = Slots

    if config.new_cells:
        cells_info = sess.get_cells_info()
        config.slots = [ slot for slot in cells_info.keys() if cells_info[slot].fetch('status_text') == StatusStrings.NEW_CELL_INSERTED ]

    log.info('selected slots', slots=config.slots)

    if config.action:
        # Start an action on slots
        sess.multiple_slots_action(config.slots, ActionCodes[config.action])

    if config.info:
        # Print cells info
        cells_info = sess.get_cells_info()

        if len(config.infoset_queries) > 0:
            results = dict()
            for slot in config.slots:
                results[slot] = list()
                json_text = cells_info[slot].to_json()

                for query in config.infoset_queries:

                    query_result = query.input(text=json_text).text()
                    results[slot].append( query_result )
                    log.debug('jq query result', slot=slot, result=query_result, query=query)

            asciitable.write([ [slot] + [ result for result in results[slot] ] for slot in config.slots ],
                names=['Slot'] + [ query.program_string for query in config.infoset_queries ],
                formats={ 'Slot': '%s' },
                Writer=asciitable.FixedWidth)
        else:
            print(json.dumps( { slot.name: cells_info[slot].fetch('.') for slot in config.slots } ))


def workflow(config):
    sess = megacell_api_session(config.mcc_baseurl)
    charger_settings = sess.get_charger_settings()

    # TODO: Allow to select a workflow in the fututre
    workflow_class = DefaultWorkflow

    if config.all_slots:
        config.slots = Slots

    if config.new_cells:
        cells_info = sess.get_cells_info()
        config.slots = [ slot for slot in cells_info.keys() if cells_info[slot].fetch('status_text') == StatusStrings.NEW_CELL_INSERTED ]

    log.info('selected slots', slots=config.slots)

    backend = v1.celldb_backends[config.backend](dsn=config.backend_dsn, config=config)

    inserted_cells = dict()
    cell_data_queues = dict()
    worker_threads = dict()

    for slot in config.slots:
        cell_id = input(f'[{config.mcc_select}/{slot.name}] Input cell ID > ')

        cell_infoset = backend.fetch(cell_id)

        if not cell_infoset:
            if config.autocreate is True:
                cell_infoset = backend.create(id=cell_id, path=getattr(config, 'path', '/'))
                backend.put(cell_infoset)
            else:
                log.error('cell not found', id=cell_id)
                sys.exit(1)

        log.info('cell found', id=cell_id)

        inserted_cells[slot] = cell_infoset
        queue = Queue()
        cell_data_queues[slot] = queue

        # Create a charger API session and workflow log entry for each thread
        sess = megacell_api_session(config.mcc_baseurl)

        with WorkflowLog(parent_log=cell_infoset.fetch('.log'), main_event={
            'type': 'measurement',
            'equipment': {
                'model': 'Megacell Charger',
                'fw': charger_settings.fetch('.fw_version'),
                'selector': config.mcc_select,
                'api_baseurl': config.mcc_baseurl,
                'slot': slot.name,
            },
            'setup': {
                'charger_settings': charger_settings.fetch('.'),  # FIXME: There is something wrong with infoset nesting here

                #
                # Put common capacity test information into the 'setup' key:
                # - some of this information is taken from the charger configuration fetched before the workflow is started
                # - some is static and always the same for Megacell Charger
                #
                # This is static for Megacell Charger and cannot be configured
                'charge_current': dict(v=1000, u='mA'),
                'discharge_current': charger_settings.fetch('.discharge.current.max'),
            },
            'results': {}
        }) as workflow_log:

            worker_threads[slot] = workflow_class(api_session=sess,
                config=config, slot=slot, queue=queue, cell_infoset=cell_infoset,
                workflow_log=workflow_log)

    for slot in config.slots:
        worker_threads[slot].start()

    while threading.active_count() > 1:
        log.info('cell state feeder loop', active_threads=threading.active_count())

        # Get the current cell info
        cells_info = sess.get_cells_info()

        for slot in config.slots:
            if not worker_threads[slot].is_alive():
                # Skip threads which have not yet started or have stopped
                continue

            cell_data_queues[slot].put(cells_info)

        time.sleep(5)

    # Save cell infosets
    for slot in config.slots:
        backend.put(inserted_cells[slot])


if __name__ == '__main__':
    # Restrict log message to be above selected level
    structlog.configure(
        processors=[
            structlog.threadlocal.merge_threadlocal,
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M.%S"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr)
    )

    load_plugins()

    parser = argparse.ArgumentParser(description='Megacell charger')
    parser.add_argument('--loglevel', choices=LOG_LEVEL_NAMES, default='INFO', help='Change log level')
    _config_group(parser)

    # These will be needed only for workflows
    add_plugin_args(parser)
    add_backend_selection_args(parser)

    subparsers = parser.add_subparsers(help='commands')

    slot_parser = subparsers.add_parser('slots', help='Slot commands')
    slot_parser.set_defaults(cmd=slot)
    slot_parser.add_argument('--action', choices=[ac.name for ac in ActionCodes],
        help="Select the action to be performed by the charger")
    slot_parser.add_argument('--info', action='store_true', help='Print current cell data')
    slot_parser.add_argument('--infoset-query', default=[], dest='infoset_queries', action=CompileJQAndAppend,
        help='Apply a JQ query to the infoset and print the result, use https://stedolan.github.io/jq/ syntax.')

    _slot_group(slot_parser)

    charger_parser = subparsers.add_parser('charger', help='Charger commands')
    charger_parser.set_defaults(cmd=charger)
    charger_parser.add_argument('--read-settings', action='store_true', help='Print charger settings')
    charger_parser.add_argument('--write-settings', action=LoadJson, help='Set new charger settings')

    workflow_parser = subparsers.add_parser('workflow', help='Workflow commands')
    workflow_parser.set_defaults(cmd=workflow)

    workflow_parser.add_argument('--workflow', action='store_true', help='Start workflow for cells already in charger')
    _slot_group(workflow_parser)
    workflow_parser.add_argument('--autocreate', default=False, action='store_true',
        help='Create cell IDs that are selected but not found')
    workflow_parser.add_argument('--path', default=os.getenv('CELLDB_PATH'), help='Set cell path')

    # Then add argument configuration argument groups dependent on the loaded plugins, include only:
    # - state var plugins
    # - celldb backend plugins
    included_plugins = v1.state_vars.keys() | v1.celldb_backends.keys()
    for codeword in filter(lambda codeword: codeword in v1.config_groups.keys(), included_plugins):
        v1.config_groups[codeword](parser)

    args = parser.parse_args()

    # Restrict log message to be above selected level
    structlog.configure( wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, args.loglevel)) )

    log.debug('config', args=args)

    # Setup log with charger config
    log = log.bind(mcc_select=args.mcc_select)

    if hasattr(args, 'cmd'):
        args.cmd(config=args)
