"""
This pipeline cleans up the addresses.
"""
import usaddress
import re
from fuzzywuzzy import process
import json
import requests
import collections

CITY_FILE = requests.get('https://data.cityofchicago.org/resource/pasq-g8mx.json').json()
CITY_STREETS = set([d['street'] for d in CITY_FILE])


class AddressPipeline(object):
    """
    Stub pipeline to clean addresses into structured data
    """
    def __init__(self):
        pass

    """
    Process an item.
    """
    def process_item(self, item, spider):
        address_components = self.street_clean_dict(item.get('location', {}),'Chicago', 'IL')
        item['address_components'] = address_components
        return item

    def street_clean_dict(self, location_dict, default_city, default_state):
        """
        Clean and item's location to make a mapzen query.
        @TODO: Fuzzy match addresses against Chicago Data Portal Address API
        """
        name = location_dict.get('name', '').strip()
        query = location_dict.get('address', '').strip()
        if name != '':
            query = ', '.join([name, query])  # combine '{name}, {address}'
        query= re.sub('city hall((?!.*chicago, il).)*$', 'City Hall 121 N LaSalle Dr, Chicago, IL', query, flags=re.I) #replace city hall 
        try:
            querydict = usaddress.tag(query)[0]
        except usaddress.RepeatedLabelError as e:
            querydict = self.bad_address_tag(e.parsed_string)
        city = querdict.get('PlaceName', default_city) # replace w default city if blank
        state = querdict.get('StateName', default_state)  # replace w default state if blank
        street = querdict.get('StreetName', '')
        if street != '': # fuzzy matching on closest street name if misspelled
            street = process.extract(street, CITY_STREETS, limit=1)
        querydict['PlaceName'] = city
        querydict['StateName'] = state
        querydict['StreetName'] = street
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
        counts = collections.Counter(t[1] for t in parsed_string
        parsedDict = collections.OrderedDict()

        for t in parseList:
            num = counts.get(t[1], 0)
            signifier = t[1]
            if num > 1:
                signifier = signifier+str(num)
                counts[t[1]] = num-1
            parseDict[signifier] = t[0]
        return parseDict
