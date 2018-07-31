from datetime import date, time

import pytest
import scrapy
from freezegun import freeze_time

from city_scrapers.spiders.next_michigan_development_corporation import NextMichiganDevelopmentCorporationSpider
from tests.utils import file_response

LOCATION = {'neighborhood': '', 'name': 'DEGC, Guardian Building', 'address': '500 Griswold, Suite 2200, Detroit'}

NAME = 'Board of Directors'

test_response = file_response('files/next_michigan_development_corporation.html',
                              'http://www.degc.org/public-authorities/d-nmdc/')
freezer = freeze_time('2018-07-26 12:00:01')
spider = NextMichiganDevelopmentCorporationSpider()
freezer.start()
parsed_items = [item for item in spider._next_meeting(test_response) if isinstance(item, dict)]
freezer.stop()


def test_initial_request_count():
    items = list(spider.parse(test_response))
    assert len(items) == 4
    urls = {r.url for r in items if isinstance(r, scrapy.Request)}
    assert urls == {
        'http://www.degc.org/public-authorities/d-nmdc/fy-2017-2018-meetings/',
        'http://www.degc.org/public-authorities/d-nmdc/dnmdc-fy-2016-2017-meetings/'
    }
    items = [i for i in items if isinstance(i, dict)]
    assert len(items) == 2


# current meeting http://www.degc.org/public-authorities/ldfa/
def test_name():
    assert parsed_items[0]['name'] == NAME


def test_description():
    assert parsed_items[0]['event_description'] == ''


def test_start():
    assert parsed_items[0]['start'] == {
        'date': date(2018, 9, 11),
        'time': time(9, 00),
        'note': ''
    }


def test_end():
    assert parsed_items[0]['end'] == {
        'date': None,
        'time': None,
        'note': ''
    }


def test_id():
    assert parsed_items[0]['id'] == 'next_michigan_development_corporation/201809110900/x/board_of_directors'


def test_status():
    assert parsed_items[0]['status'] == 'tentative'


def test_location():
    assert parsed_items[0]['location'] == LOCATION


def test_sources():
    assert parsed_items[0]['sources'] == [
        {'url': 'http://www.degc.org/public-authorities/d-nmdc/', 'note': ''}
    ]


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


# # previous meetings e.g. http://www.degc.org/public-authorities/ldfa/fy-2017-2018-meetings/
test_prev_response = file_response('files/next_michigan_development_corporation_prev.html',
                                   'http://www.degc.org/public-authorities/d-nmdc/dnmdc-fy-2016-2017-meetings')
parsed_prev_items = [item for item in spider._parse_prev_meetings(test_prev_response) if isinstance(item, dict)]
parsed_prev_items = sorted(parsed_prev_items, key=lambda x: x['start']['date'], reverse=True)


def test_request_count():
    items = list(spider._next_page_prev_meetings(test_response))
    urls = {r.url for r in items if isinstance(r, scrapy.Request)}
    assert len(urls) == 2
    assert urls == {
        'http://www.degc.org/public-authorities/d-nmdc/fy-2017-2018-meetings/',
        'http://www.degc.org/public-authorities/d-nmdc/dnmdc-fy-2016-2017-meetings/'
    }


def test_prev_meeting_count():
    # 2016-2017 page (2 meetings)
    assert len(parsed_prev_items) == 2


def test_prev_name():
    assert parsed_prev_items[0]['name'] == NAME


def test_prev_description():
    assert parsed_prev_items[0]['event_description'] == ''


def test_prev_start():
    assert parsed_prev_items[0]['start'] == {
        'date': date(2017, 8, 8), 'time': None, 'note': ''
    }


def test_prev_end():
    assert parsed_prev_items[0]['end'] == {
        'date': None, 'time': None, 'note': ''
    }


def test_prev_id():
    assert parsed_prev_items[0]['id'] \
           == 'next_michigan_development_corporation/201708080000/x/board_of_directors'


def test_prev_status():
    assert parsed_prev_items[0]['status'] == 'passed'


def test_prev_location():
    assert parsed_prev_items[0]['location'] == LOCATION


def test_prev_sources():
    assert parsed_prev_items[0]['sources'] == [
        {'url': 'http://www.degc.org/public-authorities/d-nmdc/dnmdc-fy-2016-2017-meetings', 'note': ''}
    ]


def test_prev_documents():
    assert parsed_prev_items[0]['documents'] == [
        {
            'url': 'http://www.degc.org/wp-content/uploads/2016-08-09-DNMDC-Special-Board-Meeting-Agenda-4-1.pdf',
            'note': 'agenda',
        },
    ]


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] is 'Board'


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'
