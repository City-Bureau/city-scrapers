from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMITTEE, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.wayne_public_safety import WaynePublicSafetySpider

freezer = freeze_time('2018-03-27')
freezer.start()
test_response = file_response(
    join(dirname(__file__), "files", "wayne_public_safety.html"),
    url='https://www.waynecounty.com/elected/commission/public-safety-judiciary.aspx'
)
spider = WaynePublicSafetySpider()
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
    assert item['title'] == 'Committee on Public Safety, Judiciary, and Homeland Security'


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
                ] == 'https://www.waynecounty.com/elected/commission/public-safety-judiciary.aspx'


def test_links():
    assert parsed_items[0]['links'] == [{
        'title': 'Agenda',
        'href': 'https://www.waynecounty.com/documents/commission/psjnotice20178_jan17.pdf',
    }]


def test_start():
    assert parsed_items[0]['start'] == datetime(2018, 1, 16, 10)


def test_id():
    assert parsed_items[0][
        'id'
    ] == 'wayne_public_safety/201801161000/x/committee_on_public_safety_judiciary_and_homeland_security'  # noqa


def test_status():
    assert parsed_items[0]['status'] == PASSED
