import pytest
from datetime import datetime

from tests.utils import file_response
from documenters_aggregator.spiders.chi_buildings import Chi_buildingsSpider


test_response = file_response('files/chi_buildings.html')
spider = Chi_buildingsSpider()
# Setting spider date to time test files were generated
spider.calendar_date = datetime(2017, 10, 15)
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[0]['name'] == 'Daley Plaza - Italian Exhibit'


def test_afb_name():
    assert parsed_items[3]['name'] == 'Advertisement for Bids - Ebinger Elementary School Annex'


def test_description():
    assert parsed_items[0]['description'] is None


def test_afb_description():
    assert parsed_items[3]['description'] == 'Details on advertisement for bids at: http://www.pbcchicago.com/content/working/opening_display.asp?BID_ID=503'


def test_start_time():
    assert parsed_items[0]['start_time'] == '2017-10-16T00:00:00-05:00'


def test_start_time_with_hours():
    assert parsed_items[3]['start_time'] == '2017-10-18T10:00:00-05:00'


@pytest.mark.parametrize('item', parsed_items)
def test_end_time(item):
    assert item['end_time'] is None


def test_id():
    assert parsed_items[0]['id'] == 'PBCC2176'


def test_all_day():
    assert parsed_items[0]['all_day'] is True


def test_non_all_day():
    assert parsed_items[3]['all_day'] is False


def test_classification():
    assert parsed_items[0]['classification'] == 'Daley Plaza'


def test_afb_classification():
    assert parsed_items[3]['classification'] == 'Advertisement for Bids'


@pytest.mark.parametrize('item', parsed_items)
def test_status(item):
    assert item['status'] == 'tentative'


def test_location():
    assert parsed_items[0]['location'] == {
        'url': None,
        'name': None,
        'coordinates': {
            'latitude': None,
            'longitude': None,
        },
    }


def test_board_meeting_location():
    assert parsed_items[9]['location'] == {
        'url': 'https://thedaleycenter.com',
        'name': 'Second Floor Board Room, Richard J. Daley Center, 50 W. Washington Street',
        'coordinates': {
            'latitude': '41.884089',
            'longitude': '-87.630191',
        },
    }


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert parsed_items[0]['_type'] == 'event'


def test_source():
    assert parsed_items[0]['sources'][0]['url'] == 'http://www.pbcchicago.com/content/about/calendar_detail.asp?eID=2176'
