import geocoder
import requests

"""
This pipeline decorates items with latitude and longitude by geocoding their
addresses.
"""


class MapboxPipeline(object):
    """
    Stub pipeline to geocode using Mapbox.
    """

    def __init__(self):
        # the geocoder library. this way we can use other libraries if needed or write/extend our own
        self.engine = 'geocoder'
        # api key, mapbox in this case. best practice would be to hide this
        self.key = 'pk.eyJ1IjoiZWFzaGVybWEiLCJhIjoiY2oxcW51Nzk2MDBkbTJxcGUxdm85bW5xayJ9.7mL0wQ7cjifWwt5DrXMuJA'  #API

    """
    Process an item.
    """

    def process_item(self, item, spider):
        try:
            if item['location']['coordinates']['latitude'] is None:
                with requests.Session() as session:
                    response = self.get_geocoder_query(
                        item['location']['address'],
                        bbox=[-87.940102, 41.643921, -87.523987, 42.023022], session=session)
                    #I'm not sure the above session is being persisted the way I would like
                    item['location']['coordinates']['longitude'] = response[0].lng
                    item['location']['coordinates']['latitude'] = response[0].lat
                    item['location']['url'] = response[0].url

            return item
        except Exception as e:
            print(e)
            raise

    def get_geocoder_query(self, address=None, bbox=None, **kwargs):

        if self.engine == 'geocoder':
            provider = 'mapbox'
            params = {
                'engine': self.engine,
                'provider': provider,
                'key': self.key
            }
            query_params = {
                'address': address,
                'bbox':
                bbox  # bounds to search in, useful if we dont have city/zip in address
            }

            #query = "{engine}.{provider}('{address}', key='{key}')".format(**params)

            result = getattr(geocoder, provider)(
                query_params['address'], key=params['key'], **query_params)
            return result, str(query_params)
        return query
