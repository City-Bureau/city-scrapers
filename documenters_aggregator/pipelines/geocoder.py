"""
Geocoder.
"""
import json
import os
import requests
import datetime
import time
from random import randint

from mapzen.api import MapzenAPI
from airtable import Airtable

AIRTABLE_BASE_KEY = os.environ.get('DOCUMENTERS_AGGREGATOR_AIRTABLE_BASE_KEY')
AIRTABLE_GEOCODE_TABLE = os.environ.get('DOCUMENTERS_AGGREGATOR_AIRTABLE_GEOCODE_TABLE')


class GeocoderPipeline(object):
    def __init__(self, session=None):
        if session is None:
            session = requests.Session()
        self.session = session
        self.client = MapzenAPI(os.environ.get('MAPZEN_API_KEY'))
        self.geocode_database = Airtable(AIRTABLE_BASE_KEY, AIRTABLE_GEOCODE_TABLE)

    def process_item(self, item, spider):
        """
        Performs geocoding of an event if the location is not
        already in the geocode_database.
        """
        location = item['location'].get('address', '')
        if not location:
            location = item['location'].get('name', '')
        location = location.strip()  # attempt to clean up location, may need to do more

        time.sleep(randint(0, 3))  # to avoid rate limiting?
        fetched_item = self._geocodeDB_fetch(location)
        if fetched_item:
            item['location']['coordinates'] = {
                'longitude': str(fetched_item['longitude']),
                'latitude': str(fetched_item['latitude'])
            }
            item['geocode'] = str(fetched_item['geocode'])
            item ['community_area'] = str(fetched_item['community_area'])
            return item

        try:
            geocode = self.client.search(location, boundary_country='US', format='keys')
            coordinates = geocode['features'][0]['geometry']['coordinates']
            item['location']['coordinates'] = {
                'longitude': str(coordinates[0]),
                'latitude': str(coordinates[1])
            }
            item['geocode'] = json.dumps(geocode, indent=4, sort_keys=True)
            item['community_area'] = geocode['features'][0]['properties']['neighbourhood']
        except ValueError:
            spider.logger.warn('Could not geocode {0}-{1}, skipping.'.format(spider.name, item['id']))
        except Exception:
            spider.logger.exception('Unknown error when geocoding, skipping. Message:')
            spider.logger.error(json.dumps(item, indent=4, sort_keys=True))
        else:
            write_item = {'location': location,
                          'longitude': item['location']['coordinates']['longitude'],
                          'latitude': item['location']['coordinates']['latitude'],
                          'geocode': item['geocode'],
                          'community_area': item['community_area']}
            self._geocodeDB_write(spider, write_item)

        return item

    def _geocodeDB_fetch(self, location):
        """
        Fetch from geocode_database.
        """
        return self.geocode_database.match('location', location)['fields']

    def _geocodeDB_write(self, spider, item):
        """
        Write to geocode_database.
        """
        spider.logger.debug('GEOCODE PIPELINE: Caching {0}'.format(item['location']))
        item['geocode_date_updated'] = datetime.datetime.now().isoformat()
        self.geocode_database.insert(item)
