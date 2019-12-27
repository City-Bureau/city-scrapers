from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time
from scrapy.settings import Settings

from city_scrapers.spiders.chi_plan_commission import ChiPlanCommissionSpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_plan_commission.html"),
    url='https://chicago.gov/city/en/depts/dcd/supp_info/chicago_plan_commission.html'
)
spider = ChiPlanCommissionSpider()
spider.settings = Settings(values={"CITY_SCRAPERS_ARCHIVE": False})

freezer = freeze_time("2018-01-01")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_meeting_count():
    assert len(parsed_items) == 24


def test_unique_id():
    assert len(set([item['id'] for item in parsed_items])) == 24


def test_title():
    assert parsed_items[0]['title'] == 'Commission'


def test_description():
    assert parsed_items[0]['description'] == ''


def test_start():
    assert parsed_items[0]['start'] == datetime(2018, 1, 18, 10)


def test_end():
    assert parsed_items[0]['end'] is None


def test_id():
    assert parsed_items[0]['id'] == 'chi_plan_commission/201801181000/x/commission'


def test_status():
    assert parsed_items[0]['status'] == TENTATIVE


def test_location():
    assert parsed_items[0]['location'] == {
        'name': 'City Hall',
        'address': '121 N LaSalle St Chicago, IL 60602'
    }


def test_source():
    assert parsed_items[0][
        'source'
    ] == 'https://chicago.gov/city/en/depts/dcd/supp_info/chicago_plan_commission.html'  # noqa


def test_links():
    assert parsed_items[0]['links'] == [
        {
            'href':
                'https://chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Minutes/CPC_Jan_2018_Minutes.pdf',  # noqa
            'title': 'Minutes'
        },
        {
            'href':
                'https://chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/CPC_Jan_2018_Map_rev.pdf',  # noqa
            'title': 'Map'
        }
    ]


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == COMMISSION
