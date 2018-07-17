import pytest
import scrapy

from datetime import datetime
from tests.utils import file_response
from city_scrapers.spiders.chi_buildings import Chi_buildingsSpider


test_json_response = file_response('files/chi_buildings.json')
test_event_response = file_response('files/chi_buildings.html')
spider = Chi_buildingsSpider()
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


setattr(scrapy, 'Request', mock_request)
parsed_items = [item for item in spider.parse(test_json_response)]
parsed_event = spider._parse_event(test_event_response)


def test_name():
    assert parsed_items[0]['name'] == 'Administrative Operations Committee Meeting – January 4, 2018'


def test_classification():
    assert parsed_items[0]['classification'] == 'Admin Opp Committee Meeting'
    assert parsed_items[1]['classification'] == 'Board Meeting'
    assert parsed_items[2]['classification'] == 'Admin Opp Committee Meeting'
    assert parsed_items[3]['classification'] == 'Audit Committee'


def test_start():
    assert parsed_items[0]['start']['date'].isoformat() == '2018-01-04'


def test_end_time():
    assert parsed_items[0]['end']['date'].isoformat() == '2018-01-04'


def test_id():
    assert parsed_items[0]['id'] == 'chi_buildings/000000000000/x/administrative_operations_committee_meeting_january_4_2018'

def test_event_description():
    assert parsed_items[0]['description'] == ('January 4, 2018  1:00 pm - 2:00 pm</br></br>Agenda\xa0')


def test_status():
    assert parsed_items[0]['status'] == 'passed'
    assert parsed_items[10]['status'] == 'tentative'


def test_board_meeting_location():
    assert parsed_items[0]['location'] == {
        'url': 'https://thedaleycenter.com',
        'name': 'Second Floor Board Room, Richard J. Daley Center',
        'address': '50 W. Washington Street Chicago, IL 60602',
        'coordinates': {
            'latitude': '41.884089',
            'longitude': '-87.630191',
        },
    }

def test_source():
    assert parsed_items[0]['sources'][0]['url'] == (
        'http://www.pbcchicago.com/events/event/administrative-operations-committee-meeting-january-4-2018/'
    )

def test_event_location():
    assert parsed_event['location'] == {
        'url': None,
        'name': 'McKinley Park Auditorium',
        'address': '2210 West Pershing Road, Chicago, IL, 60609, USA',
        'coordinates': {
            'latitude': '41.823738',
            'longitude': '-87.682445',
        },
    }


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert parsed_items[0]['_type'] == 'event'

@pytest.mark.parametrize('item', parsed_items)
def test_no_holidays_included(item):
    assert item['classification'] != 'Holiday'


@pytest.mark.parametrize('item', parsed_items)
def test_timezone(item):
    assert item['timezone'] == 'America/Chicago'

@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False
