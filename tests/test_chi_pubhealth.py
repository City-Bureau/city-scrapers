import pytest

from tests.utils import file_response
from documenters_aggregator.spiders.chi_pubhealth import Chi_pubhealthSpider

test_response = file_response('files/chi_pubhealth.html', url='https://www.cityofchicago.org/city/en/depts/cdph/supp_info/boh/2017-board-of-health.html')
spider = Chi_pubhealthSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[0]['name'] == 'Board of Health Meeting'


def test_description():
    assert parsed_items[0]['description'] == 'The Chicago Board of Health is scheduled to meet on the third Wednesday of each month from 9:00am-10:30am. The meetings are held at the Chicago Department of Public Health, DePaul Center, 333 S. State Street, 2nd Floor Board Room.'


def test_start_time():
    assert parsed_items[0]['start_time'] == '2017-01-18T09:00:00-06:00'


def test_end_time():
    assert parsed_items[0]['end_time'] == '2017-01-18T10:30:00-06:00'


def test_id():
    assert parsed_items[0]['id'] == 'chi_pubhealth/201701180900/x/board_of_health_meeting'


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == 'committee-meeting'


@pytest.mark.parametrize('item', parsed_items)
def test_status(item):
    assert item['status'] == 'tentative'


@pytest.mark.parametrize('item', parsed_items)
def test_location(item):
    assert item['location'] == {
        'url': 'https://www.cityofchicago.org/city/en/depts/cdph.html',
        'name': '2nd Floor Board Room, DePaul Center, 333 S. State Street, Chicago, IL',
        'coordinates': {
            'latitude': None,
            'longitude': None,
        }
    }


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'


@pytest.mark.parametrize('item', parsed_items)
def test_sources(item):
    assert item['sources'] == [{'url': 'https://www.cityofchicago.org/city/en/depts/cdph/supp_info/boh/2017-board-of-health.html', 'note': ''}]


@pytest.mark.parametrize('item', parsed_items)
def test_timezone(item):
    assert item['timezone'] == 'America/Chicago'
