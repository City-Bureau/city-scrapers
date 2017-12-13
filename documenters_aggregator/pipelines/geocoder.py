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
        Geocodes an item by:
            (1) looking in airtable cache
            (2) making a mapzen query and adding the result
                to the cache if (1) is not found

        Mapzen queries are standardized to end with ', Chicago, IL'. 

        If something like '5100 Milwaukee Chicago, IL' is not found,
        '5100 Milwaukee Ave., Chicago, IL' and
        '5100 Milwaukee St., Chicago, IL' are also tried.
        """
        query = self._get_mapzen_query(item.get('location', {}))

        for suffix in ['', ' Ave.', ' St.']:
            new_query = query.replace(', Chicago, IL', '{0}, Chicago, IL'.format(suffix))
            time.sleep(randint(0, 3))  # to avoid rate limiting?
            updated_item = self._update_fromDB(query, item)
            if updated_item:
                return updated_item

        bad_addresses = ['Chicago, IL, USA', 'Illinois, USA' , '']
        for suffix in ['', ' Ave.', ' St.']:
            new_query = query.replace(', Chicago, IL', '{0}, Chicago, IL'.format(suffix))
            geocoded_item = self._geocode(query, item)
            address = geocoded_item['location']['address']
            if (address not in bad_addresses) and (address.endswith('Chicago, IL, USA')) and (self._hasDigit(address)):
                write_item = {
                    'mapzen_query': query,
                    'longitude': geocoded_item['location']['coordinates']['longitude'],
                    'latitude': geocoded_item['location']['coordinates']['latitude'],
                    'name': geocoded_item['location']['name'],
                    'address': geocoded_item['location']['address'],
                    'geocode': geocoded_item['geocode'],
                    'community_area': geocoded_item['community_area']
                }
                self._geocodeDB_write(spider, write_item)
                return geocoded_item

        spider.logger.exception("Couldn't geocode using mapzen or airtable cache.")
        spider.logger.error(json.dumps(item, indent=4, sort_keys=True))
        return item

    def _geocode(self, query, item):
        """
        Makes a Mapzen query and returns results.
        """
        try:
            geocode = self.client.search(query, boundary_country='US', format='keys')
            new_data = {
                'location': {
                    'coordinates': {
                        'longitude': str(geocode['features'][0]['geometry']['coordinates'][0]),
                        'latitude': str(geocode['features'][0]['geometry']['coordinates'][1])
                    },
                    'name': geocode['geocoding']['query']['parsed_text'].get('query', ''),
                    'address': geocode['features'][0]['properties']['label'],
                    'url': item.get('location', {'url': ''}).get('url', '')
                },
                'geocode': json.dumps(geocode, indent=4, sort_keys=True),
                'community_area': geocode['features'][0]['properties']['neighbourhood']
            }
            item.update(new_data)
            return item
        except ValueError:
            spider.logger.warn('Could not geocode {0}-{1}, skipping.'.format(spider.name, item['id']))
        except Exception:
            spider.logger.warn('Unknown error when geocoding, skipping. Message:')
        return {'location': {'address': ''}}

    def _hasDigit(self, string):
        """
        Returns True if the string contains a digit.
        """
        return any(char.isdigit() for char in string)

    def _get_mapzen_query(self, location_dict):
        """
        Clean and item's location to make a mapzen query
        """
        name = location_dict.get('name', '').strip()
        address = location_dict.get('address', '').strip()
        query = ', '.join([name, address]).strip(', ')
        query = query.replace('-', ' ').replace(',', ' ').replace('/', ' ')
        query = query.replace('Milwukee', 'Milwaukee').replace('Milwuakee', 'Milwaukee')
        query = query.replace('N.', 'N. ').replace('S.', 'S. ').replace('E.', 'E. ').replace('W.', 'W. ')
        if not query:
            return ''
        if 'city hall' in query.lower():
            return 'Chicago City Hall, Chicago, IL'
        if query.endswith(', Chicago, IL'):
            return query
        if query.endswith(' Chicago'):
            return '{0}, IL'.format(query)
        else:
            return '{0}, Chicago, IL'.format(query)

    def _update_fromDB(self, query, item):
        """
        Query the geocode database and update item
        with results.
        """
        fetched_item = self._geocodeDB_fetch(query)
        if fetched_item:
            new_data = {
                'location': {
                    'coordinates': {
                        'longitude': str(fetched_item['longitude']),
                        'latitude': str(fetched_item['latitude'])
                    },
                    'name': fetched_item.get('name', ''),
                    'address': fetched_item['address'],
                    'url': item.get('location', {'url': ''}).get('url', '')
                },
                'geocode': str(fetched_item['geocode']),
                'community_area': fetched_item['community_area']
            }
            item.update(new_data)
            return item
        return {}

    def _geocodeDB_fetch(self, query):
        """
        Fetch from geocode_database.
        """
        try:
            return self.geocode_database.match('mapzen_query', query)['fields']
        except:
            return None

    def _geocodeDB_write(self, spider, item):
        """
        Write to geocode_database.
        """
        spider.logger.debug('GEOCODE PIPELINE: Caching {0}'.format(item['mapzen_query']))
        item['geocode_date_updated'] = datetime.datetime.now().isoformat()
        airtable_item = self.geocode_database.match('mapzen_query', item['mapzen_query'])
        if airtable_item:
            self.geocode_database.update_by_field('mapzen_query', item['mapzen_query'], item)
        else:
            self.geocode_database.insert(item)
