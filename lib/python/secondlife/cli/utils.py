#!/usr/bin/env python3

import parsedatetime
import time
import sys
from structlog import get_logger

log = get_logger()

def cell_identifiers(config):
    for id in config.identifiers:

        if id == '-':
            for line in sys.stdin:
                line = line.strip()
                if len(line) == 0:
                    continue

                yield line
        else:
            yield id

def measurement_ts(config):
    # Parse the timestamp argument
    cal = parsedatetime.Calendar()
    time_parsed, context = cal.parse(config.timestamp, version=parsedatetime.VERSION_CONTEXT_STYLE)
    log.debug('parsed timestamp', argument=config.timestamp, time_parsed=time_parsed, context=context)

    if not context.hasDate and context != parsedatetime.pdtContext(accuracy=parsedatetime.pdtContext.ACU_NOW):
        log.fatal('no date in timestamp', parsed=time_parsed, pdt_context=context)
        sys.exit(1)

    return time.mktime(time_parsed)