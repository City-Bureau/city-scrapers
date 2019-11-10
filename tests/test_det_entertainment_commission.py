from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, PASSED
from city_scrapers_core.utils import file_response

from city_scrapers.spiders.det_entertainment_commission import DetEntertainmentCommissionSpider

test_response = file_response(
    join(dirname(__file__), "files", "det_entertainment_commission.html"),
    url='https://www.detroitsentertainmentcommission.com/services'
)
spider = DetEntertainmentCommissionSpider()
parsed_items = [item for item in spider.parse(test_response)]


def test_title():
    assert parsed_items[0]['title'] == 'Entertainment Commission'


def test_description():
    assert parsed_items[0]['description'] == ''


def test_start():
    assert parsed_items[0]['start'] == datetime(2018, 7, 16, 17)


def test_end():
    assert parsed_items[0]['end'] is None


def test_id():
    assert parsed_items[0][
        'id'] == 'det_entertainment_commission/201807161700/x/entertainment_commission'


def test_status():
    assert parsed_items[0]['status'] == PASSED


def test_location():
    assert parsed_items[0]['location'] == {
        'name': 'Coleman A. Young Municipal Center',
        'address': '2 Woodward Ave, Detroit, MI 48226'
    }


def test_source():
    assert parsed_items[0]['source'] == 'https://www.detroitsentertainmentcommission.com/services'


def test_links():
    assert parsed_items[0]['links'] == []


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == COMMISSION
