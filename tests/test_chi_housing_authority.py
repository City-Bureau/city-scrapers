from datetime import date, time

import pytest
from freezegun import freeze_time
from tests.utils import file_response

from city_scrapers.constants import BOARD, CANCELED, PASSED
from city_scrapers.spiders.chi_housing_authority import ChiHousingAuthoritySpider

spider = ChiHousingAuthoritySpider()

freezer = freeze_time('2018-12-14')
freezer.start()

UPCOMING_URL = 'http://www.thecha.org/about/board-meetings-agendas-and-resolutions/board-information-and-meetings'  # noqa
NOTICE_URL = 'http://www.thecha.org/about/board-meetings-agendas-and-resolutions/board-meeting-notices'  # noqa
MINUTES_URL = 'http://www.thecha.org/doing-business/contracting-opportunities/view-all/Board%20Meeting'  # noqa

upcoming_items = spider._parse_upcoming(
    file_response('files/chi_housing_authority_upcoming.html', UPCOMING_URL)
)
notice_req = file_response('files/chi_housing_authority_notice.html', NOTICE_URL)
notice_req.meta['upcoming'] = upcoming_items
minutes_req = file_response('files/chi_housing_authority_minutes.html', MINUTES_URL)
minutes_req.meta['upcoming'] = [item for item in spider._parse_notice(notice_req)]

parsed_items = [item for item in spider._parse_combined_meetings(minutes_req)]

freezer.stop()


def test_raises_location_error():
    with pytest.raises(ValueError):
        [i for i in spider.parse(minutes_req)]


def test_start():
    assert parsed_items[0]['start'] == {
        'date': date(2018, 7, 17),
        'time': time(8, 30),
        'note': 'Times may change based on notice',
    }


def test_id():
    assert parsed_items[0]['id'] == 'chi_housing_authority/201807170830/x/board_of_commissioners'


def test_status():
    assert parsed_items[0]['status'] == PASSED
    assert parsed_items[-3]['status'] == CANCELED


def test_sources():
    assert parsed_items[0]['sources'] == [{'url': MINUTES_URL, 'note': ''}]
    assert parsed_items[-2]['sources'] == [{'url': UPCOMING_URL, 'note': ''}]
    assert parsed_items[-1]['sources'] == [{'url': NOTICE_URL, 'note': ''}]


def test_documents():
    assert parsed_items[0]['documents'] == [{
        'url': 'http://www.thecha.org/sites/default/files/July%2017%2C%202018.pdf',
        'note': 'July 17, 2018 Minutes',
    }]
    assert len(parsed_items[-1]['documents']) == 27


@pytest.mark.parametrize('item', parsed_items)
def test_name(item):
    assert item['name'] == 'Board of Commissioners'


@pytest.mark.parametrize('item', parsed_items)
def test_description(item):
    assert item['event_description'] == ''


@pytest.mark.parametrize('item', parsed_items)
def test_end(item):
    assert item['end']['date'] == item['start']['date']
    assert item['end']['time'] == time(13, 0)


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
        'neighborhood': '',
    }


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'
