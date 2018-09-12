# -*- coding: utf-8 -*-
from datetime import date, time

import pytest

from tests.utils import file_response
from city_scrapers.spiders.cook_hospitals import CookHospitalsSpider

test_response = file_response('files/cook_hospitals.html', url='http://www.cookcountyhhs.org/about-cchhs/governance/board-committee-meetings/')
spider = CookHospitalsSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]

def test_name():
    assert parsed_items[0]['name'] == 'Meetings of the Board of Directors'


def test_description():
    assert parsed_items[0]['event_description'] == ''


def test_times():
    assert parsed_items[0]['start'] == {
        'date': date(2017, 1, 27),
        'time': time(9, 00),
        'note': ''
    }

    assert parsed_items[0]['end'] == {
        'date': date(2017, 1, 27),
        'time': time(12, 00),
        'note': 'End time is estimated to be 3 hours after the start time'
    }

def test_documents():
    assert parsed_items[0]['documents'] == [
        {'url': 'http://www.cookcountyhhs.org/wp-content/uploads/2016/01/01-27-17-Board-Agenda.pdf',
         'note': 'agenda and materials'},
        {'url': 'http://www.cookcountyhhs.org/wp-content/uploads/2017/02/01-27-17-Board-scan-Minutes.pdf',
         'note': 'minutes'},
    ]
    assert parsed_items[-1]['documents'] == []


def test_id():
    assert parsed_items[0]['id'] == 'cook_hospitals/201701270900/x/meetings_of_the_board_of_directors'


def test_status():
    assert parsed_items[0]['status'] == 'passed'


def test_location():
    assert parsed_items[0]['location'] == {
        'name': '',
        'address': '1900 W. Polk, Second Floor Conference Room, Chicago, Illinois',
        'neighborhood': '',
    }


def test_classification():
    assert parsed_items[0]['classification'] == 'Board'
    assert parsed_items[-1]['classification'] == 'Committee'


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'


@pytest.mark.parametrize('item', parsed_items)
def test_sources(item):
    assert item['sources'] == [
        {'url': 'http://www.cookcountyhhs.org/about-cchhs/governance/board-committee-meetings/',
         'note': ''}
    ]
