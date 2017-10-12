import pytest

from tests.utils import file_response
from documenters_aggregator.spiders.ward_night import WardNightSpider

test_response = file_response('files/ward_night.json')
spider = WardNightSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_id():
    assert parsed_items[0]['id'] == 'ward1-2017-01-01'


def test_name():
    assert parsed_items[0]['name'] == 'Ward Night with Alderman Joe Moreno (Ward 1)'


def test_description():
    assert parsed_items[0]['description'] == 'first come first served, one-on-one meetings usually about 10-20 minutes'


# def test_start_time():
#     assert parsed_items[0]['start_time'] == ''


# def test_end_time():
#     assert parsed_items[0]['end_time'] == ''


# def test_location():
#     assert parsed_items[0]['location'] == {
#         'url': '',
#         'name': '',
#         'coordinates': {
#             'latitude': None,
#             'longitude': None,
#         },
#         'address': ''
#     }


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert parsed_items[0]['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert parsed_items[0]['classification'] is None


@pytest.mark.parametrize('item', parsed_items)
def test_status(item):
    assert parsed_items[0]['status'] == 'tentative'


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert parsed_items[0]['_type'] == 'event'
