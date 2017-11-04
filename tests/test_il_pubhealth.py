# -*- coding: utf-8 -*-

import pytest

from tests.utils import file_response
from documenters_aggregator.spiders.il_pubhealth import Il-pubhealthSpider

test_response = file_response('files/il_pubhealth.html')
spider = Il-pubhealthSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[2]['name'] == 'PAC: Maternal Mortality Review Committee Meeting'


def test_description():
    assert parsed_items[1]['description'] == """CONFERENCE ROOMS
122 S. Michigan, 7th Floor, Chicago, Room 711
535 West Jefferson St., 5th Floor, Springfield
Conference Call Information
Conference Call-In#: 888.494.4032
Access Code: 6819028741
Interested persons may contact the Office of Women’s Health at 312-814-4035 for information"""


def test_start_time():
    assert parsed_items[4]['start_time'] == '2017-08-09T11:00:00-05:00'


def test_end_time():
    assert parsed_items[4]['end_time'] == '2017-08-09T15:00:00-05:00'


def test_id():
    assert parsed_items[5]['id'] == '16556'


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
        'url': None,
        'name': None,
        'coordinates': None,
    }


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'


# @TODO in the future, could consider passing multiple items + expected values.
# @pytest.mark.parametrize("parsed_value,expected", [
    # (parsed_items[0]['name'], 'PANDAS/PANS Advisory Council'),
    # (parsed_items[2]['name'], 'PAC: Maternal Mortality Review Committee Meeting'),
# ])
