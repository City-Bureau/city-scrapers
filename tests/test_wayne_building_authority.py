from datetime import datetime

import pytest
from city_scrapers_core.constants import CANCELLED, COMMITTEE
from freezegun import freeze_time
from tests.utils import file_response

from city_scrapers.spiders.wayne_building_authority import WayneBuildingAuthoritySpider

freezer = freeze_time('2018-03-27')
freezer.start()
test_response = file_response(
    'files/wayne_building_authority_meetings.html',
    url='https://www.waynecounty.com/boards/buildingauthority/meetings.aspx'
)
spider = WayneBuildingAuthoritySpider()
parsed_items = [item for item in spider.parse(test_response)]
freezer.stop()


@pytest.mark.parametrize('item', parsed_items)
def test_location(item):
    assert item['location'] == spider.location


@pytest.mark.parametrize('item', parsed_items)
def test_title(item):
    assert item['title'] == 'Building Authority'


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
def test_sources(item):
    assert item['source'] == 'https://www.waynecounty.com/boards/buildingauthority/meetings.aspx'


def test_links():
    assert parsed_items[-1]['links'] == []


def test_start():
    assert parsed_items[-1]['start'] == datetime(2018, 1, 17, 10)


def test_id():
    assert parsed_items[-1]['id'] == 'wayne_building_authority/201801171000/x/building_authority'


def test_status():
    assert parsed_items[-1]['status'] == CANCELLED
