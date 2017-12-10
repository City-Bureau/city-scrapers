# -*- coding: utf-8 -*-

import pytest

from tests.utils import file_response
from documenters_aggregator.spiders.cook_hospitals import Cook_hospitalsSpider

test_response = file_response('files/cook_hospitals.html', url='http://www.cookcountyhhs.org/about-cchhs/governance/board-committee-meetings/')
spider = Cook_hospitalsSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[0]['name'] == 'Meetings of the Board of Directors'


def test_description():
    assert parsed_items[0]['description'] == 'http://www.cookcountyhhs.org/wp-content/uploads/2016/01/01-27-17-Board-Agenda.pdf'


def test_start_time():
    assert parsed_items[0]['start_time'] == '2017-01-27T09:00:00-06:00'


def test_id():
    assert parsed_items[0]['id'] == 'cook_hospitals/201701270900/x/meetings_of_the_board_of_directors'


def test_status():
    assert parsed_items[0]['status'] == 'passed'


def test_location():
    assert parsed_items[0]['location'] == {
        'url': '',
        'name': '1900 W. Polk, Second Floor Conference Room, Chicago, Illinois',
        'coordinates': {'latitude': '', 'longitude': ''},
    }


@pytest.mark.parametrize('item', parsed_items)
def test_end_time(item):
    assert item['end_time'] is None


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == 'Not classified'


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'


@pytest.mark.parametrize('item', parsed_items)
def test_sources(item):
    assert item['sources'] == [{'url': 'http://www.cookcountyhhs.org/about-cchhs/governance/board-committee-meetings/', 'note': ''}]


@pytest.mark.parametrize('item', parsed_items)
def test_timezone(item):
    assert item['timezone'] == 'America/Chicago'
