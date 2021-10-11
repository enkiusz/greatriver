#!/usr/bin/env python3

from secondlife.plugins.api import v1
from structlog import get_logger
from dateutil.relativedelta import relativedelta
import asciitable
import json
import time

# We care only about hour level accuracy
_attrs = ['years', 'months', 'days', 'hours']


def _since_now(ts):
    if ts is None:
        return 'NO TIMESTAMP'
    if time.time() - ts < 3600:
        return '< 1 hour ago'
    try:
        delta = relativedelta(seconds=ts - time.time())
        return ' '.join([ '%d %ss' % (getattr(delta, attr), getattr(delta, attr) > 1 and attr or attr[:-1])
                for attr in _attrs if getattr(delta, attr) ])
    except Exception as e:
        return ''


def _format_results(results):
    r = []
    for (name, value) in results.items():
        try:
            r.append(f"{name}={round(value['v'],3)}{value.get('u')}")
        except Exception:
            # No 'v' or 'u' key, print as plain value
            r.append(f"{name}={value!r}")
    if len(r) == 0:
        return 'NO RESULTS'
    else:
        return ' '.join(r)


def _print_keys(data: dict, keys: list):
    r = []
    for key in keys:
        if key not in data:
            continue

        r.append(f"{key}={data[key]}")
    return ' '.join(r)


class LogReport(object):

    def __init__(self, **kwargs):
        self.config = kwargs['config']
        self.log = get_logger(name=__class__.__name__)
        self.cells = dict()

    def process_cell(self, infoset):
        log = self.log.bind(id=infoset.fetch('.id'))
        log.debug('processing cell')

        measurement_log = infoset.fetch('.log')

        log.debug('measurement log', log=measurement_log)

        self.cells[infoset.fetch('.id')] = [
            [
                _since_now(m.get('ts')),
                m.get('type', 'NO TYPE CODE'),
                m.get('event', 'NO EVENT CODE'),
                _print_keys(m.get('equipment', {}), ('model', 'selector')),
                _format_results(m['results']) if 'results' in m else str(m),
            ] for m in measurement_log
        ]

    def report(self):

        if len(self.cells.items()) > 0:
            for (id, rows) in self.cells.items():
                print(f"=== Log for {id}")
                if len(rows) > 0:
                    asciitable.write(rows, names=['Timestamp', 'Type', 'Event', 'Equipment', 'Results'],
                        formats={'Timestamp': '%s', 'Type': '%s', 'Event': '%s', 'Equipment': '%s', 'Results': '%s'}, Writer=asciitable.FixedWidth)
                else:
                    print("LOG EMPTY")
        else:
            self.log.warning('no data')


v1.register_report(v1.Report('log', LogReport))
