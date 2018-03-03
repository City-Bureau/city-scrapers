import pytest
from tests.utils import file_response
from documenters_aggregator.spiders.chi_police import Chi_policeSpider

test_response = file_response('files/chi_police.json')
spider = Chi_policeSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_name():
    assert isinstance(parsed_items[0]['name'], str)


def test_description():
    assert isinstance(parsed_items[0]['description'], str)


def test_start_time():
    assert parsed_items[0]['start_time'].isoformat() == '2017-12-28T18:30:00-06:00'


def test_end_time():
    assert parsed_items[0]['end_time'].isoformat() == '2017-12-28T19:30:00-06:00'


def test_id():
    assert parsed_items[0]['id'] == 'chi_police/201712281830/25/2514_beat_meeting'


def test_all_day():
    assert parsed_items[0]['all_day'] is False


def test_classification():
    assert parsed_items[0]['classification'] == 'CAPS community event'


def test_status():
    assert parsed_items[0]['status'] == 'confirmed'


def test_location():
    assert isinstance(parsed_items[0]['location']['address'], str)


def test__type():
    assert isinstance(parsed_items[0]['_type'], str)


@pytest.mark.parametrize('item', parsed_items)
def test_sources(item):
    EXPECTED_SOURCES = [{'url': 'https://home.chicagopolice.org/get-involved-with-caps/all-community-event-calendars',
                         'note': ''}]
    assert item['sources'] == EXPECTED_SOURCES


@pytest.mark.parametrize('item', parsed_items)
def test_timezone(item):
    assert item['timezone'] == 'America/Chicago'
