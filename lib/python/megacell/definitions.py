#!/usr/bin/env python3

from enum import Enum


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

    # Unknown yet
    OVERDISCHARGE_HALT = 'Overdischarge halt'


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

    EMERGENCY_STOP = '!!!Emergency stop!!!'


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
