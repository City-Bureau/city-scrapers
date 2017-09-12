import pytest
import scrapy

from tests.utils import file_response
from documenters_aggregator.spiders.cclba import CclbaSpider

import json
import datetime as dt
import pytz

"""
Uncomment below
"""

file = file_response('files/cclba.json')
spider = CclbaSpider()
data = json.loads(file.text)
test_response = scrapy.Selector(text=data['content'], type="html")
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[0]['name'] == 'CCLBA Finance Committee Meeting'


def test_description():
    assert parsed_items[0]['description'] == None


def test_start_time():
    assert parsed_items[0]['start_time'] == '2017-09-13T15:00:00+00:00'
    # Make a string in zulu time


def test_end_time():
    assert parsed_items[0]['end_time'] == None

def test_id():
    assert parsed_items[0]['id'] == '3381'


def test_all_day(item):
    assert parsed_items[0]['all_day'] is False


def test_classification(item):
    assert parsed_items[0]['classification'] == 'Not classified'


def test_status(item):
    assert parsed_items[0]['status'] == 'tentative'


def test_location(item):
    assert item['location'] == {
        'url': 'http://www.cookcountylandbank.org/',
        'name': "Cook County Administration Building, 69 W. Washington St., 22nd Floor, Conference Room 'A', Chicago, IL 60602",
        'coordinates': {
            'latitude': None,
            'longitude': None,
        },
    }

def test_sources(item):
    assert item['location'] == {
        'url': 'http://www.cookcountylandbank.org/events/cclba-finance-committee-meeting-09132017/',
        'note': "Event Page",
    }

def test__type(item):
    assert parsed_items[0]['_type'] == 'event'
