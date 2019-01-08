from datetime import date, time

import pytest
from freezegun import freeze_time
from tests.utils import file_response

from city_scrapers.constants import COMMISSION, CONFIRMED, PASSED
from city_scrapers.spiders.chi_ssa_25 import ChiSsa25Spider

test_response = file_response(
    'files/chi_ssa_25.html', 'http://littlevillagechamber.org/2018-meetings-minutes/'
)
spider = ChiSsa25Spider()

freezer = freeze_time('2018-12-13')
freezer.start()

parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]

freezer.stop()


def test_name():
    assert parsed_items[0]['name'] == 'Commission: Monthly'


def test_start():
    assert parsed_items[0]['start'] == {
        'date': date(2018, 1, 16),
        'time': time(9, 0),
        'note': '',
    }
    assert parsed_items[-1]['start'] == {
        'date': date(2018, 12, 18),
        'time': time(9, 0),
        'note': '',
    }


def test_end():
    assert parsed_items[0]['end'] == {
        'date': date(2018, 1, 16),
        'time': time(10, 0),
        'note': '',
    }
    assert parsed_items[-1]['end'] == {
        'date': date(2018, 12, 18),
        'time': time(10, 0),
        'note': '',
    }


def test_id():
    assert parsed_items[0]['id'] == 'chi_ssa_25/201801160900/x/commission_monthly'


def test_status():
    assert parsed_items[0]['status'] == PASSED
    assert parsed_items[-1]['status'] == CONFIRMED


def test_location():
    assert parsed_items[0]['location'] == {
        'name': 'LV-Chamber',
        'address': '3610 W. 26th St., 2nd Floor Chicago, IL',
        'neighborhood': '',
    }
    assert parsed_items[-1]['location'] == {
        'name': 'La Catedral Café',
        'address': '2500 S. Christiana Chicago, IL',
        'neighborhood': '',
    }


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url': 'http://littlevillagechamber.org/2018-meetings-minutes/',
        'note': '',
    }]


def test_documents():
    assert parsed_items[0]['documents'] == [{
        'url':
            'http://littlevillagechamber.org/wp-content/uploads/2018/03/Jan.-2018-Meeting-minutes-to-approve.pdf',  # noqa
        'note': 'Minutes'
    }]
    assert parsed_items[-1]['documents'] == []


@pytest.mark.parametrize('item', parsed_items)
def test_event_description(item):
    assert item['event_description'] == ''


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == COMMISSION


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert parsed_items[0]['_type'] == 'event'
