from datetime import date, time

import pytest

from tests.utils import file_response
from freezegun import freeze_time
from city_scrapers.constants import CONFIRMED, PASSED, TENTATIVE, COMMISSION
from city_scrapers.spiders.chi_ssa_1 import ChiSsa1Spider


test_response = file_response('files/chi_ssa_1.html')
spider = ChiSsa1Spider()

freezer = freeze_time('2018-10-12 12:00:00')
freezer.start()

parsed_items = [
    item for item in spider.parse(test_response)
    if isinstance(item, dict)
]

freezer.stop()


def test_start():
    assert parsed_items[0]['start'] == {
        'date': date(2018, 1, 16),
        'time': time(14, 0),
        'note': ''
    }


def test_id():
    assert parsed_items[0]['id'] == (
        'chi_ssa_1/201801161400/x/state_street_commission'
    )


def test_status():
    assert parsed_items[0]['status'] == PASSED
    assert parsed_items[5]['status'] == CONFIRMED
    assert parsed_items[-1]['status'] == TENTATIVE


def test_documents():
    assert parsed_items[0]['documents'] == [{
      'url': 'https://loopchicago.com/assets/State-Street-Commission-Meeting-Minutes/da3d4977e1/2018-january-16-ssc-meeting-minutes.pdf',
      'note': 'Minutes',
    }]
    assert parsed_items[-1]['documents'] == []


@pytest.mark.parametrize('item', parsed_items)
def test_name(item):
    assert item['name'] == 'State Street Commission'


@pytest.mark.parametrize('item', parsed_items)
def test_description(item):
    assert item['event_description'] == ''


@pytest.mark.parametrize('item', parsed_items)
def test_end(item):
    assert item['end']['date'] == item['start']['date']
    assert item['end']['time'] is None


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_location(item):
    assert item['location'] == {
        'address': '190 N State St Chicago, IL 60601',
        'name': 'ABC 7 Chicago',
        'neighborhood': '',
    }


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == COMMISSION


@pytest.mark.parametrize('item', parsed_items)
def test_sources(item):
    assert len(item['sources']) == 1


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'
