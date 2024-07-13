#!/usr/bin/env python3

from secondlife.plugins.api import v1
from structlog import get_logger
import tabulate
import json
from collections import defaultdict
import structlog
import sys
import jq
import argparse

from secondlife.cli.utils import CompileJQ

log = structlog.get_logger()

import matplotlib.pyplot as plt
import numpy as np


class PlotReport(object):

    def __init__(self, **kwargs):
        self.config = kwargs['config']
        self.log = get_logger(name=__class__.__name__)
        self.x = []
        self.y = []

    def process_cell(self, infoset):
        cell_id = infoset.fetch('.id')
        log = self.log.bind(id=cell_id)
        log.debug('processing cell')

        json_text = infoset.to_json(indent=2)

        if self.config.plot_query_x is None or self.config.plot_query_y is None:
            log.error('both x and y queries need to be defined')
            sys.exit(1)

        result_x = self.config.plot_query_x.input(text=json_text).first()
        result_y = self.config.plot_query_y.input(text=json_text).first()

        if result_x is None or result_y is None:
            log.warn('no result', id=cell_id, x=result_x, y=result_y)
            return

        log.debug('jq query result', id=cell_id, x=result_x, y=result_y,
                  query_x=self.config.plot_query_x,
                  query_y=self.config.plot_query_y)

        self.x.append(float(result_x))
        self.y.append(float(result_y))

    def report(self, format='ascii'):
        if format != 'ascii':
            log.error('unknown report format', format=format)
            return

        if len(self.x) == 0 or len(self.y) == 0:
            self.log.warning('no data')
            return

        if len(self.x) != len(self.y):
            log.error('x and y array length mismatch', num_x=len(self.x), num_y=len(self.y))
            return

        log.info('plotting', num_points=len(self.x))

        fig, ax = plt.subplots()

        ax.scatter(self.x, self.y)

        plt.show()


def _config_group(parser):
    group = parser.add_argument_group('plot report')
    group.add_argument('--plot-query-x', dest='plot_query_x', action=CompileJQ,
        help='The JQ query to use as the X axis, use https://stedolan.github.io/jq/ syntax.')
    group.add_argument('--plot-query-y', dest='plot_query_y', action=CompileJQ,
        help='The JQ query to use as the Y axis, use https://stedolan.github.io/jq/ syntax.')


v1.register_report(v1.Report('plot', PlotReport))
v1.register_config_group('plot', _config_group)
