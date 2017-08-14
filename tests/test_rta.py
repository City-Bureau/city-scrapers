# -*- coding: utf-8 -*-

import pytest

from tests.utils import file_response
from documenters_aggregator.spiders.rta import RtaSpider

page_response = file_response('files/rta.html')
events_response = file_response('files/rta_calendar.html')
events_response.meta['description'] = "Test Description"

spider = RtaSpider()
parsed_items = [item for item in spider.parse_iframe(events_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[0]['name'] == 'Board of Directors'


def test_description():
    assert parsed_items[0]['description'] == 'Test Description'


def test_start_time():
    assert parsed_items[0]['start_time'] == '2017-08-24T08:30:00-05:00'


def test_end_time():
    assert parsed_items[0]['end_time'] is None


def test_id():
    assert parsed_items[0]['id'] == '2017-08-24-board-of-directors'


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == 'Not classified'


@pytest.mark.parametrize('item', parsed_items)
def test_status(item):
    assert item['status'] == 'tentative'


@pytest.mark.parametrize('item', parsed_items)
def test_location(item):
    assert item['location'] == {
        'url': 'http://www.rtachicago.org/index.php/about-us/contact-us.html',
        'name': 'RTA Administrative Offices',
        'coordinates': None,
        'address': '175 W. Jackson Blvd, Suite 1650, Chicago, IL 60604'
    }


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'


# @TODO in the future, could consider passing multiple items + expected values.
# @pytest.mark.parametrize("parsed_value,expected", [
    # (parsed_items[0]['name'], 'PANDAS/PANS Advisory Council'),
    # (parsed_items[2]['name'], 'PAC: Maternal Mortality Review Committee Meeting'),
# ])
