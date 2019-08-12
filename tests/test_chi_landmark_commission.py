from datetime import datetime

import pytest
from city_scrapers_core.constants import COMMISSION, PASSED
from tests.utils import file_response

from city_scrapers.spiders.chi_landmark_commission import ChiLandmarkCommissionSpider

test_response = file_response(
    'files/chi_landmark_commission_landmarks_commission.html',
    'https://www.chicago.gov/city/en/depts/dcd/supp_info/landmarks_commission.html'
)
spider = ChiLandmarkCommissionSpider()
parsed_items = [item for item in spider.parse(test_response)]


def test_meeting_count():
    # 12 mtgs / yr * 10 yrs + 3 extra (May 2018, March 2014, June 2013)
    assert len(parsed_items) == 123


def test_unique_id_count():
    assert len(set([item['id'] for item in parsed_items])) == 123


def test_title():
    assert parsed_items[0]['title'] == 'Commission'


def test_description():
    assert parsed_items[0]['description'] == ''


def test_start():
    assert parsed_items[0]['start'] == datetime(2018, 1, 11, 12, 45)


def test_end():
    assert parsed_items[0]['end'] is None


def test_id():
    assert parsed_items[0]['id'] == 'chi_landmark_commission/201801111245/x/commission'


def test_status():
    assert parsed_items[0]['status'] == PASSED


def test_location():
    assert parsed_items[0]['location'] == {
        'name': 'City Hall',
        'address': '121 N LaSalle St, Room 201A, Chicago, IL 60602'
    }


def test_source():
    assert parsed_items[0][
        'source'] == 'https://www.chicago.gov/city/en/depts/dcd/supp_info/landmarks_commission.html'


def test_links():
    assert parsed_items[0]['links'] == [{
        'href':
            'https://www.chicago.gov/content/dam/city/depts/zlup/Historic_Preservation/Minutes/CCLJan2018Minutes.pdf',  # noqa
        'title': 'Minutes'
    }]


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == COMMISSION
