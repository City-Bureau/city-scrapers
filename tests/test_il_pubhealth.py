# -*- coding: utf-8 -*-

import pytest

from tests.utils import file_response
from documenters_aggregator.spiders.il_pubhealth import Il_pubhealthSpider

test_response = file_response('files/il_pubhealth.html', url='http://www.dph.illinois.gov/events')
spider = Il_pubhealthSpider()
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
    assert parsed_items[4]['start_time'].isoformat() == '2017-08-09T11:00:00-05:00'


def test_end_time():
    assert parsed_items[4]['end_time'].isoformat() == '2017-08-09T15:00:00-05:00'


def test_id():
    assert parsed_items[5]['id'] == 'il_pubhealth/201708100830/16556/levels_of_care_work_group_hospital_designations_redesignations_change_of_networks'


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
        'url': '',
        'name': '',
        'address': '',
        'coordinates': {'latitude': '', 'longitude': ''}
    }


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'


@pytest.mark.parametrize('item', parsed_items)
def test_timezone(item):
    assert item['timezone'] == 'America/Chicago'


def test_sources():
    assert parsed_items[0]['sources'] == [{'url': 'http://www.dph.illinois.gov/events', 'note': ''}]

# @TODO in the future, could consider passing multiple items + expected values.
# @pytest.mark.parametrize("parsed_value,expected", [
    # (parsed_items[0]['name'], 'PANDAS/PANS Advisory Council'),
    # (parsed_items[2]['name'], 'PAC: Maternal Mortality Review Committee Meeting'),
# ])
