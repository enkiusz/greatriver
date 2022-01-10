#!/usr/bin/env python3

import sys
import structlog
import argparse
import json
import getpass
from bankster.credstore.keepass import KeepassCredstore, AskUserCredstore
from tabulate import tabulate
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

log = structlog.get_logger()

class CurrencyConverter(object):
    def __init__(self):
        self.currencypairs = {}
        self.base_currency = None
        self.ecb_download()

    def ecb_download(self):
        self.base_currency = 'EUR'

        url = 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'
        log.debug('downloading gesmes data', url=url)
        r = requests.get(url)
        r.raise_for_status()

        root = ET.fromstring(r.text)
        log.debug('gesmes data', root=root)

        daily_cube = root.find('./{http://www.ecb.int/vocabulary/2002-08-01/eurofxref}Cube').find('./{http://www.ecb.int/vocabulary/2002-08-01/eurofxref}Cube')
        for currency_cube in daily_cube.findall('{http://www.ecb.int/vocabulary/2002-08-01/eurofxref}Cube'):
            currency = currency_cube.attrib['currency']
            self.currencypairs[ f'EUR/{currency}'] = float(currency_cube.attrib['rate'])
            self.currencypairs[ f'{currency}/EUR' ] = 1/float(currency_cube.attrib['rate'])

        log.info('loaded currency pairs', count=len(self.currencypairs))

    def convert(self, amount, frm, to):
        # First check straight conversion
        if f'{frm}/{to}' in self.currencypairs:
            return amount * self.currencypairs[f'{frm}/{to}']

        # Try via a base currency
        base_amount = self.convert(amount, frm, self.base_currency)
        return self.convert(base_amount, self.base_currency, to)


currency_converter = CurrencyConverter()

# Manual plugin import
# KISS
from bankster.plugins.pl_generali import PLGenerali
from bankster.plugins.pl_nestbank import PLNestbank
from bankster.plugins.pl_obligacjeskarbowe import PLObligacjeSkarbowe
from bankster.plugins.pl_ideabank import PLIdeabank
from bankster.plugins.pl_bosbank24 import PLBosbank
from bankster.plugins.pl_starfunds import PLStarfunds
from bankster.plugins.pl_mbank import PLMBank

bank_plugins = dict(PLBosbank=PLBosbank, PLGenerali=PLGenerali, PLNestbank=PLNestbank, PLObligacjeSkarbowe=PLObligacjeSkarbowe,
PLStarfunds=PLStarfunds, PLMBank=PLMBank)

structlog.configure(
    processors=[
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt='iso'),
        structlog.dev.ConsoleRenderer()
    ],
)

#
# Parse command line arguments
#

parser = argparse.ArgumentParser(description='Fetch account balances and summarize them in an org-mode table')
parser.add_argument('-l', '--login', dest='login', metavar='LOGIN',
                    help='Use LOGIN as the login name')
parser.add_argument('-P', '--plugin', dest='enabled_plugins', action='append', metavar='NAME', choices=bank_plugins.keys(),
                    help='Fetch data using specific plugins, all are used by default')
parser.add_argument('-K', '--keepass-db', dest='keepass_db_files', action='append', metavar='FILENAME',
                    help='Use KEEPASS_DB Keepass database(s) file as a source(s) for credentials')
parser.add_argument('--single-password', action='store_true', help='Use a single password to unlock all Keepass database(s)')

args = parser.parse_args()
if not args.enabled_plugins:
    # Enable all plugins by default
    args.enabled_plugins = bank_plugins.keys()

log.msg("start", args=vars(args))

credstores = []
if args.keepass_db_files is not None:
    credstores = [KeepassCredstore(filename=f) for f in args.keepass_db_files]
else:
    if args.login is not None:
        credstores = [AskUserCredstore(identity=args.login)]
    else:
        log.msg('no identity and no keepass db provided')
        sys.exit(1)

if len(credstores) > 1 and args.single_password:
    # Try to unlock using a common secret
    unlock_secret = getpass.getpass("Enter password to unlock *ALL* Keepass databases: ")
else:
    unlock_secret = None

# Unlock all keystores and keep only those which unlocked successfuly
credstores = list(filter(lambda c: c.unlock(unlock_secret) is True, credstores))
if len(credstores) == 0:
    log.msg('could not open any credstores')
    sys.exit(1)

rows = []
for c in credstores:
    log = log.bind(credstore=c.name)

    for plugin_name in args.enabled_plugins:
        plugin_class = bank_plugins[plugin_name]
        log = log.bind(plugin=plugin_name)
        g = plugin_class(credstore=c)

        usable_ids = g.usable_identities()

        if len(usable_ids) == 0:
            log.msg('no usable identities found')
            continue

        g.authenticate()
        data = g.get_balances()
        g.logout()
        g.close()

        if data:
            for bag in data['bags']:
                amount = ''
                if bag['value'] is not None:

                    currency = bag['value'].split(' ')[0]
                    amount = float(bag['value'].split(' ')[1])

                    if currency != 'PLN':
                        #
                        # Convert currency to PLN if needed
                        #
                        amount = currency_converter.convert(amount, currency, 'PLN')

                rows.append( [data['name'], bag['description'], amount] )

rows.append(['Total', '', ''])

# Note: The is no table format in the tabulate library that explicitly generates org-mode tables,
# however the 'github' mode is identical.
print(tabulate(rows, headers=['Institution', 'Description', 'Amount'], tablefmt='github',
               numalign='right'))

# Print org-mode expression used to calculate the total
# # Reference: https://orgmode.org/manual/The-spreadsheet.html
print('#+TBLFM: @>$3=vsum(@2..@-1)::')
