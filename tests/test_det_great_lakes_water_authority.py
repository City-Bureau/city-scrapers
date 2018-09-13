from datetime import date, time

import pytest

from city_scrapers.constants import CANCELED
from city_scrapers.spiders.det_great_lakes_water_authority import DetGreatLakesWaterAuthoritySpider
from tests.utils import file_response
import scrapy

test_response = file_response('files/det_great_lakes_water_authority.html', 'http://www.glwater.org/events/')
spider = DetGreatLakesWaterAuthoritySpider()
requests = [request for request in spider.parse(test_response)]
test_ics_response = file_response(
    'files/det_great_lakes_water_authority.ics',
    'http://www.glwater.org/events/?ical=1&tribe_display=month'
)
parsed_items = [item for item in spider._parse_ical(test_ics_response)]
parsed_items = sorted(parsed_items, key=lambda x: (x['start']['date'], x['start']['time']))


def test_requests():
    requests = [request for request in spider.parse(test_response)]
    urls = {r.url for r in requests}
    # spider should yield ical for month + request for next month calendar
    assert len(requests) == 2
    assert urls == {
        'http://www.glwater.org/events/?ical=1&tribe_display=month',
        'http://www.glwater.org/events/2018-08/',
    }


def test_event_count():
    assert len(parsed_items) == 7


def test_name():
    assert parsed_items[0]['name'] == 'Legal Committee Meeting'


def test_description():
    assert parsed_items[0]['event_description'] == ''


def test_start():
    assert parsed_items[0]['start'] == {
        'date': date(2018, 6, 27),
        'time': time(13, 00),
        'note': ''
    }


def test_end():
    assert parsed_items[0]['end'] == {
        'date': date(2018, 6, 27),
        'time': time(14, 00),
        'note': ''
    }


def test_id():
    assert parsed_items[0]['id'] == 'det_great_lakes_water_authority/201806271300/x/legal_committee_meeting'


def test_status():
    assert parsed_items[0]['status'] == CANCELED


def test_location():
    assert parsed_items[0]['location'] == {
        'neighborhood': '',
        'name': '',
        'address': '735 Randolph, 5th Floor Board Room, Detroit,, MI, 48226'
    }


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url': 'http://www.glwater.org/event/legal-committee-meeting-7/',
        'note': ''
    }]


def test_classification():
    assert parsed_items[0]['classification'] == 'Committee'


def test_documents():
    assert parsed_items[0]['documents'] == []


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert parsed_items[0]['_type'] == 'event'
