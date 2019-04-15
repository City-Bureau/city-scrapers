from datetime import datetime

import pytest
import scrapy
from city_scrapers_core.constants import BOARD, PASSED
from freezegun import freeze_time
from tests.utils import file_response

from city_scrapers.spiders.det_neighborhood_development_corporation import (
    DetNeighborhoodDevelopmentCorporationSpider
)

LOCATION = {
    'name': 'DEGC, Guardian Building',
    'address': '500 Griswold St, Suite 2200, Detroit, MI 48226',
}

TITLE = 'Board of Directors'

test_response = file_response(
    'files/det_neighborhood_development_corporation.html',
    url='http://www.degc.org/public-authorities/ndc/'
)
freezer = freeze_time('2018-07-29')
spider = DetNeighborhoodDevelopmentCorporationSpider()
freezer.start()
parsed_items = [item for item in spider._next_meeting(test_response)]
freezer.stop()


def test_initial_request_count():
    items = list(spider.parse(test_response))
    assert len(items) == 5
    urls = {r.url for r in items if isinstance(r, scrapy.Request)}
    assert urls == {
        'http://www.degc.org/public-authorities/ndc/fy-2015-2016-meetings/',
        'http://www.degc.org/public-authorities/ndc/fy-2017-2018-meetings/'
    }
    items = [i for i in items if not isinstance(i, scrapy.Request)]
    # current meeting plus two prev meetings on first page
    assert len(items) == 3


# current meeting http://www.degc.org/public-authorities/ndc/
def test_title():
    assert parsed_items[0]['title'] == TITLE


def test_description():
    assert parsed_items[0]['description'] == ''


def test_start():
    assert parsed_items[0]['start'] == datetime(2018, 7, 24, 8, 45)


def test_end():
    assert parsed_items[0]['end'] is None


def test_id():
    assert parsed_items[0][
        'id'] == 'det_neighborhood_development_corporation/201807240845/x/board_of_directors'


def test_status():
    assert parsed_items[0]['status'] == PASSED


def test_location():
    assert parsed_items[0]['location'] == LOCATION


def test_source():
    assert parsed_items[0]['source'] == 'http://www.degc.org/public-authorities/ndc/'


def test_links():
    assert parsed_items[0]['links'] == []


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == BOARD


# previous meetings e.g. http://www.degc.org/public-authorities/ndc/fy-2015-2016-meetings/
test_prev_response = file_response(
    'files/det_neighborhood_development_corporation_prev.html',
    url='http://www.degc.org/public-authorities/ndc/fy-2015-2016-meetings/'
)
parsed_prev_items = [item for item in spider._parse_prev_meetings(test_prev_response)]
parsed_prev_items = sorted(parsed_prev_items, key=lambda x: x['start'], reverse=True)


def test_request_count():
    items = list(spider._next_page_prev_meetings(test_response))
    urls = {r.url for r in items if isinstance(r, scrapy.Request)}
    assert len(urls) == 2
    assert urls == {
        'http://www.degc.org/public-authorities/ndc/fy-2015-2016-meetings/',
        'http://www.degc.org/public-authorities/ndc/fy-2017-2018-meetings/'
    }


def test_prev_meeting_count():
    assert len(parsed_prev_items) == 1


def test_prev_title():
    assert parsed_prev_items[0]['title'] == TITLE


def test_prev_description():
    assert parsed_prev_items[0]['description'] == ''


def test_prev_start():
    assert parsed_prev_items[0]['start'] == datetime(2016, 6, 27)


def test_prev_end():
    assert parsed_prev_items[0]['end'] is None


def test_prev_id():
    assert parsed_prev_items[0][
        'id'] == 'det_neighborhood_development_corporation/201606270000/x/board_of_directors'


def test_prev_status():
    assert parsed_prev_items[0]['status'] == PASSED


def test_prev_location():
    assert parsed_prev_items[0]['location'] == LOCATION


def test_prev_sources():
    assert parsed_prev_items[0][
        'source'] == 'http://www.degc.org/public-authorities/ndc/fy-2015-2016-meetings/'


def test_prev_links():
    assert parsed_prev_items[
        0
    ]['links'
      ] == [
          {
              'href':
                  'http://www.degc.org/wp-content/uploads/2017-06-27-NDC-Board-Meeting-Agenda.pdf',  # noqa
              'title': 'Agenda',
          },
      ]


@pytest.mark.parametrize('item', parsed_prev_items)
def test_prev_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_prev_items)
def test_prev_classification(item):
    assert item['classification'] == BOARD
