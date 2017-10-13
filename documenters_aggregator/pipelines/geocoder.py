"""
Geocoder.
"""
import json
import os

from mapzen.api import MapzenAPI


class GeocoderPipeline(object):
    def __init__(self, session=None):
        self.client = MapzenAPI('mapzen-WKDW883')

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
                'latitude': coordinates[0],
                'longitude': coordinates[1],
            }
            item['geocode'] = json.dumps(geocode, indent=4, sort_keys=True)
        except Exception as e:
            spider.logger.exception('Message')
            spider.logger.error(json.dumps(item, indent=4, sort_keys=True))
            raise DropItem('Could not geocode {0}'.format(item['id']))

        spider.logger.debug(json.dumps(item, indent=4, sort_keys=True))
        return item
