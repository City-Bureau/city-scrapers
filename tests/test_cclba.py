from tests.utils import file_response
from documenters_aggregator.spiders.cclba import CclbaSpider

"""
Uncomment below
"""

file = file_response('files/cclba.json')
spider = CclbaSpider()

# import pdb; pdb.set_trace()

test_response = file
parsed_items = list(spider.parse(test_response))


def test_name():
    assert parsed_items[0]['name'] == 'CCLBA Finance Committee Meeting'


def test_description():
    assert parsed_items[0]['description'] is None


def test_start_time():
    assert parsed_items[0]['start_time'] == '2017-09-13T15:00:00+00:00'
    # Make a string in zulu time


def test_end_time():
    assert parsed_items[0]['end_time'] is None


def test_id():
    assert parsed_items[0]['id'] == '3381'


def test_all_day():
    assert parsed_items[0]['all_day'] is False


def test_classification():
    assert parsed_items[0]['classification'] == 'Not classified'


def test_status():
    assert parsed_items[0]['status'] == 'passed'


def test_location():
    assert parsed_items[0]['location'] == {
        'url': 'http://www.cookcountylandbank.org/',
        'name': "Cook County Administration Building, 69 W. Washington St., 22nd Floor, Conference Room 'A', Chicago, IL 60602",
        'coordinates': {
            'latitude': None,
            'longitude': None,
        },
    }


def test_sources():
    assert parsed_items[0]['sources'] == {
        'url': 'http://www.cookcountylandbank.org/events/cclba-finance-committee-meeting-09132017/',
        'note': "Event Page",
    }


def test__type():
    assert parsed_items[0]['_type'] == 'event'
