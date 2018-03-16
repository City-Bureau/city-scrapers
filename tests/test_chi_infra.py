import pytest
from tests.utils import file_response
from documenters_aggregator.spiders.chi_infra import Chi_infraSpider

test_response = file_response('files/chi_infra.html', url='http://chicagoinfrastructure.org/public-records/scheduled-meetings')
spider = Chi_infraSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[0]['name'] == 'Board Meeting'


def test_description():
    assert parsed_items[0]['description'] is None


def test_start_time():
    assert parsed_items[0]['start_time'].isoformat() == '2017-10-11T00:00:00-05:00'


def test_end_time():
    assert parsed_items[0]['end_time'] is None


def test_id():
    assert parsed_items[0]['id'] == 'chi_infra/201710110000/x/board_meeting'


def test_all_day():
    assert parsed_items[0]['all_day'] is False


def test_classification():
    assert parsed_items[0]['classification'] == "Board Meeting"


def test_status():
    assert parsed_items[0]['status'] == 'tentative'


@pytest.mark.parametrize('item', parsed_items)
def test_location(item):
    assert item['location'] == {
        'url': None,
        'name': None,
        'address': None,
        'coordinates': {
            'latitude': None,
            'longitude': None,
        },
    }


def test__type():
    assert parsed_items[0]['_type'] == 'event'


@pytest.mark.parametrize('item', parsed_items)
def test_sources(item):
    assert item['sources'] == [{'url': 'http://chicagoinfrastructure.org/public-records/scheduled-meetings', 'note': ''}]


@pytest.mark.parametrize('item', parsed_items)
def test_timezone(item):
    assert item['timezone'] == 'America/Chicago'
