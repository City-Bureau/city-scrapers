from datetime import datetime
from os.path import dirname, join

import pytest
import scrapy
from city_scrapers_core.constants import BOARD, CANCELLED, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.det_brownfield_redevelopment_authority import (
    DetBrownfieldRedevelopmentAuthoritySpider
)

test_response = file_response(
    join(dirname(__file__), "files", "det_brownfield_redevelopment_authority.html"),
    url='http://www.degc.org/public-authorities/dbra/'
)
spider = DetBrownfieldRedevelopmentAuthoritySpider()


def test_initial_request_count():
    items = list(spider.parse(test_response))
    assert len(items) == 3
    urls = {r.url for r in items if isinstance(r, scrapy.Request)}
    assert urls == {
        'http://www.degc.org/public-authorities/dbra/fy-2018-2019-notices-agendas-and-minutes/',
        'http://www.degc.org/public-authorities/dbra/fy-2017-2018-meetings/',
        'http://www.degc.org/public-authorities/dbra/dbra-fy-2016-2017-meetings/'
    }


test_meetings = file_response(
    join(dirname(__file__), "files", "det_brownfield_redevelopment_authority_meetings.html"),
    url='http://www.degc.org/public-authorities/dbra/fy-2017-2018-meetings/'
)
freezer = freeze_time('2018-07-28')
spider = DetBrownfieldRedevelopmentAuthoritySpider()
freezer.start()

parsed_items = [item for item in spider._parse_meetings(test_meetings)]
parsed_items = sorted(parsed_items, key=lambda x: x['id'], reverse=True)
freezer.stop()


def test_meeting_count():
    ids = {item['id'] for item in parsed_items}
    assert len(parsed_items) == 51
    assert len(ids) == 51


def test_title():
    assert parsed_items[0]['title'] == 'Board of Directors'
    assert parsed_items[1]['title'] == 'Harmonie Social Club City Council Public Hearing'


def test_description():
    assert parsed_items[0]['description'] == ''


def test_start():
    assert parsed_items[0]['start'] == datetime(2019, 12, 19, 16)
    assert parsed_items[1]['start'] == datetime(2019, 4, 11)


def test_end():
    assert parsed_items[0]['end'] is None


def test_id():
    assert parsed_items[0][
        'id'
    ] == 'det_brownfield_redevelopment_authority/201912191600/x/board_of_directors'


def test_status():
    assert parsed_items[0]['status'] == CANCELLED
    assert parsed_items[-1]['status'] == PASSED


def test_location():
    assert parsed_items[0]['location'] == spider.location


def test_source():
    assert parsed_items[0]['source'
                           ] == 'http://www.degc.org/public-authorities/dbra/fy-2017-2018-meetings/'


def test_links():
    assert parsed_items[0]['links'] == [{
        'href': 'http://www.degc.org/wp-content/uploads/DBRA-121918-Meeting-Cancellation.pdf',
        'title': 'DBRA Regular Meeting Cancellation Notice',
    }]


def test_classification():
    assert parsed_items[0]['classification'] == BOARD
    assert parsed_items[-1]['classification'] == BOARD


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False
