from datetime import datetime

import pytest
from city_scrapers_core.constants import CANCELLED, COMMITTEE
from freezegun import freeze_time
from tests.utils import file_response

from city_scrapers.spiders.wayne_government_operations import WayneGovernmentOperationsSpider

freezer = freeze_time('2018-03-27')
freezer.start()
test_response = file_response(
    'files/wayne_government-operations.html',
    url='https://www.waynecounty.com/elected/commission/government-operations.aspx'
)
spider = WayneGovernmentOperationsSpider()
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
    assert item['title'] == 'Committee on Government Operations'


@pytest.mark.parametrize('item', parsed_items)
def test_end_time(item):
    assert item['end'] is None


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == COMMITTEE


@pytest.mark.parametrize('item', parsed_items)
def test_source(item):
    assert item['source'
                ] == 'https://www.waynecounty.com/elected/commission/government-operations.aspx'


def test_links():
    assert parsed_items[0]['links'] == []


def test_start():
    assert parsed_items[0]['start'] == datetime(2018, 1, 9, 9, 30)


def test_id():
    assert parsed_items[0][
        'id'] == 'wayne_government_operations/201801090930/x/committee_on_government_operations'


def test_status():
    assert parsed_items[0]['status'] == CANCELLED
