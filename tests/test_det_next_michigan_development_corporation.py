from datetime import datetime
from os.path import dirname, join

import pytest
import scrapy
from city_scrapers_core.constants import BOARD, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.det_next_michigan_development_corporation import (
    DetNextMichiganDevelopmentCorporationSpider
)

LOCATION = {
    'name': 'DEGC, Guardian Building',
    'address': '500 Griswold St, Suite 2200, Detroit, MI 48226'
}

TITLE = 'Board of Directors'

test_response = file_response(
    join(dirname(__file__), "files", "det_next_michigan_development_corporation.html"),
    url='http://www.degc.org/public-authorities/d-nmdc/'
)
freezer = freeze_time('2018-07-26')
spider = DetNextMichiganDevelopmentCorporationSpider()
freezer.start()
parsed_items = [item for item in spider._next_meetings(test_response)]
freezer.stop()


def test_initial_request_count():
    items = list(spider.parse(test_response))
    assert len(items) == 3
    urls = {r.url for r in items if isinstance(r, scrapy.Request)}
    assert urls == {
        'http://www.degc.org/public-authorities/d-nmdc/fy-2017-2018-meetings/',
        'http://www.degc.org/public-authorities/d-nmdc/dnmdc-fy-2016-2017-meetings/'
    }


# current meeting http://www.degc.org/public-authorities/ldfa/
def test_title():
    assert parsed_items[0]['title'] == TITLE


def test_description():
    assert parsed_items[0]['description'] == ''


def test_start():
    assert parsed_items[0]['start'] == datetime(2018, 9, 11, 9)


def test_end():
    assert parsed_items[0]['end'] is None


def test_id():
    assert parsed_items[0][
        'id'] == 'det_next_michigan_development_corporation/201809110900/x/board_of_directors'


def test_status():
    assert parsed_items[0]['status'] == TENTATIVE


def test_location():
    assert parsed_items[0]['location'] == LOCATION


def test_sources():
    assert parsed_items[0]['source'] == 'http://www.degc.org/public-authorities/d-nmdc/'


def test_links():
    assert parsed_items[0]['links'] == []


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == BOARD


# # previous meetings e.g. http://www.degc.org/public-authorities/ldfa/fy-2017-2018-meetings/
test_prev_response = file_response(
    join(dirname(__file__), "files", "det_next_michigan_development_corporation_prev.html"),
    url='http://www.degc.org/public-authorities/d-nmdc/dnmdc-fy-2016-2017-meetings'
)
parsed_prev_items = [item for item in spider._parse_prev_meetings(test_prev_response)]
parsed_prev_items = sorted(parsed_prev_items, key=lambda x: x['start'], reverse=True)


def test_request_count():
    items = list(spider._prev_meetings(test_response))
    urls = {r.url for r in items if isinstance(r, scrapy.Request)}
    assert len(urls) == 2
    assert urls == {
        'http://www.degc.org/public-authorities/d-nmdc/fy-2017-2018-meetings/',
        'http://www.degc.org/public-authorities/d-nmdc/dnmdc-fy-2016-2017-meetings/'
    }


def test_prev_meeting_count():
    # 2016-2017 page (2 meetings)
    assert len(parsed_prev_items) == 2


def test_prev_title():
    assert parsed_prev_items[0]['title'] == TITLE


def test_prev_description():
    assert parsed_prev_items[0]['description'] == ''


def test_prev_start():
    assert parsed_prev_items[0]['start'] == datetime(2017, 8, 8, 9)


def test_prev_end():
    assert parsed_prev_items[0]['end'] is None


def test_prev_id():
    assert parsed_prev_items[0][
        'id'] == 'det_next_michigan_development_corporation/201708080900/x/board_of_directors'


def test_prev_status():
    assert parsed_prev_items[0]['status'] == PASSED


def test_prev_location():
    assert parsed_prev_items[0]['location'] == LOCATION


def test_prev_source():
    assert parsed_prev_items[0][
        'source'] == 'http://www.degc.org/public-authorities/d-nmdc/dnmdc-fy-2016-2017-meetings'


def test_prev_links():
    assert parsed_prev_items[0]['links'] == [
        {
            'href':
                'http://www.degc.org/wp-content/uploads/2016-08-09-DNMDC-Special-Board-Meeting-Agenda-4-1.pdf',  # noqa
            'title': 'D-NMDC Agenda',
        },
    ]


@pytest.mark.parametrize('item', parsed_prev_items)
def test_prev_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_prev_items)
def test_prev_classification(item):
    assert item['classification'] == BOARD
