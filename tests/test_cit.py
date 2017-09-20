from tests.utils import file_response
from documenters_aggregator.spiders.cit import CitSpider

test_response = file_response('files/cit.html')
spider = CitSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]

def test_name():
    assert parsed_items[0]['name'] == 'Chicago Infrastructure Trust'


def test_description():
    assert parsed_items[0]['description'] is None


def test_start_time():
    assert parsed_items[0]['start_time'] == '2017-10-11T00:00:00+00:00'


def test_end_time():
    assert parsed_items[0]['end_time'] is None


def test_id():
    assert parsed_items[0]['id'] == '2017-10-11'


def test_all_day():
    assert parsed_items[0]['all_day'] is False


def test_classification():
    assert parsed_items[0]['classification'] == "Board Meeting"


def test_status():
    assert parsed_items[0]['status'] == 'tentative'


# def test_location(item):
#     assert item['location'] == {
#         'url': 'EXPECTED URL',
#         'name': 'EXPECTED NAME',
#         'coordinates': {
#             'latitude': 'EXPECTED LATITUDE',
#             'longitude': 'EXPECTED LONGITUDE',
#         },
#     }


def test__type():
    assert parsed_items[0]['_type'] == 'event'
