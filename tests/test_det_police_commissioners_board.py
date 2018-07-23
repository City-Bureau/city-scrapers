from datetime import date, time

import pytest
import scrapy

from tests.utils import file_response
from city_scrapers.spiders.det_police_commissioners_board import DetPoliceDeptSpider

initial_response = file_response('files/det_city_all_events.html',
                                 'http://www.detroitmi.gov/Calendar-Events')
filtered_response = file_response('files/det_police_commissioners_board_all.html',
                                  'http://www.detroitmi.gov/Calendar-and-Events/CategoryID/166')
spider = DetPoliceDeptSpider()
parsed_items = [item for item in spider.parse(filtered_response) if isinstance(item, dict)]


def test_initial_request():
    initial_requests = list(spider.start_requests())
    assert len(initial_requests) == 1
    initial_request = initial_requests[0]
    assert initial_request.url == 'http://www.detroitmi.gov/Calendar-Events'


def test_meetings_urls():
    filtered_events = list(spider._filter_category(initial_response))
    assert len(filtered_events) == 1
    filtered_event = filtered_events[0]
    assert filtered_event.url == 'http://www.detroitmi.gov/Calendar-and-Events/CategoryID/166'


def test_meeting_count():
    assert len(parsed_items) == 7


def test_name():
    assert parsed_items[0]['name'] == 'Board of Commissioners'


def test_description():
    assert parsed_items[0]['event_description'] == \
           'Board of Police Commissioners Meeting  is meeting Thursday,November 29, 2018 @ 3:00 pm. The meeting is ' \
           'held at Detroit Public Safety Headquarters. 1301 Third St. Detroit, MI 48226.'


def test_start():
    assert parsed_items[0]['start'] == {
        'date': date(2018, 11, 29), 'time': time(15, 00), 'note': ''
    }


def test_end():
    assert parsed_items[0]['end'] == {
        'date': None, 'time': None, 'note': ''
    }


def test_id():
    assert parsed_items[0]['id'] == 'det_police_commissioners_board/201811291500/x/board_of_commissioners'


def test_status():
    assert parsed_items[-1]['status'] == 'passed'


def test_location():
    assert parsed_items[0]['location'] == {
        'neighborhood': '',
        'name': '',
        'address': 'Detroit Public Safety Headquarters. 1301 Third St. Detroit, MI 48226.'
    }


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url': 'http://www.detroitmi.gov/Calendar-and-Events/CategoryID/166',
        'note': ''
    }]


def test_documents():
    assert parsed_items[0]['documents'] == []


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == 'Board'


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'
