from datetime import datetime

import pytest
from city_scrapers_core.constants import CANCELLED, COMMITTEE
from freezegun import freeze_time
from tests.utils import file_response

from city_scrapers.spiders.wayne_ways_means import WayneWaysMeansSpider

freezer = freeze_time('2018-03-27')
freezer.start()
test_response = file_response(
    'files/wayne_ways_means.html',
    url='https://www.waynecounty.com/elected/commission/ways-means.aspx'
)
spider = WayneWaysMeansSpider()
parsed_items = [item for item in spider.parse(test_response)]
freezer.stop()


@pytest.mark.parametrize('item', parsed_items)
def test_description(item):
    assert item['description'] == ''


@pytest.mark.parametrize('item', parsed_items)
def test_location(item):
    assert item['location'] == spider.location


@pytest.mark.parametrize('item', parsed_items)
def test_title(item):
    assert item['title'] == 'Ways and Means Committee'


@pytest.mark.parametrize('item', parsed_items)
def test_end(item):
    assert item['end'] is None


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == COMMITTEE


@pytest.mark.parametrize('item', parsed_items)
def test_source(item):
    assert item['source'] == 'https://www.waynecounty.com/elected/commission/ways-means.aspx'


def test_links():
    assert parsed_items[0]['links'] == []


def test_start():
    assert parsed_items[0]['start'] == datetime(2018, 1, 9, 12)


def test_id():
    assert parsed_items[0]['id'] == 'wayne_ways_means/201801091200/x/ways_and_means_committee'


def test_status():
    assert parsed_items[0]['status'] == CANCELLED
