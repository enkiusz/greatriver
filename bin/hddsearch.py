#!/usr/bin/env python3

from suds.client import Client
import logging
import os
import getpass
import sys
import argparse
import pickle
from xdg.BaseDirectory import xdg_cache_home, xdg_config_home
from prettytable import PrettyTable
from configparser import ConfigParser

config = ConfigParser()

argparser = argparse.ArgumentParser(description="Search for Allegro hard disks with best Passmark scores")
argparser.add_argument('--config', metavar='FILE', default=os.path.join(xdg_config_home, 'allegro-prodsearch', 'config.ini'), help='Configuration file location')
argparser.add_argument('--category', '-c', metavar='ID', action='append', default=[4476], type=int, help='The category identifier')
argparser.add_argument('--maxresults', metavar='NUM', type=int, default=100, help='Limit the number of search results for each query (speeds up search)')
argparser.add_argument("--min_size", metavar="GB", type=int, help="The minimum HDD size in GB")
argparser.add_argument("--max_size", metavar="GB", type=int, help="The maximum HDD size in GB")
argparser.add_argument("--rotation_rates", metavar="RPMs", help="Acceptable rotation rate(s) of the HDD, separated by commas")
argparser.add_argument("--form_factors", metavar="INCHES", help="Acceptable form factors (2.5, 3.5, ...), separated by commas")
argparser.add_argument("--interfaces", metavar="IFACE", help="Acceptable interface types (SATA, PATA, ...), separated by commas")

args = argparser.parse_args()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

log.debug("Trying to load configuration file from '%s'" % (args.config))
config.read(args.config)

log.debug("Loaded configuration dump:")
log.debug(config)

log.debug("Commandline arguments:")
log.debug(args)

# Check if we can load from cache
cache_filename = os.path.join(config['DEFAULT']['cache_location'], 'passmark-hdds.pickle')


hdds = None

try:
    with open(cache_filename, "rb") as f:
        hdds = pickle.load(f)

except FileNotFoundError:
    from bs4 import BeautifulSoup
    import requests

    passmark_url = config['DEFAULT']['passmark_url']
    print("Downloading list of hard disks from PassMark URL '{}' into '{}'".format(passmark_url, config['DEFAULT']['cache_location']))

    bs = BeautifulSoup(requests.get(passmark_url).content, "lxml")

    hdd_table = bs.find(id="cputable")

    hdds = dict()

    for row in hdd_table.find('tbody').find_all('tr'):
        cols = row.find_all('td')
        drive_name = cols[0].get_text(strip=True)
        rating = cols[1].get_text(strip=True)
        rank = cols[2].get_text(strip=True)
        value = cols[3].get_text(strip=True)
        price = cols[4].get_text(strip=True)

        # print("%s rating='%s' rank='%s' value='%s' price='%s USD': %s" % (drive_name,rating,rank,value,price, row))

        hdds[drive_name] = dict(name=drive_name, rating=rating, rank=rank, value=value, price=price)


    with open(cache_filename, "wb") as f:
        pickle.dump(hdds, f)

finally:
    print("Loaded information about '%s' hard disks from Passmark" % (len(hdds.keys())))

client = Client(config['DEFAULT']['wsdl'])
webapi_key = os.getenv('ALLEGRO_WEBAPI_KEY')
country = config['DEFAULT']['country_id']

cat_filter = client.factory.create("FilterOptionsType")
cat_filter.filterId = 'category'
cat_filter.filterValueId = client.factory.create('ArrayOfString')
cat_filter.filterValueId.item = [ args.category ]

filteroptions = client.factory.create('ArrayOfFilteroptionstype')
filteroptions.item = [ cat_filter ]


if args.min_size is not None or args.max_size is not None:
    log.debug("Creating filter for HDD size constraint <{}, {}> GB".format(args.min_size, args.max_size))

    size_filter = client.factory.create("FilterOptionsType")
    size_filter.filterId = 82
    size_filter.filterValueRange = client.factory.create("RangeValueType")

    if args.min_size is not None:
        size_filter.filterValueRange.rangeValueMin = args.min_size
    if args.max_size is not None:
        size_filter.filterValueRange.rangeValueMax = args.max_size

    filteroptions.item.append(size_filter)

if args.rotation_rates is not None:
    log.debug("Creating filter for HDD rotation rates '{}' RPM".format(args.rotation_rates))

    rpm_filter = client.factory.create("FilterOptionsType")
    rpm_filter.filterId = 18268
    rpm_filter.filterValueId = client.factory.create("ArrayOfString")

    # TODO: This needs to be detected from available reported filterValues
    rpm_rate_valueIds = {
        4200: 266258,
        5400: 2,
        5900: 16,
        7200: 1,
        10000: 4,
        15000: 8
    }

    rpm_filter.filterValueId.item = [ rpm_rate_valueIds[int(rpm)] for rpm in args.rotation_rates.split(",") ]

    filteroptions.item.append(rpm_filter)

if args.form_factors is not None:
    log.debug("Creating filter for form factors '{}' RPM".format(args.form_factors))

    ff_filter = client.factory.create("FilterOptionsType")
    ff_filter.filterId = 207378
    ff_filter.filterValueId = client.factory.create("ArrayOfString")

    # TODO: This needs to be detected from available reported filterValues
    ff_valueIds = {
        "1.8": 231694,
        "2.5": 231698,
        "3.5": 231702
    }

    ff_filter.filterValueId.item = [ ff_valueIds[ff] for ff in args.form_factors.split(",") ]

    filteroptions.item.append(ff_filter)

if args.interfaces is not None:
    log.debug("Creating filter for HDD interfaces '{}' RPM".format(args.interfaces))

    iface_filter = client.factory.create("FilterOptionsType")
    iface_filter.filterId = 474
    iface_filter.filterValueId = client.factory.create("ArrayOfString")

    # TODO: This needs to be detected from available reported filterValues
    iface_valueIds = {
        "SATA": 1,
        "SATA-II": 2,
        "SATA-III": 5,
        "mSATA": 231638,
        "µSATA": 277481,
        "PATA": 231642,
        "SAS": 231646
    }

    iface_filter.filterValueId.item = [ iface_valueIds[iface] for iface in args.interfaces.split(",") ]

    filteroptions.item.append(iface_filter)

log.debug("Constraints:")
log.debug(filteroptions)

res = client.service.doGetItemsList(webapiKey=webapi_key, countryId=country, filterOptions=filteroptions)

common_keywords = [
    # Interfaces
    'SATA2',
    'SATA3',
    # Common keywords used in describing disks
    'SSHD', 'ENTERPRISE', "GREEN", 'twardy', "3.5''", "3,5''",
    # Cache
    'CACHE',
    # Rotation rates
    '7200RPM', '5400RPM', '7200OBR.',
    # Vendors
    'SEAGATE', 'SEGATE', 'HITACHI', 'HGST', "TOSHIBA", 'SAMSUNG', "CAVIAR",
    # Volumes
    '1024G', '2000GB', '3000GB', '1000GB',
    # Allegro-specific terms
    'FV-23%',
    # Warranty information keywords
    'GW.36', 'GW.24',
    # Misc
    'SZYBKI', "SUPER", "Windows"
]

p = PrettyTable(["ID", "Auction title", "Bidders", "Price", "Passmark candidate(s)", "Avg. Passmark"])
p.align["Auction title"] = p.align["ID"] = "l"

for item in res.itemsList.item:
    # Find the price
    price=None
    for price_item in item.priceInfo.item:
        if price_item.priceType == 'buyNow':
            price=price_item.priceValue

    # Skip auctions
    if price is None:
        continue


    # Remove common keywords
    # Remove short keywords (< 5 characters)
    keywords = list( filter(lambda keyword: keyword.upper() not in common_keywords and len(keyword) > 4, item.itemTitle.split()) )

    log.debug("Item:")
    log.debug(item)
    log.debug("Searching for keywords '{}'".format(keywords))

    found_hdds = []
    passmark_sum = passmark_avg = 0
    for name in hdds.keys():

        score = 0
        for keyword in keywords:
            if name.lower().find(keyword.lower()) >= 0:
                score+=1

        if score > 0:
            found_hdds.append("%s(%s)" % (name,hdds[name]['rating']))
            passmark_sum += int(hdds[name]['rating'])

    if len(found_hdds) > 0:
        passmark_avg = passmark_sum / len(found_hdds)

    log.debug("Found HDDS: '{}' (avg {})".format(found_hdds, passmark_avg))
    log.debug("8<-----------------------------------------------------------")

    p.add_row([item.itemId, item.itemTitle, item.biddersCount, price, "\n".join(found_hdds), passmark_avg])

print(p.get_string(sortby="Avg. Passmark"))


