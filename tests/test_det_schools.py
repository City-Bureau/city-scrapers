import pytest

from tests.utils import file_response
from documenters_aggregator.spiders.det_schools import Det_schoolsSpider

test_response = file_response('files/det_schools.html')
spider = Det_schoolsSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[0]['name'] == 'Policy Ad-hoc Sub-Committee Meeting (Open)'


def test_description():
    assert parsed_items[0]['description'] == 'Policy Ad-hoc Sub-Committee Meeting (Open)'


def test_start_time():
    assert parsed_items[0]['start_time'].isoformat() == '2018-04-17T09:00:00'


def test_end_time():
    assert parsed_items[0]['end_time'].isoformat() == '2018-04-17T10:30:00'


def test_id():
    assert parsed_items[0]['id'] == 'det_schools/201804170900/MmlhcTcyNW50Nm43dWZqN3BpOWwzYmF1ZzRfMjAxODA0MTdUMTMwMDAwWiA4bmpua21kbzgxcDdyZGw0MjA4dDI2MmM2b0Bn/policy_ad_hoc_sub_committee_meeting_open'


def test_location():
    assert parsed_items[0]['location'] == {
        'url': '',
        'name': '',
        'address': 'Fisher Building, 3011 W. Grand Boulevard, 12th Floor Conference Room',
        'coordinates': {
            'latitude': '',
            'longitude': '',
        },
    }


# def test_sources():
    # assert parsed_items[0]['sources'] == {
        # 'url': 'EXPECTED URL',
        # 'note': 'EXPECTED NOTE'
    # }


# @pytest.mark.parametrize('item', parsed_items)
# def test_timezone(item):
    # assert item['timezone'] == 'EXPECTED TIMEZONE'


# @pytest.mark.parametrize('item', parsed_items)
# def test_all_day(item):
    # assert item['all_day'] is False


# @pytest.mark.parametrize('item', parsed_items)
# def test_classification(item):
    # assert item['classification'] is None


# @pytest.mark.parametrize('item', parsed_items)
# def test__type(item):
    # assert parsed_items[0]['_type'] == 'event'
