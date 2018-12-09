#!/usr/bin/env python3

from suds.client import Client
from xdg.BaseDirectory import xdg_cache_home, xdg_config_home

from configparser import ConfigParser
import pickle
import os
import logging
import sys
import argparse

config = ConfigParser()

argparser = argparse.ArgumentParser(description="Search for a category")
argparser.add_argument('--config', metavar='FILE', default=os.path.join(xdg_config_home, 'allegro-prodsearch', 'config.ini'), help='Configuration file location')
argparser.add_argument('query', metavar='QUERY', nargs='*', help='The query string to search')

args = argparser.parse_args()

logging.basicConfig(level=logging.INFO)
# logging.getLogger('suds.client').setLevel(logging.DEBUG)
# logging.getLogger('suds.transport').setLevel(logging.DEBUG)
log = logging.getLogger()

config_filename = args.config
if not os.path.isfile(config_filename):

    os.makedirs(os.path.dirname(config_filename), exist_ok=True)
    with open(config_filename, 'w') as f:
        log.info("Creating a new configuration file in '%s'" % (config_filename))

        # Create a default config if config file doesn't exist
        config['DEFAULT']['country_id'] = '1'
        config['DEFAULT']['cache_location'] = os.path.join(xdg_cache_home, 'allegro-prodsearch', 'country-%d' % (int(config['DEFAULT']['country_id'])) )
        config['DEFAULT']['wsdl'] = 'https://webapi.allegro.pl/service.php?wsdl'
        config.write(f)

else:
    log.debug("Trying to load configuration file from '%s'" % (config_filename))
    config.read(config_filename)

webapi_key = os.getenv('ALLEGRO_WEBAPI_KEY')

client = Client(config['DEFAULT']['wsdl'])

# Get version of category tree
#
# Reference: https://allegro.pl/webapi/documentation.php/show/id,1079#method-input
#
# sysvar | int | required
# Component whose value is to be loaded (3 - category's tree structure, 4 - fields of a sale form).
cat_tree_info = client.service.doQuerySysStatus(countryId=config['DEFAULT']['country_id'], webapiKey=webapi_key, sysvar=3)
cat_version = cat_tree_info['info']

log.debug("Current category tree version '{}' key '{}'".format(cat_version, cat_tree_info['verKey']))

categories = None

cache_filename = os.path.join(config['DEFAULT']['cache_location'], 'country-{}'.format(config['DEFAULT']['country_id']), 'categories-{}.pickle'.format(cat_version))

# Check if we can load from cache
if os.path.isfile(cache_filename):
    with open(cache_filename, "rb") as f:
        categories = pickle.load(f)
else:
    log.warn("Cache file '{}' for version '{}' could not be found, requesting categories tree from server".format(cache_filename, cat_version))

    all_status = client.service.doQueryAllSysStatus(countryId=config['DEFAULT']['country_id'], webapiKey=webapi_key)

    log.debug("Server returned status information:")
    log.debug(all_status)

    sys_status = list(filter(lambda status: status.countryId == int(config['DEFAULT']['country_id']), all_status.item))[0]
    # Result fields:
    #   programVersion = "1.0"
    #   catsVersion = "1.4.64"
    #   apiVersion = "1.0"
    #   attribVersion = "1.0"
    #   formSellVersion = "1.11.17"
    #   siteVersion = "1.0"
    #   verKey = 1500555571
    cats_version = sys_status.catsVersion

    cache_filename = os.path.join(config['DEFAULT']['cache_location'], 'country-{}'.format(config['DEFAULT']['country_id']), 'categories-%s.pickle' % (cats_version))

    # Download categories
    categories_reply = client.service.doGetCatsData(countryId=config['DEFAULT']['country_id'], webapiKey=webapi_key, localVersion=0)

    # Convert the response to a hash indexed by the category ID
    categories = {}
    for cat in categories_reply.catsList.item:
        # O_O
        # https://stackoverflow.com/a/39286285
        categories.update( {
            cat['catId']: { key: value for key, value in cat.__dict__.items() if not key.startswith("__") }
            } )

    # Create the cache dir and pickle the categories tree there
    os.makedirs(os.path.join(config['DEFAULT']['cache_location'], 'country-{}'.format(config['DEFAULT']['country_id'])), exist_ok=True)
    with open(cache_filename, "wb") as f:
        pickle.dump(categories, f)
        log.info("Cached categories tree version '%s' in '%s'" % (cats_version, cache_filename))

log.info("Loaded %d categories" % len(categories.keys()))

def path(categories, cat_id):
    if cat_id == 0:
        return "/Allegro"
    return path(categories, categories[cat_id]['catParent']) + '/' + categories[cat_id]['catName']

results = []
for cat_id, cat in categories.items():
    cat_path = path(categories, cat_id)
    for q in args.query:
        if cat_path.lower().find(q.lower()) >= 0:
            results.append(dict(id=cat_id, path=cat_path))

for res in sorted(results, key=lambda r: r["path"]):
        print("%-7d %s" % (res["id"], res["path"]))

