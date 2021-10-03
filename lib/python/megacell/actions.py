#!/usr/bin/env python3

import structlog
from queue import Queue
from .definitions import Slots, ActionCodes, StatusStrings
from .api import _get_status_and_state, _get_measurement_results

log = structlog.get_logger()


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

        if status_text == StatusStrings.OVERDISCHARGE_HALT:
            log.error('overdischarge halt')
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
