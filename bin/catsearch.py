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
argparser.add_argument('query', metavar='QUERY', nargs='+', help='The query string to search')

args = argparser.parse_args()

logging.basicConfig(level=logging.INFO)
# logging.getLogger('suds.client').setLevel(logging.DEBUG)
# logging.getLogger('suds.transport').setLevel(logging.DEBUG)
log = logging.getLogger()

log.debug("Trying to load configuration file from '%s'" % (args.config))
config.read(args.config)

webapi_key = os.getenv('ALLEGRO_WEBAPI_KEY')

client = Client(config['DEFAULT']['wsdl'])

categories = None

# Check if we can load from cache
cache_filename = os.path.join(config['DEFAULT']['cache_location'], 'categories-latest.pickle')

if os.path.isfile(cache_filename):
    with open(cache_filename, "rb") as f:
        categories = pickle.load(f)
else:
    log.warn("Cache file '{}' could not be found, requesting categories tree from server".format(cache_filename))

    all_status = client.service.doQueryAllSysStatus(countryId=config.country_id, webapiKey=webapi_key)

    sys_status = list(filter(lambda status: status.countryId == config.country_id, all_status.item))[0]
    # Result fields:
    #   programVersion = "1.0"
    #   catsVersion = "1.4.64"
    #   apiVersion = "1.0"
    #   attribVersion = "1.0"
    #   formSellVersion = "1.11.17"
    #   siteVersion = "1.0"
    #   verKey = 1500555571
    cats_version = sys_status.catsVersion

    cache_filename = os.path.join(cache_dir,'categories-%s.pickle' % (cats_version))

    # Download categories
    categories_reply = client.service.doGetCatsData(countryId=config.country_id, webapiKey=webapi_key, localVersion=0)

    # Convert the response to a hash indexed by the category ID
    categories = {}
    for cat in categories_reply.catsList.item:
        # O_O
        # https://stackoverflow.com/a/39286285
        categories.update( {
            cat['catId']: { key: value for key, value in cat.__dict__.items() if not key.startswith("__") }
            } )

    # Create the cache dir and pickle the categories tree there
    os.makedirs(os.path.dirname(cache_dir), exist_ok=True)
    with open(cache_filename, "wb") as f:
        pickle.dump(categories, f)
        log.info("Cached categories tree version '%s' in '%s'" % (cats_version, cache_filename))

    # Symlink the latest version
    fd = os.open(os.path.dirname(cache_filename), os.O_RDONLY)
    os.symlink(cache_filename, "categories-latest.pickle", dir_fd=fd)
    os.close(fd)

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

