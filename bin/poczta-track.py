#!/usr/bin/env python3

#
# Copyright 2018 Maciej Grela <enki@fsck.pl>
# SPDX-License-Identifier: WTFPL
#
# Fetch information about a parcel using the Polish Post tracking API.
#

import sys
from suds.client import Client
from suds.wsse import *
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

##
## Login and get version number
####
pp_url = 'https://tt.poczta-polska.pl/Sledzenie/services/Sledzenie?wsdl'
log.info("Creating client using WSDL URL '{}'".format(pp_url))

conn = Client(pp_url)

identity = 'sledzeniepp'
secret = 'PPSA'

security = Security()
token = UsernameToken(identity, secret)
security.tokens.append(token)
conn.set_options(wsse=security)

api_version = str(conn.service.wersja())
log.debug("API version: '{}'".format(api_version))

tracking_no = sys.argv[1]
status = conn.service.sprawdzPrzesylkePl(tracking_no)
print("Status of parcel '{}' is {}".format(tracking_no, status))

