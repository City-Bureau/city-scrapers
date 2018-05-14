"""
Geocoder.
"""
import geocoder
import requests
import usaddress
import re
import os
from airtable import Airtable

AIRTABLE_BASE_KEY = os.environ.get('DOCUMENTERS_AGGREGATOR_AIRTABLE_BASE_KEY')
AIRTABLE_GEOCODE_TABLE = os.environ.get('DOCUMENTERS_AGGREGATOR_AIRTABLE_GEOCODE_TABLE')

TAMU_API_KEY = 'e8a8f1283b3440c4b248adb52204c8ae' #temporary for testing


class GeocoderPipeline(object):
    def __init__(self, session=None):
        if session is None:
            session = requests.Session()
        self.session = session
        #self.geocode_database = Airtable(AIRTABLE_BASE_KEY, AIRTABLE_GEOCODE_TABLE)

    def process_item(self, item, spider):
        """
        Performs geocoding of an event if it doesn't already have
        coordinates.
        """
        if item['location']['coordinates'] is None:
            query = self._parse_address(item.get('location', {}))
            if not query:
                spider.logger.debug('GEOCODER PIPELINE: Empty query. Not geocoding {0}'.format(item['id']))
                return item
            item['location']['coordinates'] = self._geocode_address(query,'Chicago', 'IL')
            return item

    def _geocode_address(self, query, default_city, default_state):
        city_found = query.get('PlaceName', default_city) # replace w default city if blank
        state_found = query.get('StateName', default_state)  # replace w default state if blank
        zipcode_found = query.get('ZipCode', '')
        address = ', '.join(v for (k, v) in query.items() if k not in ['PlaceName', 'StateName', 'ZipCode'])
        g = geocoder.tamu(address,
                          city=city_found,
                          state=state_found,
                          zipcode=zipcode_found,
                          session=self.session, key=TAMU_API_KEY)
        coords = g.latlng
        return {'latitude': str(coords[0]), 'longitude': str(coords[1])}

    def _parse_address(self, location_dict):
        """
        Disabled Fuzzy match Chicago addresses on Chicago Data Portal Address API
        """
        name = location_dict.get('name', None)
        address = location_dict.get('address', '')

        if name is None and address is None:
            return {}

        if name is None:
            query = address.strip()
        else:
            query = ', '.join([name.strip(), address.strip()])

        # replace city hall
        query = re.sub('city hall((?!.*chicago, il).)*$',
                       'City Hall 121 N LaSalle St., Chicago, IL', query, flags=re.I)

        try:
            querydict = usaddress.tag(query)[0]
        except usaddress.RepeatedLabelError as ex: 
        # include multiple errors
            querydict = self.bad_address_tag(ex.parsed_string)

        return querydict

    def bad_address_tag(parsed_string):
        """
        Turn the usaddress parse list of tuples with
        RepeatedLabelError issues (duplicate labels)
        Returns the second label as the valid label.
        Thus far the only duplicate label appears to be due to
        incorrectly identifying an earlier string as the PlaceName, Thus
        we are encoding the second PlaceName as the true PlaceName while
        preserving the order in an ordered dictionary.
        """
        counts = collections.Counter(t[1] for t in parsed_string)
        parsedDict = collections.OrderedDict()

        for t in parsed_string:
            num = counts.get(t[1], 0)
            signifier = t[1]
            if num > 1:
                signifier = signifier+str(num)
                counts[t[1]] = num-1
            parsedDict[signifier] = t[0]
        return parsedDict

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