import pytest

from tests.utils import file_response
from documenters_aggregator.spiders.ilrb import IlrbSpider


test_response = file_response('files/ilrb.html')
spider = IlrbSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]
print(parsed_items)


def test_name():
    assert parsed_items[0]['name'] == 'Local panel meeting'


@pytest.mark.parametrize('item', parsed_items)
def test_description(item):
    assert item['description'] == 'To discuss issues and cases pending before the panel'


def test_start_time():
    assert parsed_items[1]['start_time'] == '2017-09-12T13:00:00-05:00'


def test_end_time():
    assert parsed_items[0]['end_time'] == '2017-09-07T11:00:00-05:00'


@pytest.mark.parametrize('item', parsed_items)
def test_id(item):
    assert item['id'] is None


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == 'board meeting'


@pytest.mark.parametrize('item', parsed_items)
def test_status(item):
    assert item['status'] == 'confirmed'


def test_location():
    assert parsed_items[0]['location'] == {
        'url': None,
        'name': '160 N. LaSalle Street, Room N-401, Chicago, IL',
        'coordinates': {
            'latitude': None,
            'longitude': None,
        },
    }

    assert parsed_items[1]['location'] == {
        'url': None,
        'name': 'Conference Room 5A, 801 S. 7th Street, Springfield, IL',
        'coordinates': {
            'latitude': None,
            'longitude': None,
        },
    }


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'
