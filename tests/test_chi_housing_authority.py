from datetime import datetime, time

import pytest
from city_scrapers_core.constants import BOARD, CANCELLED, PASSED
from freezegun import freeze_time
from tests.utils import file_response

from city_scrapers.spiders.chi_housing_authority import ChiHousingAuthoritySpider

spider = ChiHousingAuthoritySpider()

freezer = freeze_time('2018-12-14')
freezer.start()

UPCOMING_URL = 'http://www.thecha.org/about/board-meetings-agendas-and-resolutions/board-information-and-meetings'  # noqa
NOTICE_URL = 'http://www.thecha.org/about/board-meetings-agendas-and-resolutions/board-meeting-notices'  # noqa
MINUTES_URL = 'http://www.thecha.org/doing-business/contracting-opportunities/view-all/Board%20Meeting'  # noqa

spider.upcoming_meetings = spider._parse_upcoming(
    file_response('files/chi_housing_authority_upcoming.html', UPCOMING_URL)
)
spider.upcoming_meetings = spider._parse_notice(
    file_response('files/chi_housing_authority_notice.html', NOTICE_URL)
)
minutes_req = file_response('files/chi_housing_authority_minutes.html', MINUTES_URL)

parsed_items = [item for item in spider._parse_combined_meetings(minutes_req)]

freezer.stop()


def test_raises_location_error():
    with pytest.raises(ValueError):
        [i for i in spider.parse(minutes_req)]


def test_start():
    assert parsed_items[0]['start'] == datetime(2018, 7, 17, 8, 30)


def test_time_notes():
    assert parsed_items[0]['time_notes'] == 'Times may change based on notice'


def test_id():
    assert parsed_items[0]['id'] == 'chi_housing_authority/201807170830/x/board_of_commissioners'


def test_status():
    assert parsed_items[0]['status'] == PASSED
    assert parsed_items[-3]['status'] == CANCELLED


def test_source():
    assert parsed_items[0]['source'] == MINUTES_URL
    assert parsed_items[-2]['source'] == UPCOMING_URL
    assert parsed_items[-1]['source'] == NOTICE_URL


def test_links():
    assert parsed_items[0]['links'] == [{
        'href': 'http://www.thecha.org/sites/default/files/July%2017%2C%202018.pdf',
        'title': 'July 17, 2018 Minutes',
    }]
    assert len(parsed_items[-1]['links']) == 27


@pytest.mark.parametrize('item', parsed_items)
def test_title(item):
    assert item['title'] == 'Board of Commissioners'


@pytest.mark.parametrize('item', parsed_items)
def test_description(item):
    assert item['description'] == ''


@pytest.mark.parametrize('item', parsed_items)
def test_end(item):
    assert item['end'].time() == time(13, 0)


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == BOARD


@pytest.mark.parametrize('item', parsed_items)
def test_location(item):
    assert item['location'] == {
        'address': '4859 S Wabash Chicago, IL 60615',
        'name': 'Charles A. Hayes FIC',
    }
