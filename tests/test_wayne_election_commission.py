from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, PASSED
from city_scrapers_core.utils import file_response

from city_scrapers.spiders.wayne_election_commission import WayneElectionCommissionSpider

test_response = file_response(
    join(dirname(__file__), "files", "wayne_election_commission.html"),
    url='https://www.waynecounty.com/elected/clerk/election-commission.aspx'
)
spider = WayneElectionCommissionSpider()
parsed_items = [item for item in spider.parse(test_response)]


def test_title():
    assert parsed_items[0]['title'] == 'Election Commission'


def test_description():
    assert parsed_items[0]['description'] == ''


def test_start():
    assert parsed_items[0]['start'] == datetime(2018, 1, 29)


def test_end():
    assert parsed_items[0]['end'] is None


def test_id():
    assert parsed_items[0]['id'] == 'wayne_election_commission/201801290000/x/election_commission'


def test_status():
    assert parsed_items[0]['status'] == PASSED


def test_location():
    assert parsed_items[0]['location'] == spider.location


def test_source():
    assert parsed_items[0]['source'
                           ] == 'https://www.waynecounty.com/elected/clerk/election-commission.aspx'


def test_links():
    assert parsed_items[1]['links'] == [{
        'href': 'https://www.waynecounty.com/documents/clerk/wecn2518.pdf',
        'title': 'Notice'
    }, {
        'href': 'https://www.waynecounty.com/documents/clerk/eca20518.pdf',
        'title': 'Agenda'
    }, {
        'href': 'https://www.waynecounty.com/documents/clerk/ecm20518.pdf',
        'title': 'Minutes'
    }]


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == COMMISSION
