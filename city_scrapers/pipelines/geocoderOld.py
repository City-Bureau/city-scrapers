"""
Geocoder.
"""
import json
import os
import requests
import datetime
import time
from random import randint
import re

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
        # skip geocoding if event is in the past
        if item.get('start_time') is None:
            spider.logger.debug('GEOCODER PIPELINE: Ignoring event without start_time {0}'.format(item['id']))
            return item
        dt = item['start_time']
        if dt < datetime.datetime.now(dt.tzinfo):
            spider.logger.debug('GEOCODER PIPELINE: Ignoring past event {0}'.format(item['id']))
            return item

        query = self._get_mapzen_query(item.get('location', {}))
        if not query:
            spider.logger.debug('GEOCODER PIPELINE: Empty query. Not geocoding {0}'.format(item['id']))
            return item

        for suffix in ['', ' ave.', ' st.']:
            new_query = query.replace(', chicago, il', '{0}, chicago, il'.format(suffix))
            time.sleep(randint(0, 3))  # to avoid rate limiting?
            updated_item = self._update_fromDB(new_query, item)
            if updated_item:
                spider.logger.debug('GEOCODER PIPELINE: Geocoded item from airtable cache.')
                return updated_item

        bad_addresses = ['Chicago, IL, USA', 'Illinois, USA', '']
        for suffix in ['', ' ave.', ' st.']:
            new_query = query.replace(', chicago, il', '{0}, chicago, il'.format(suffix))
            geocoded_item = self._geocode(new_query, item, spider)
            address = geocoded_item['location']['address']
            if (address not in bad_addresses) and (address.endswith('Chicago, IL, USA')) and (self._hasDigit(address)):
                write_item = {
                    'mapzen_query': new_query,
                    'longitude': geocoded_item['location']['coordinates']['longitude'],
                    'latitude': geocoded_item['location']['coordinates']['latitude'],
                    'name': geocoded_item['location']['name'],
                    'address': geocoded_item['location']['address'],
                    'geocode': geocoded_item['geocode'],
                    'community_area': geocoded_item['community_area']
                }
                self._geocodeDB_write(spider, write_item)
                spider.logger.debug('GEOCODER PIPELINE: Geocoded item from mapzen.')
                return geocoded_item

        spider.logger.exception(("GEOCODER PIPELINE: Couldn't geocode using mapzen or airtable cache. "
                                 "Query: {0}. Item id: {1}").format(query, item['id']))
        return item

    def _geocode(self, query, item, spider):
        """
        Makes a Mapzen query and returns results.
        """
        try:
            geocode = self.client.search(query, boundary_country='US', format='keys')
        except ValueError:
            spider.logger.debug(('GEOCODER PIPELINE: Could not geocode, skipping. '
                                 'Query: {0}. Item id: {1}').format(query, item['id']))
        except Exception as e:
            spider.logger.info(('GEOCODER PIPELINE: Unknown error when geocoding, skipping. '
                                'Query: {0}. Item id: {1}. Message: {2}').format(query, item['id'], str(e)))
        else:
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
                'community_area': geocode['features'][0]['properties'].get('neighbourhood', '')
            }
            geocoded_item = item.copy()
            geocoded_item.update(new_data)
            return geocoded_item
        return {'location': {'address': ''}}

    def _hasDigit(self, string):
        """
        Returns True if the string contains a digit.
        """
        return any(char.isdigit() for char in string)

    def _get_mapzen_query(self, location_dict):
        """
        Clean and item's location to make a mapzen query.
        All cleaned queries are lowercase and
        end with ', chicago, il'.
        """
        name = location_dict.get('name', '').strip()
        address = location_dict.get('address', '').strip()
        query = ', '.join([name, address]).strip(', ').lower()  # combine '{name}, {address}' and lowercase
        query = query.replace('-', ' ').replace('/', ' ')  # remove special characters
        query = query.replace('milwukee', 'milwaukee').replace('milwuakee', 'milwaukee')  # fix misspellings
        query = query.replace('n.', 'n. ').replace('s.', 's. ').replace('e.', 'e. ').replace('w.', 'w. ')
        query = re.sub(r' +', ' ', query)  # remove repeated spaces
        query = re.sub(r',* chicago,*( il)* *\d*$', ', chicago, il', query)  # remove zip code, standardize ', chicago, il'
        if not query:
            return ''
        if 'city hall' in query.lower():
            return 'chicago city hall, chicago, il'
        if not query.endswith(', chicago, il'):
            return '{0}, chicago, il'.format(query)
        else:
            return query

    def _update_fromDB(self, query, item):
        """
        Query the geocode database and update item
        with results.
        """
        fetched_item = self._geocodeDB_fetch(query)
        try:
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
                'geocode': str(fetched_item.get('geocode', '')),
                'community_area': fetched_item.get('community_area', '')
            }
        except:
            return {}
        else:
            updated_item = item.copy()
            updated_item.update(new_data)
            return updated_item

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
        spider.logger.debug('GEOCODER PIPELINE: Caching {0}'.format(item['mapzen_query']))
        item['geocode_date_updated'] = datetime.datetime.now().isoformat()
        airtable_item = self.geocode_database.match('mapzen_query', item['mapzen_query'])
        if airtable_item:
            self.geocode_database.update_by_field('mapzen_query', item['mapzen_query'], item)
        else:
            self.geocode_database.insert(item)
