from datetime import datetime

import pytest
from city_scrapers_core.constants import COMMITTEE, PASSED
from freezegun import freeze_time
from tests.utils import file_response

from city_scrapers.spiders.wayne_economic_development import WayneEconomicDevelopmentSpider

freezer = freeze_time('2018-03-27')
freezer.start()
test_response = file_response(
    'files/wayne_economic-development.html',
    url='https://www.waynecounty.com/elected/commission/economic-development.aspx'
)
spider = WayneEconomicDevelopmentSpider()
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
    assert item['title'] == 'Committee on Economic Development'


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
                ] == 'https://www.waynecounty.com/elected/commission/economic-development.aspx'


def test_links():
    assert parsed_items[0]['links'] == [{
        'title': 'Agenda',
        'href': 'https://www.waynecounty.com/documents/commission/edcnotice2018_jan9.pdf',
    }]


def test_start():
    assert parsed_items[0]['start'] == datetime(2018, 1, 9, 11)


def test_id():
    assert parsed_items[0][
        'id'] == 'wayne_economic_development/201801091100/x/committee_on_economic_development'


def test_status():
    assert parsed_items[0]['status'] == PASSED
