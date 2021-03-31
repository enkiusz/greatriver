#!/usr/bin/env python3

import sys
import argparse
from structlog import get_logger
from pathlib import Path
import json
import asciitable
import datetime
import time
from dateutil.relativedelta import relativedelta

log = get_logger()

# We care only about hour level accuracy
attrs = ['years', 'months', 'days', 'hours']
def human_readable(delta):
    try:
        return ' '.join([ '%d %s' % (getattr(delta, attr), getattr(delta, attr) > 1 and attr or attr[:-1])
                for attr in attrs if getattr(delta, attr) ])
    except:
        return ''

def load_metadata(filename):
    with open(filename) as f:

        version_token = f.readline().rstrip()
        if version_token != 'V0':
            raise RuntimeError(f"Version '{version_token}' not supported")
        
        j = json.loads(f.read())
        return j

def find_cell(cell_id):
    p = Path()

    # First check if cell_id is a path itself
    try:
        metadata = load_metadata(Path(cell_id).joinpath('meta.json'))
        if metadata['id'] == cell_id:
            return (path, metadata)
    except:
        pass

    # Now look in subdirectories
    for path in p.glob('**/meta.json'):
        try:
            metadata = load_metadata(path)
            if metadata['id'] == cell_id:
                return (path, metadata)
        except:
            pass
    else:
        return (None, None)

def load_all_cells(path, log):
    cells = []

    # Now look in subdirectories
    for path in path.glob('**/meta.json'):
        try:
            metadata = load_metadata(path)
            if 'id' in metadata:
                log.debug('loaded cell', id=metadata['id'])
                cells.append((path, metadata))
        except Exception as e: 
            log.error('cannot load metadata', path=path, _exc_info=e)

    return cells

def format_results(results):
    r = []
    for (name,value) in results.items():
        r.append(f"{name}={value['v']}{value.get('u', value.get('unit'))}")
    
    return ' '.join(r)

selfdisch_report_rows = []

def print_info(cell_id, config, log):
    log = log.bind(cell_id=cell_id)
    log.info('print info')

    path, metadata = find_cell(cell_id)
    if not path:
        log.warn('cell not found')
        return

    cell_info(path=path, metadata=metadata, config=config, log=log)

def cell_info(path, metadata, config, log):

    cell_id = metadata['id']
    log = log.bind(cell_id=cell_id, path=path)
    log.info('cell info')

    try:
        log_path = path.with_name('log.json')
        measurement_log = json.loads(log_path.read_text(encoding='utf8'))
    except Exception as e:
        log.error('cannot read log', _exc_info=e)
        return
    

    log.debug('measurement log', log=measurement_log)
    
    rows = []
    for m in measurement_log:
        rows.append([
            human_readable(relativedelta(seconds=m.get('ts')-time.time())) if 'ts' in m else '',
            format_results(m.get('results'))
        ])

    print(f"Cell '{cell_id}' measurement log:")
    asciitable.write(rows, names=['Timestamp', 'Results'], Writer=asciitable.FixedWidth)

    # We need to do this that way because the result of enumerate() is not reversible
    for i in reversed(range(len(measurement_log))):
        m = measurement_log[i]
        if 'OCV' not in m['results']:
            continue

        # Find most recent OCV measurement
        most_recent_ocv = m
        log.debug('most recent OCV measurement', measurement=most_recent_ocv)

        ocv = most_recent_ocv['results']['OCV']['v'] # in V
        if i == 0:
            selfdisch_report_rows.append([
            cell_id,
            'Cell not charged',
            ocv,
            ])
            break

        # Look for a previous charge event
        try:
            charge_event = measurement_log[i-1]
            log.debug('charge event', charge_event=charge_event)
            if 'capacity' in charge_event['results']:
                log.debug('found charging event', charge_event=charge_event)  
                selfdisch_report_rows.append([
                    cell_id, 
                    human_readable(relativedelta(seconds=most_recent_ocv.get('ts')-time.time())) if 'ts' in most_recent_ocv else '',
                    ocv,
                    ])
                break

        except IndexError as e:
            selfdisch_report_rows.append([
                cell_id,
                'Cell not charged',
                ocv,
                ])            
            break
    else:
        selfdisch_report_rows.append([
            cell_id,
            'No OCV test',
            'Unknown',
        ])
                

def main(config, log):
    
    if config.all:
        config.identifiers = [] # Ignore identifiers on commandline

        all_cells = load_all_cells(path=Path(), log=log)
        for (path, metadata) in all_cells:
            cell_info(path=path, metadata=metadata, config=config, log=log)

    for id in config.identifiers:

        if id == '-':
            for line in sys.stdin:
                line = line.strip()
                if len(line) == 0:
                    continue

                print_info(cell_id=line, config=config, log=log)
        else:
            print_info(cell_id=id, config=config, log=log)

    if len(selfdisch_report_rows) > 0:
        print("Cell self-discharge report")
        asciitable.write(selfdisch_report_rows, 
            names=['Cell ID', 'OCV test timestamp', 'OCV voltage [mV]'], 
            formats={ 'Cell ID': '%s', 'OCV test timestamp': '%s', 'OCV voltage [mV]': '%s'},
            Writer=asciitable.FixedWidth)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Log an action')
    parser.add_argument('--all', '-a', default=False, action='store_true', help='Load all cells you can find')
    parser.add_argument('identifiers', nargs='*', default=['-'], help='Cell identifiers, read from stdin by default')

    args = parser.parse_args()
    log.debug('config', args=args)

    main(config=args, log=log)

