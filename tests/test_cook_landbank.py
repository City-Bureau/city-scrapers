import pytest
from tests.utils import file_response
from documenters_aggregator.spiders.cook_landbank import Cook_landbankSpider

file = file_response('files/cook_landbank.json')
spider = Cook_landbankSpider()

test_response = file
parsed_items = list(spider.parse(test_response))


def test_name():
    assert parsed_items[0]['name'] == 'CCLBA Finance Committee Meeting'


def test_description():
    assert parsed_items[0]['description'] is None


def test_start_time():
    assert parsed_items[0]['start_time'].isoformat() == '2017-09-13T10:00:00-05:00'


def test_end_time():
    assert parsed_items[0]['end_time'] is None


@pytest.mark.parametrize('item', parsed_items)
def test_timezone(item):
    assert item['timezone'] == 'America/Chicago'


def test_id():
    assert parsed_items[0]['id'] == 'cook_landbank/201709131000/3381/cclba_finance_committee_meeting'


def test_all_day():
    assert parsed_items[0]['all_day'] is False


def test_classification():
    assert parsed_items[0]['classification'] == 'Not classified'


def test_status():
    assert parsed_items[0]['status'] == 'passed'


def test_location():
    assert parsed_items[0]['location'] == {
        'url': 'http://www.cookcountylandbank.org/',
        'name': None,
        'address': "Cook County Administration Building, 69 W. Washington St., 22nd Floor, Conference Room 'A', Chicago, IL 60602",
        'coordinates': {
            'latitude': None,
            'longitude': None,
        },
    }


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url': 'http://www.cookcountylandbank.org/events/cclba-finance-committee-meeting-09132017/',
        'note': "Event Page",
    }]


def test__type():
    assert parsed_items[0]['_type'] == 'event'
