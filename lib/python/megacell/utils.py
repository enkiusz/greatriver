#!/usr/bin/env python3

import structlog
import time

log = structlog.get_logger()


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
                raise e
            time.sleep(delay)
            log.warning('retrying', delay=delay, retry_count=retry_count, max_retries=max_retries)


def _http_exc(e, res):
    log.warning('exception', _exc_info=e)
    if res is not None:
        log.debug('exception in http request', method=res.request.method, url=res.request.url)
        log.debug('http response', code=res.status_code, resource_url=res.url, headers=res.headers, content=res.text)
