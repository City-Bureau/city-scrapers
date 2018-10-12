from datetime import date, time

import pytest

from tests.utils import file_response
from freezegun import freeze_time
from city_scrapers.constants import PASSED, TENTATIVE, COMMISSION
from city_scrapers.spiders.chi_ssa_14 import ChiSsa14Spider


test_response = file_response('files/chi_ssa_14.html')
spider = ChiSsa14Spider()

freezer = freeze_time('2018-10-12 12:00:00')
freezer.start()

parsed_items = [
    item for item in spider.parse(test_response)
    if isinstance(item, dict)
]

freezer.stop()


def test_start():
    assert parsed_items[0]['start'] == {
        'date': date(2018, 4, 25),
        'time': time(19, 0),
        'note': ''
    }


def test_id():
    assert parsed_items[0]['id'] == (
        'chi_ssa_14/201804251900/x/ssa_governing_commission'
    )


def test_status():
    assert parsed_items[0]['status'] == PASSED
    assert parsed_items[-1]['status'] == TENTATIVE


def test_documents():
    assert parsed_items[0]['documents'] == [{
      'url': 'http://www.mp-security.org/images/stories/minutes25april2018.pdf',
      'note': 'Minutes',
    }]
    assert parsed_items[-1]['documents'] == []


@pytest.mark.parametrize('item', parsed_items)
def test_name(item):
    assert item['name'] == 'SSA Governing Commission'


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
        'address': '2711 W. 71ST STREET CHICAGO, IL 60629',
        'name': 'Lithuanian Human Services Council',
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
