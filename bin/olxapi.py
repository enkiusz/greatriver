#!/usr/bin/env python3

#
# Copyright 2018 Maciej Grela <enki@fsck.pl>
# SPDX-License-Identifier: WTFPL
#
# Some experiments in interaction with the OLX mobile app API endpoints.
#

import requests
from urllib.parse import urljoin

import logging
import json
import os

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

try:
    from http.client import HTTPConnection # py3
except ImportError:
    from httplib import HTTPConnection # py2

HTTPConnection.debuglevel = 1

class OlxMobileApiSession(requests.Session):
    def __init__(self, *args, **kwargs):
        super(OlxMobileApiSession, self).__init__(*args, *kwargs)
        self.base_url = "https://www.olx.pl/"
        self.bearer_token = os.getenv('OLX_OAUTH_TOKEN')
        self.headers.update({ "Authorization": "Bearer {}".format(self.bearer_token)})
        self.headers.update({ "User-Agent": "Android App"})

    def request(self, method, url, **kwargs):
        return super(OlxMobileApiSession, self).request(method, urljoin(self.base_url, url) , **kwargs)

def main():
    s = OlxMobileApiSession()

    r = s.get("/i2/account/menu/", params= {"json": 1, "version": "2.3.9"})
    print(r.json())

    print("------------------------------------------------")

    r = s.get("/i2/myaccount/active", params= {"json": 1, "page": 1, "version": "2.3.9"})
    print(json.dumps(r.json(), indent=4, sort_keys=True))

if __name__ == "__main__":
    main()

