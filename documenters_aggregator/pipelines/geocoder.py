"""
Geocoder.
"""
import json
import os
import requests

from mapzen.api import MapzenAPI


class GeocoderPipeline(object):
    def __init__(self, session=None):
        if session is None:
            session = requests.Session()
        self.session = session
        self.client = MapzenAPI(os.environ.get('MAPZEN_API_KEY'))

    def process_item(self, item, spider):
        """
        Performs geocoding of an event if it doesn't already have
        coordinates.
        """
        try:
            location = item['location'].get('address') or item['location']['name']
            geocode = self.client.search(location, boundary_country='US', format='keys')
            coordinates = geocode['features'][0]['geometry']['coordinates']
            item['location']['coordinates'] = {
                'longitude': str(coordinates[0]),
                'latitude': str(coordinates[1]),
            }
            item['geocode'] = json.dumps(geocode, indent=4, sort_keys=True)
        except Exception as e:
            spider.logger.exception('Message')
            spider.logger.error(json.dumps(item, indent=4, sort_keys=True))
            raise DropItem('Could not geocode {0}'.format(item['id']))

        return item
