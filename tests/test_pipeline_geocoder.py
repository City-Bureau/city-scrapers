import betamax
import requests
import tests.conftest as config
from tests.utils import test_item
from city_scrapers.pipelines.geocoder import GeocoderPipeline
import csv
from city_scrapers.utils import get_key
from random import randint

betamax_config = config.config


def test_geocoding():
    item = test_item()
    item['location']['coordinates'] = None

    session = requests.Session()
    recorder = betamax.Betamax(session, betamax_config.cassette_library_dir)

    with recorder.use_cassette('test_geocoding'):
        geocoder = GeocoderPipeline(session)
        #geocoder.geocode_database = {}
        geocoder.process_item(item, None)

    expected = {'latitude': '41.8833466352224', 'longitude': '-87.6323211702195'}
    assert item['location']['coordinates'] == expected


def test_compare_geo():
    with open('city_scrapers/local_outputs/geocache_mini.csv', 'r') as infile:
        oldcache = list(csv.DictReader(infile))
    infile.close()
    with open('city_scrapers/local_outputs/geocache_results.csv', 'w') as f:
        newnames = ("mapzen_query", "tamu_query", "location_name", "location_address",
                    "new_latitude", "new_longitude",
                    "cache_latitude", "cache_longitude",
                    "community_area", "geo_key", "geocode_date_updated")
        writer = csv.DictWriter(f, newnames)
        writer.writeheader()
        for row in oldcache:
            print(row)
            print(type(row))
            item = {
                '_type': 'event',
                'name': None,
                'description': None,
                'classification': None,
                'start_time': None,
                'end_time': None,
                'all_day': False,
                'timezone': 'America/Chicago',
                'status': 'tentative',
                'location': {
                    'address': row['address'],
                    'coordinates': None
                }
            }
            session = requests.Session()
            geocoder = GeocoderPipeline(session)
            item = geocoder.process_item(item, None)
            print(item)
            new_item = item
            new_item['new_latitude'] = new_item['location']['coordinates']['latitude']
            print(get_key(new_item, 'location.coordinates.latitude'))
            print(new_item['location']['coordinates']['latitude'])
            new_item['new_longitude'] = new_item['location']['coordinates']['longitude']
            new_item['location_address'] = new_item['location']['address']
            new_item['location_name'] = row['name']
            new_item['cache_latitude'] = row['latitude']
            new_item['cache_longitude'] = row['longitude']
            new_item['mapzen_query'] = row['mapzen_query']
            new_item['community_area'] = row['community_area']
            new_item['geo_key'] = row['geo_key']
            new_item['geocode_date_updated'] = row['geocode_date_updated']
            new_item = {k: v for k, v in new_item.items() if k in newnames}
            print(new_item)
            writer.writerow(new_item)
    f.close()


## Testing
log = open("city_scrapers/local_outputs/geocoding_logs.txt", "w")
print(test_compare_geo(), file=log)
testitem = {
    '_type': 'event',
    'name': None,
    'description': None,
    'classification': None,
    'start_time': None,
    'end_time': None,
    'all_day': False,
    'timezone': 'America/Chicago',
    'status': 'tentative',
    'location': {
        'address': 'filler',
        'coordinates': {
            'latitude': '9999',
            'longitude': '1111',
        }
    }
}
from city_scrapers.utils import get_key
get_key(testitem, 'location.coordinates.latitude')