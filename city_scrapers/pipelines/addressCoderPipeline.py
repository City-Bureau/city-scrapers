"""
This pipeline cleans up the addresses.
"""
import usaddress
import re
import requests
import collections


CITY_FILE = requests.get('https://data.cityofchicago.org/resource/pasq-g8mx.json').json()
CITY_STREETS = set([d['street'] for d in CITY_FILE])


class AddressPipeline(object):
    """
    Process an item.
    """
    def process_item(self, item, spider):
        address_components = self.street_clean_dict(item.get('location', {}),'Chicago', 'IL')
        item['address_components'] = address_components
        return item

    def street_clean_dict(self, location_dict, default_city, default_state):
        """
        Disabled Fuzzy match Chicago addresses on Chicago Data Portal Address API
        """
        name = location_dict.get('name', None)
        address = location_dict.get('address', None)

        if name is None and address is None:
            return {}

        if name is None:
            query = address.strip()
        else:
            query = ', '.join([name.strip(), adaddress.strip()])

        # replace city hall
        query = re.sub('city hall((?!.*chicago, il).)*$',
                       'City Hall 121 N LaSalle Dr, Chicago, IL', query, flags=re.I)

        try:
            querydict = usaddress.tag(query)[0]
        except usaddress.RepeatedLabelError as ex:
            querydict = self.bad_address_tag(ex.parsed_string)

        city = querydict.get('PlaceName', default_city) # replace w default city if blank
        state = querydict.get('StateName', default_state)  # replace w default state if blank
        querydict['PlaceName'] = city
        querydict['StateName'] = state
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
