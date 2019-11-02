from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.wayne_full_commission import WayneFullCommissionSpider

freezer = freeze_time('2018-03-27')
freezer.start()
test_response = file_response(
    join(dirname(__file__), "files", "wayne_full_commission.html"),
    url='https://www.waynecounty.com/elected/commission/full-commission.aspx'
)
spider = WayneFullCommissionSpider()
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
    assert item['title'] == 'Full Commission'


@pytest.mark.parametrize('item', parsed_items)
def test_end_time(item):
    assert item['end'] is None


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == BOARD


@pytest.mark.parametrize('item', parsed_items)
def test_sources(item):
    assert item['source'] == 'https://www.waynecounty.com/elected/commission/full-commission.aspx'


def test_links():
    assert parsed_items[0]['links'] == [
        {
            'title': 'Agenda',
            'href': 'https://www.waynecounty.com/documents/commission/fullboard011118.pdf',
        },
        {
            'title': 'Journal',
            'href': 'https://www.waynecounty.com/documents/commission/journal2018-111.pdf'
        },
    ]


def test_start():
    assert parsed_items[0]['start'] == datetime(2018, 1, 11, 10)


def test_id():
    assert parsed_items[0]['id'] == 'wayne_full_commission/201801111000/x/full_commission'


def test_status():
    assert parsed_items[0]['status'] == PASSED
