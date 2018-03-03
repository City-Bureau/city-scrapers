import pytest

from freezegun import freeze_time
from tests.utils import file_response
from documenters_aggregator.spiders.chi_transit import ChiTransitSpider

freezer = freeze_time('2017-11-10 12:00:01')
freezer.start()

test_response = file_response('files/chi_transit.html')
spider = ChiTransitSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]

freezer.stop()


def test_name():
    assert parsed_items[0]['name'] == 'Committee on Strategic Planning & Service Delivery'
    assert parsed_items[1]['name'] == 'Committee on Finance, Audit & Budget'
    assert parsed_items[2]['name'] == 'Regular Board Meeting of Chicago Transit Board'


def test_description():
    assert parsed_items[0]['description'] == 'Transit Board Committee Meetings -  Meeting Notice: http://www.transitchicago.com/assets\\1\\agendas_minutes\\Nov2017_-_Notice_-_Strategic_Planning_Cmte.pdf'
    assert parsed_items[1]['description'] == 'Transit Board Committee Meetings -  Meeting Notice: http://www.transitchicago.com/assets\\1\\agendas_minutes\\Nov2017_-_Notice_-_FAB.pdf'
    assert parsed_items[2]['description'] == 'Transit Board Meetings -  Meeting Notice: http://www.transitchicago.com/assets\\1\\agendas_minutes\\Nov2017_-_Notice_-_Regular_Brd.pdf'


def test_start_time():
    assert parsed_items[0]['start_time'].isoformat() == '2017-11-15T14:00:00-06:00'


def test_start_time_after_mtg():
    assert parsed_items[1]['start_time'].isoformat() == '2017-11-15T14:00:00-06:00'


def test_classification():
    assert parsed_items[0]['classification'] == 'Transit Board Committee Meetings'
    assert parsed_items[2]['classification'] == 'Transit Board Meetings'


def test_id():
    assert parsed_items[0]['id'] == 'chi_transit/201711151400/x/committee_on_strategic_planning_service_delivery'
    assert parsed_items[2]['id'] == 'chi_transit/201711151430/x/regular_board_meeting_of_chicago_transit_board'


@pytest.mark.parametrize('item', parsed_items)
def test_end_time(item):
    assert item['end_time'] is None


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_status(item):
    assert item['status'] == 'tentative'


@pytest.mark.parametrize('item', parsed_items)
def test_location(item):
    assert item['location'] == {
        'url': 'http://www.transitchicago.com',
        'name': 'Chicago Transit Authority 2nd Floor Boardroom',
        'address': '567 West Lake Street Chicago, IL',
        'coordinates': {
            'latitude': 41.88528,
            'longitude': -87.64235,
        },
    }


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert parsed_items[0]['_type'] == 'event'


@pytest.mark.parametrize('item', parsed_items)
def test_timezone(item):
    assert item['timezone'] == 'America/Chicago'
