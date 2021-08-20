#!/usr/bin/env python3

from secondlife.plugins.api import v1
from structlog import get_logger

log = get_logger()

def _copy_transform(input_infoset, config):
    log.debug('copy transform', cell_id=input_infoset.fetch('.id'))
    return input_infoset

v1.register_infoset_transform('copy', _copy_transform)
