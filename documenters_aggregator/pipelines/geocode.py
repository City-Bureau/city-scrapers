# import json
# import os
# import requests
# import datetime
# import dateutil.parser
# import time
# from random import randint
# import re
import geocoder
"""
Alternate geocoding process. Sticks to just geocoding, and uses a
python library to make switching geocoding engines easier.
"""


class GeocoderPipeline(object):
    """
    Pipeline that geocodes given items.

    Uses the scraped location schema, for example:
    "location":
    {
    "url": null,
    "name": "6th District Station, 7808 S. Halsted St.",
    "coordinates": {"latitude": null, "longitude": null}
    }
    """

    # provider = 'arcgis'
    def process_item(self, item, spider):
        if item['location']['coordinates']['latitude'] is None:
            response = geocoder.arcgis(item['location']['name'])
            item['location']['coordinates']['latitude'] = response.lat
            item['location']['coordinates']['longitude'] = response.lng
            item['location']['url'] = response.url
        return item
