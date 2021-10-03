#!/usr/bin/env python3

import structlog
import threading
import time
from structlog.threadlocal import bind_threadlocal, clear_threadlocal

from .definitions import StatusStrings
from .actions import low_voltage_recovery, measure_capacity
from .api import _get_status_and_state, _get_measurement_results

log = structlog.get_logger()


class DefaultWorkflow(threading.Thread):
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

            else:
                log.warning('failed capacity measurement', outcome=mcap_outcome)

                status_text = mcap_outcome['status_text']
                if status_text == StatusStrings.HOT_CHARGED or status_text == StatusStrings.HOT_DISCHARGED:
                    self._cell_infoset.put('.props.tags.excessive_heat', True)

        else:
            log.warning('failed low voltage recovery attempt', outcome=lvc_outcome)

            self._cell_infoset.put('.props.tags.precharge_fail', True)

        log.info('workflow finished')
