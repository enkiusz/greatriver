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
import os
import json

from collections import defaultdict
import time
from queue import Queue
from threading import Thread
import threading

from structlog.threadlocal import bind_threadlocal, clear_threadlocal
from structlog.contextvars import bind_contextvars, clear_contextvars
import asciitable


from secondlife.infoset import Infoset
from secondlife.plugins.api import v1, load_plugins
from secondlife.cli.utils import selected_cells, add_plugin_args, add_cell_selection_args, add_backend_selection_args
from secondlife.cli.utils import perform_measurement

from megacell.definitions import ActionCodes, Slots, StatusStrings
from megacell.api import megacell_api_session
from megacell.workflow import DefaultWorkflow
from megacell.utils import WorkflowLog

from secondlife.cli.utils import CompileJQAndAppend

# Reference: https://stackoverflow.com/a/49724281
LOG_LEVEL_NAMES = [logging.getLevelName(v) for v in
                   sorted(getattr(logging, '_levelToName', None) or logging._levelNames) if getattr(v, "real", 0)]

log = structlog.get_logger()


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

    inserted_cells = { slot: None for slot in config.slots }
    cell_data_queues = { slot: Queue() for slot in config.slots }
    worker_threads = { slot: None for slot in config.slots }

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

        for slot in worker_threads.keys():
            if worker_threads[slot] is None:
                # Skip threads which have not been created yet
                continue

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
