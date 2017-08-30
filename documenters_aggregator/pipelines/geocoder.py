import geocoder

class GeocoderPipeline(object):
    """
    Performs geocoding of an event if it doesn't already have
    coordinates.
    """
    def process_item(self, item, spider):
        if item['location']['coordinates'] is None:
            item['location']['coordinates'] = _geocode_address(item.location.name)
            return item

    def _geocode_address(self, address):
        g = geocoder.google(address)
        coords = g.latlng
        return { 'latitude': coords[0],
                 'longitude': coords[1] }
