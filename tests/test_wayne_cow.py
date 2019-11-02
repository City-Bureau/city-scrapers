from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMITTEE, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.wayne_cow import WayneCommitteeWholeSpider

freezer = freeze_time('2018-04-26')
freezer.start()
test_response = file_response(
    join(dirname(__file__), "files", "wayne_cow.html"),
    url='https://www.waynecounty.com/elected/commission/committee-of-the-whole.aspx'
)
spider = WayneCommitteeWholeSpider()
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
    assert item['title'] == 'Committee of the Whole'


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
    assert item['source'
                ] == 'https://www.waynecounty.com/elected/commission/committee-of-the-whole.aspx'


def test_links():
    assert parsed_items[0]['links'] == [{
        'title': 'Agenda',
        'href': 'https://www.waynecounty.com/documents/commission/cowmtg01-10-17.pdf',
    }]


def test_start():
    assert parsed_items[0]['start'] == datetime(2018, 1, 10, 10)


def test_status():
    assert parsed_items[0]['status'] == PASSED


def test_id():
    assert parsed_items[0]['id'] == 'wayne_cow/201801101000/x/committee_of_the_whole'
