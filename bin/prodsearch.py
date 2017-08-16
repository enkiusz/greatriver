#!/usr/bin/env python3

from suds.client import Client
from xdg.BaseDirectory import xdg_cache_home, xdg_config_home

from configparser import ConfigParser
import logging
import os
import getpass
import argparse
import pickle

config = ConfigParser()

argparser = argparse.ArgumentParser(description="Search for and summarize concluded offers on Allegro")
argparser.add_argument('--config', metavar='FILE', default=os.path.join(xdg_config_home, 'allegro-prodsearch', 'config.ini'), help='Configuration file location')
argparser.add_argument('--category', '-c', metavar='ID', action='append', type=int, help='The category identifier')
argparser.add_argument('query', metavar='QUERY', nargs='?', help='The query string to search')

args = argparser.parse_args()

logging.basicConfig(level=logging.INFO)
# logging.getLogger('suds.client').setLevel(logging.DEBUG)
# logging.getLogger('suds.transport').setLevel(logging.DEBUG)
log = logging.getLogger()

config_filename = args.config
if not os.path.isfile(config_filename):

    os.makedirs(os.path.dirname(config_filename), exist_ok=True)
    with open(config_filename, 'w') as f:
        log.debug("Creating a new configuration file in '%s'" % (config_filename))

        # Create a default config if config file doesn't exist
        config['DEFAULT']['country_id'] = '1'
        config['DEFAULT']['cache_location'] = os.path.join(xdg_cache_home, 'allegro-prodsearch', 'country-%d' % (int(config['DEFAULT']['country_id'])) )
        config['DEFAULT']['wsdl'] = 'https://webapi.allegro.pl/service.php?wsdl'
        config.write(f)

else:
    log.debug("Trying to load configuration file from '%s'" % (config_filename))
    config.read(config_filename)


client = Client(config['DEFAULT']['wsdl'])

webapi_key = os.getenv('ALLEGRO_WEBAPI_KEY')

categories = None

# Check if we can load from cache
cache_filename = os.path.join(config['DEFAULT']['cache_location'], 'categories-latest.pickle')

if os.path.isfile(cache_filename):
    with open(cache_filename, "rb") as f:
        categories = pickle.load(f)

def path(categories, cat_id):
    if cat_id == 0:
        return "/Allegro"
    return path(categories, categories[cat_id]['catParent']) + '/' + categories[cat_id]['catName']

total_results = []
for category_id in args.category:

    query = args.query
    filters_def = {
        'closed': 'true',
        'condition': 'used',
        'category': category_id,
        'search': query
    }

    filter = client.factory.create("ArrayOfFilteroptionstype")

    for filter_id, value in filters_def.items():
        f = client.factory.create("FilterOptionsType")
        f.filterId = filter_id
        f.filterValueId = client.factory.create("ArrayOfString")
        f.filterValueId.item = value
        filter.item.append(f)

    sort_options = client.factory.create("SortOptionsType")
    sort_options.sortType = "endingTime"
    sort_options.sortOrder = "desc"

    log.info("Searching for '%s' in category '%s'" % (query, category_id))

    query_result = client.service.doGetItemsList(webapiKey=webapi_key, countryId=config['DEFAULT']['country_id'], filterOptions=filter, resultScope=3)
    log.info("Search returned %d offers" % (query_result.itemsCount))

    log.debug(query_result)

    if query_result.itemsCount > 0:
        total_results.extend(query_result.itemsList.item)

from prettytable import PrettyTable
p = PrettyTable(["Auction title", "Category", "Bidders", "Finished", "Price"])
p.align["Auction title"] = p.align["ID"] = "l"

concluded_offers_count = 0
for item in total_results:

    # Skip offers that did not conclude
    if item.biddersCount == 0:
        continue

    # Find the price
    price = None

    for price_item in item.priceInfo.item:
        if price_item.priceType == "bidding" or price_item.priceType == "buyNow":
            price = price_item.priceValue

    p.add_row([item.itemTitle, "%d (%s)" % (item.categoryId, path(categories, item.categoryId)) if categories is not None else item.categoryId, item.biddersCount, item.endingTime.strftime("%Y-%m-%d"), price])
    concluded_offers_count += 1

log.info("Summarizing %d returned offers, %d offers concluded" % (len(total_results), concluded_offers_count))
print(p.get_string(sortby="Finished", reversesort=True))
