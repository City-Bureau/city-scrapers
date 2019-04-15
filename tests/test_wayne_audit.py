from datetime import datetime

import pytest
from city_scrapers_core.constants import COMMITTEE, PASSED
from freezegun import freeze_time
from tests.utils import file_response

from city_scrapers.spiders.wayne_audit import WayneAuditSpider

freezer = freeze_time('2018-03-27')
freezer.start()
test_response = file_response(
    'files/wayne_audit.html', url='https://www.waynecounty.com/elected/commission/audit.aspx'
)
spider = WayneAuditSpider()
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
    assert item['title'] == 'Audit Committee'


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
    assert item['source'] == 'https://www.waynecounty.com/elected/commission/audit.aspx'


def test_links():
    assert parsed_items[0]['links'] == [{
        'title': 'Agenda',
        'href': 'https://www.waynecounty.com/documents/commission/adtmtg_2018-0117.pdf',
    }]


def test_start():
    assert parsed_items[0]['start'] == datetime(2018, 1, 17, 9, 30)


def test_id():
    assert parsed_items[0]['id'] == 'wayne_audit/201801170930/x/audit_committee'


def test_status():
    assert parsed_items[0]['status'] == PASSED
