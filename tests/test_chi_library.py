import pytest
import betamax
import requests

from tests.utils import file_response
from city_scrapers.spiders.chi_library import ChiLibrarySpider

# Use betamax to record requests
session = requests.Session()
recorder = betamax.Betamax(session)
with recorder.use_cassette('test_chi_library_libinfo'):
    test_response = file_response('files/chi_library.html', url='https://www.chipublib.org/board-of-directors/board-meeting-schedule/')
    spider = ChiLibrarySpider(session=session)
    parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[0]['name'] == 'Chicago Public Library Board Meeting'


def test_description():
    assert parsed_items[0]['description'] == 'There are no meetings in February, July and August. Entry into these meetings is permitted at 8:45 a.m.'


def test_start_time():
    assert parsed_items[0]['start_time'].isoformat() == '2017-01-17T09:00:00-06:00'


def test_end_time():
    assert parsed_items[0]['end_time'] is None


# def test_id():
#    assert parsed_items[0]['id'] == 'chi_library/201701170900/x/chicago_public_library_board_meeting'


def test_all_day():
    assert parsed_items[0]['all_day'] is False


def test_location():
    assert parsed_items[0]['location'] == {
    'address': '400 S. State Street, CHICAGO IL 60605',
    'coordinates': {'latitude': None, 'longitude': None},
    'name': 'Harold Washington Library Center, Multi-Purpose Room, Lower Level',
    'url': None}


##### Parameterized Tests #####


@pytest.mark.parametrize('item', parsed_items)
def test_type(item):
    assert item['_type'] == 'event'

@pytest.mark.parametrize('item', parsed_items)
def test_name_param(item):
    assert item['name'] == 'Chicago Public Library Board Meeting'

@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == 'Board meeting'

@pytest.mark.parametrize('item', parsed_items)
def test_end(item):
    assert item['end_time'] is None

@pytest.mark.parametrize('item', parsed_items)
def test_all_day_param(item):
    assert item['all_day'] is False

@pytest.mark.parametrize('item', parsed_items)
def test_timezone(item):
    assert item['timezone'] == 'America/Chicago'

@pytest.mark.parametrize('item', parsed_items)
def test_status(item):
    assert item['status'] == 'tentative'

@pytest.mark.parametrize('item', parsed_items)
def test_sources(item):
    assert item['sources'] == [{'url': 'https://www.chipublib.org/board-of-directors/board-meeting-schedule/', 'note': ''}]
