#!/usr/bin/env python3

#
# Copyright 2018 Maciej Grela <enki@fsck.pl>
# SPDX-License-Identifier: WTFPL
#
# Fetch and print a list of mainboards supported by Coreboot. Order by last good build timestamp.
# Filter only mainboards which have SPI BIOS chips as these are the easiest to program.
#

import requests
import logging
import sys
import json
from bs4 import BeautifulSoup

# Configuration
supported_mobos_uri = 'https://coreboot.org/status/board-status.html'

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

log.debug("Downloading list of supported mobos from '{}'".format(supported_mobos_uri))
r = requests.get(supported_mobos_uri)

supported_mobos = [ dict(zip(['vendor', 'model', 'latest_good', 'northbridge', 'southbridge', 'superio', 'cpu', 'socket',
                              'rom_pkg', 'rom_proto', 'rom_socketed', 'flashrom', 'vcs'],
    map(lambda col: col.get_text(strip=True).replace('—', ''), row.find_all('td')) ))
    for row in BeautifulSoup(r.content, "lxml").find('h1', text='Motherboards supported in coreboot').find_next('table').
    find_all(lambda tag: tag.name == 'tr' and len(tag.find_all('td')) == 13) ]

log.debug( "Total {} supported mobos".format(len(supported_mobos)))


# Mobo candidates
def mobo_candidate(mobo):

    # We want BIOS chips that we can program in practice
    if mobo['rom_proto'] != 'SPI':
        return False

    # We want boards that are known to work
    if mobo['latest_good'] == 'Unknown':
        return False

    return True


candidate_mobos = sorted([m for m in supported_mobos if mobo_candidate(m)], key=lambda m: m.get('latest_good', ''), reverse=True)
print(json.dumps(candidate_mobos))
