import pytest
import scrapy

from datetime import datetime
from tests.utils import file_response

from city_scrapers.constants import BOARD, COMMITTEE
from city_scrapers.spiders.chi_buildings import ChiBuildingsSpider

test_json_response = file_response('files/chi_buildings.json')
test_event_response = file_response('files/chi_buildings.html')
spider = ChiBuildingsSpider()
# Setting spider date to time test files were generated
spider.calendar_date = datetime(2018, 2, 18)


class MockRequest(object):
    meta = {}

    def __getitem__(self, key):
        return self.meta['item'].get(key)


def mock_request(*args, **kwargs):
    mock = MockRequest()
    mock.meta = {'item': {}}
    return mock


@pytest.fixture()
def parsed_items(monkeypatch):
    monkeypatch.setattr(scrapy, 'Request', mock_request)
    parsed_items = [item for item in spider.parse(test_json_response)]
    return parsed_items


@pytest.fixture()
def parsed_event():
    return spider._parse_event(test_event_response)


def test_name(parsed_items):
    assert parsed_items[0]['name'] == 'Administrative Operations Committee Meeting – January 4, 2018'


def test_classification(parsed_items):
    assert parsed_items[0]['classification'] == COMMITTEE
    assert parsed_items[1]['classification'] == BOARD
    assert parsed_items[2]['classification'] == COMMITTEE
    assert parsed_items[3]['classification'] == COMMITTEE


def test_start(parsed_items):
    assert parsed_items[0]['start']['date'].isoformat() == '2018-01-04'


def test_end_time(parsed_items):
    assert parsed_items[0]['end']['date'].isoformat() == '2018-01-04'


def test_id(parsed_items):
    assert parsed_items[0][
               'id'] == 'chi_buildings/000000000000/x/administrative_operations_committee_meeting_january_4_2018'

def test_event_description(parsed_items):
    assert parsed_items[0]['description'] == ('January 4, 2018  1:00 pm - 2:00 pm</br></br>Agenda\xa0')


def test_status(parsed_items):
    assert parsed_items[0]['status'] == 'passed'
    assert parsed_items[10]['status'] == 'tentative'


def test_board_meeting_location(parsed_items):
    assert parsed_items[0]['location'] == {
        'url': 'https://thedaleycenter.com',
        'name': 'Second Floor Board Room, Richard J. Daley Center',
        'address': '50 W. Washington Street Chicago, IL 60602',
        'coordinates': {
            'latitude': '41.884089',
            'longitude': '-87.630191',
        },
    }


def test_source(parsed_items):
    assert parsed_items[0]['sources'][0]['url'] == (
        'http://www.pbcchicago.com/events/event/administrative-operations-committee-meeting-january-4-2018/'
    )


def test_event_location(parsed_event):
    assert parsed_event['location'] == {
        'url': None,
        'name': 'McKinley Park Auditorium',
        'address': '2210 West Pershing Road, Chicago, IL, 60609, USA',
        'coordinates': {
            'latitude': '41.823738',
            'longitude': '-87.682445',
        },
    }


def test__type(parsed_items):
    assert {item['_type'] for item in parsed_items} == {'event'}


def test_no_holidays_included(parsed_items):
    assert 'Holiday' not in {item['classification'] for item in parsed_items}


def test_all_day(parsed_items):
    assert {item['all_day'] for item in parsed_items} == {False}
