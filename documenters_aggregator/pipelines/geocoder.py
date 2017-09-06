"""
To use this pipeline, you must `export MAPQUEST_API_KEY=<SECRET KEY>`;
see http://geocoder.readthedocs.io/providers/MapQuest.html for more
information.
"""
import geocoder
import requests


class GeocoderPipeline(object):
    def __init__(self, session=None):
        if session is None:
            session = requests.Session()
        self.session = session

    def process_item(self, item, spider):
        """
        Performs geocoding of an event if it doesn't already have
        coordinates.
        """
        if item['location']['coordinates'] is None:
            item['location']['coordinates'] = self._geocode_address(item['location']['name'])
            return item

    def _geocode_address(self, address):
        g = geocoder.mapquest(address, session=self.session)
        coords = g.latlng
        return {'latitude': str(coords[0]),
                'longitude': str(coords[1])}
