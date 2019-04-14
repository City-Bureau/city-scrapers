from datetime import datetime

import pytest
from city_scrapers_core.constants import COMMISSION, PASSED
from tests.utils import file_response

from city_scrapers.spiders.chi_plan_commission import ChiPlanCommissionSpider

test_response = file_response(
    'files/chi_plan_commission_chicago_plan_commission.html',
    'https://www.cityofchicago.org/city/en/depts/dcd/supp_info/chicago_plan_commission.html'
)
spider = ChiPlanCommissionSpider()
parsed_items = [item for item in spider.parse(test_response)]


def test_meeting_count():
    # 12 mtgs / yr * 10 yrs + 1 extra (March 2015)
    assert len(parsed_items) == 121


def test_unique_id():
    assert len(set([item['id'] for item in parsed_items])) == 121


def test_title():
    assert parsed_items[0]['title'] == 'Chicago Plan Commission'


def test_description():
    assert parsed_items[0]['description'] == ''


def test_start():
    assert parsed_items[0]['start'] == datetime(2018, 1, 18, 10)


def test_end():
    assert parsed_items[0]['end'] is None


def test_id():
    assert parsed_items[0]['id'] == 'chi_plan_commission/201801181000/x/chicago_plan_commission'


def test_status():
    assert parsed_items[0]['status'] == PASSED


def test_location():
    assert parsed_items[0]['location'] == {
        'name': 'City Hall',
        'address': '121 N LaSalle St Chicago, IL 60602'
    }


def test_source():
    assert parsed_items[0][
        'source'
    ] == 'https://www.cityofchicago.org/city/en/depts/dcd/supp_info/chicago_plan_commission.html'  # noqa


def test_links():
    assert parsed_items[0]['links'] == [
        {
            'href':
                'https://www.cityofchicago.org/content/dam/city/depts/zlup/Planning_and_Policy/Minutes/CPC_Jan_2018_Minutes.pdf',  # noqa
            'title': 'Minutes'
        },
        {
            'href':
                'https://www.cityofchicago.org/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/CPC_Jan_2018_Map_rev.pdf',  # noqa
            'title': 'Map'
        }
    ]


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == COMMISSION
