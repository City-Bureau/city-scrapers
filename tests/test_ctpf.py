import pytest

from tests.utils import file_response
from documenters_aggregator.spiders.ctpf import CtpfSpider

def test_tests():
    print('Please write some tests for this spider or at least disable this one.')
    assert False


"""
Uncomment below
"""

# test_response = file_response('files/ctpf.html')
# spider = CtpfSpider()
# parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


# def test_name():
    # assert parsed_items[0]['name'] == 'EXPECTED NAME'


# def test_description():
    # assert parsed_items[0]['description'] == 'EXPECTED DESCRIPTION'


# def test_start_time():
    # assert parsed_items[0]['start_time'] == 'EXPECTED START DATE AND TIME'


# def test_end_time():
    # assert parsed_items[0]['end_time'] == 'EXPECTED END DATE AND TIME'


# def test_id():
    # assert parsed_items[0]['id'] == 'EXPECTED ID'


# def test_all_day(item):
    # assert parsed_items[0]['all_day'] is False


# def test_classification(item):
    # assert parsed_items[0]['classification'] == None


# def test_status(item):
    # assert parsed_items[0]['status'] == 'tentative'


# def test_location(item):
    # assert item['location'] == {
        # 'url': 'EXPECTED URL',
        # 'name': 'EXPECTED NAME',
        # 'coordinates': {
            # 'latitude': 'EXPECTED LATITUDE',
            # 'longitude': 'EXPECTED LONGITUDE',
        # },
    # }


# def test__type(item):
    # assert parsed_items[0]['_type'] == 'event'
