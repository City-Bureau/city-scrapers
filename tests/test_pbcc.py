import pytest

from tests.utils import file_response
from documenters_aggregator.spiders.pbcc import PbccSpider


test_response = file_response('files/pbcc.html')
spider = PbccSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[0]['name'] == 'Daley Plaza - Italian Exhibit'


def test_afb_name():
    assert parsed_items[3]['name'] == 'Advertisement for Bids - Ebinger Elementary School Annex'


@pytest.mark.parametrize('item', parsed_items)
def test_description(item):
    assert item['description'] is None


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


@pytest.mark.parametrize('item', parsed_items)
def test_location(item):
    assert item['location'] == {
        'url': None,
        'name': None,
        'coordinates': {
            'latitude': None,
            'longitude': None,
        },
    }


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert parsed_items[0]['_type'] == 'event'


def test_source():
    assert parsed_items[0]['sources'][0]['url'] == 'http://www.pbcchicago.com/content/about/calendar_detail.asp?eID=2176'
