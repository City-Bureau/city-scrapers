from datetime import date, time

import pytest
import scrapy
from freezegun import freeze_time

from tests.utils import file_response
from city_scrapers.constants import BOARD, CONFIRMED, PASSED
from city_scrapers.spiders.det_downtown_development_authority import (
    DetDowntownDevelopmentAuthoritySpider
)

# Shared properties between two different page / meeting types

LOCATION = {
    'neighborhood': '',
    'name': 'DEGC, Guardian Building',
    'address': '500 Griswold, Suite 2200, Detroit',
}

NAME = 'Board of Directors'

test_response = file_response('files/det_downtown_development_authority.html',
                              'http://www.degc.org/public-authorities/dda/')
freezer = freeze_time('2018-07-25 12:00:01')
spider = DetDowntownDevelopmentAuthoritySpider()
freezer.start()
parsed_items = [
    item for item in spider._next_meeting(test_response)
    if isinstance(item, dict)
]
freezer.stop()


def test_initial_request_count():
    items = list(spider.parse(test_response))
    assert len(items) == 3
    urls = {r.url for r in items if isinstance(r, scrapy.Request)}
    assert urls == {
        'http://www.degc.org/public-authorities/dda/fy-2017-2018-meetings/',
        'http://www.degc.org/public-authorities/dda/dda-fy-2016-2017-meetings/'
    }
    items = [i for i in items if isinstance(i, dict)]
    assert len(items) == 1


# current meeting (e.g. http://www.degc.org/public-authorities/dda/)
def test_name():
    assert parsed_items[0]['name'] == NAME


def test_description():
    assert parsed_items[0]['event_description'] == ''


def test_start():
    assert parsed_items[0]['start'] == {
        'date': date(2018, 7, 25),
        'time': time(15, 00),
        'note': ''
    }


def test_end():
    assert parsed_items[0]['end'] == {
        'date': None,
        'time': None,
        'note': ''
    }


def test_id():
    assert parsed_items[0]['id'] == (
        'det_downtown_development_authority/'
        '201807251500/x/board_of_directors'
    )


def test_status():
    assert parsed_items[0]['status'] == CONFIRMED


def test_location():
    assert parsed_items[0]['location'] == LOCATION


def test_sources():
    assert parsed_items[0]['sources'] == [
        {'url': 'http://www.degc.org/public-authorities/dda/', 'note': ''}
    ]


def test_documents():
    assert parsed_items[0]['documents'] == [{
        'url': (
            'http://www.degc.org/wp-content/uploads'
            '/07-25-18-DDA-Board-Meeting-Agenda-Only.pdf'
        ),
        'note': 'Agenda'
    }]


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == BOARD


@pytest.mark.parametrize('item', parsed_items)
def test_type(item):
    assert item['_type'] == 'event'


# previous meetings e.g.
# http://www.degc.org/public-authorities/dda/dda-fy-2016-2017-meetings/
test_prev_response = file_response(
    'files/det_downtown_development_authority_prev.html',
    'http://www.degc.org/public-authorities/dda/dda-fy-2016-2017-meetings/'
)
parsed_prev_items = [
    item for item in spider._parse_prev_meetings(test_prev_response)
    if isinstance(item, dict)
]
parsed_prev_items = sorted(
    parsed_prev_items, key=lambda x: x['start']['date'], reverse=True
)


def test_request_count():
    requests = list(spider._prev_meetings(test_response))
    urls = {r.url for r in requests}
    assert len(requests) == 2
    assert urls == {
        'http://www.degc.org/public-authorities/dda/fy-2017-2018-meetings/',
        'http://www.degc.org/public-authorities/dda/dda-fy-2016-2017-meetings/'
    }


def test_prev_meeting_count():
    # 2016-2017 page (15 meetings)
    assert len(parsed_prev_items) == 15


def test_prev_name():
    assert parsed_prev_items[0]['name'] == NAME


def test_prev_description():
    assert parsed_prev_items[0]['event_description'] == ''


def test_prev_start():
    assert parsed_prev_items[0]['start'] == {
        'date': date(2017, 6, 28), 'time': None, 'note': ''
    }


def test_prev_end():
    assert parsed_prev_items[0]['end'] == {
        'date': None, 'time': None, 'note': ''
    }


def test_prev_id():
    assert parsed_prev_items[0]['id'] == (
        'det_downtown_development_authority/201706280000/'
        'x/board_of_directors'
    )


def test_prev_status():
    assert parsed_prev_items[0]['status'] == PASSED


def test_prev_location():
    assert parsed_prev_items[0]['location'] == LOCATION


def test_prev_sources():
    assert parsed_prev_items[0]['sources'] == [
        {
            'url': (
                'http://www.degc.org/public-authorities/'
                'dda/dda-fy-2016-2017-meetings/'
            ),
            'note': ''
        }
    ]


def test_prev_documents():
    assert parsed_prev_items[0]['documents'] == [
        {
            'url': (
                'http://www.degc.org/wp-content/uploads'
                '/2017-06-28-dda-special-board-meeting-materials.pdf'
            ),
            'note': 'Meeting Materials',
        },
        {
            'url': (
                'http://www.degc.org/wp-content/uploads'
                '/2017-06-28-Attachment-D.pdf'
            ),
            'note': 'Attachment D',
        },
        {
            'url': (
                'http://www.degc.org/wp-content/uploads'
                '/2017-06-28-Attachment-K.pdf'
            ),
            'note': 'Attachment k',
        },
        {
            'url': (
                'http://www.degc.org/wp-content/uploads'
                '/2017-06-28-DDA-Board-Meeting-Minutes.pdf'
            ),
            'note': 'Minutes',
        },
    ]


@pytest.mark.parametrize('item', parsed_prev_items)
def test_prev_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_prev_items)
def test_prev_classification(item):
    assert item['classification'] is BOARD


@pytest.mark.parametrize('item', parsed_prev_items)
def test_prev_type(item):
    assert item['_type'] == 'event'
