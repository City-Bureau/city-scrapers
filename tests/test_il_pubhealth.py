# -*- coding: utf-8 -*-
from datetime import date, time

import pytest

from tests.utils import file_response
from city_scrapers.spiders.il_pubhealth import Il_pubhealthSpider

test_response = file_response('files/il_pubhealth.html', url='http://www.dph.illinois.gov/events')
spider = Il_pubhealthSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]

def test_name():
    assert parsed_items[2]['name'] == 'PAC: Maternal Mortality Review Committee Meeting'


def test_event_description():
    assert parsed_items[1]['event_description'] == """CONFERENCE ROOMS
122 S. Michigan, 7th Floor, Chicago, Room 711
535 West Jefferson St., 5th Floor, Springfield
Conference Call Information
Conference Call-In#: 888.494.4032
Access Code: 6819028741
Interested persons may contact the Office of Women’s Health at 312-814-4035 for information"""


def test_start():
    assert parsed_items[4]['start'] == {
        'date': date(2017, 8, 9),
        'time': time(11, 00),
        'note': ''
    }


def test_end_time():
    assert parsed_items[4]['end'] == {
        'date': date(2017, 8, 9),
        'time': time(15, 00),
        'note': ''
    }


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
    assert item['status'] == 'passed'


def test_high_confidence_location():
    addr_lines = [
        'Top of the Building',
        '69 West Washington St., 35th Floor, Chicago',
        '-OR-',
        '500 Vernon, Normal, IL 61761'
    ]
    address = spider._find_high_confidence_address(addr_lines)

    assert address == '69 West Washington St., 35th Floor, Chicago'

def test_medium_confidence_location():
    addr_lines = [
        'Top of the Building',
        '122 S. Michigan Avenue, Room 711, West Chicago',
        '-OR-',
        '500 Vernon, Normal, IL 61761'
    ]
    address = spider._find_medium_confidence_address(addr_lines)

    assert address == '122 S. Michigan Avenue, Room 711, West Chicago'

def test_low_confidence_location():
    addr_lines = [
        'Top of the Building',
        '1234 Main St, West Side, 57th Floor, Chicago, IL',
        '-OR-',
        '500 Vernon, Normal, IL 61761'
    ]
    address = spider._find_low_confidence_address(addr_lines)

    assert address == '1234 Main St, West Side, 57th Floor, Chicago, IL'

def test_no_matching_location():
    assert parsed_items[8]['location'] == {
        'name': '',
        'address': 'multiple locations not in Chicago, see description',
        'neighborhood': '',
    }

def test_documents():
    assert parsed_items[0]['documents'] == []
    assert parsed_items[1]['documents'] == [{
        'url': 'http://www.dph.illinois.gov/sites/default/files/8-3-17-LOC-3-and-4-Agenda.pdf',
        'note': 'agenda',
    }]

@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'


def test_sources():
    assert parsed_items[0]['sources'] == [{'url': 'http://www.dph.illinois.gov/events', 'note': ''}]

# @TODO in the future, could consider passing multiple items + expected values.
# @pytest.mark.parametrize("parsed_value,expected", [
    # (parsed_items[0]['name'], 'PANDAS/PANS Advisory Council'),
    # (parsed_items[2]['name'], 'PAC: Maternal Mortality Review Committee Meeting'),
# ])
