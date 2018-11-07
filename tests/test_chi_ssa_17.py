from datetime import date, time

import pytest
from freezegun import freeze_time

from tests.utils import file_response
from city_scrapers.constants import PASSED, TENTATIVE, COMMISSION
from city_scrapers.spiders.chi_ssa_17 import ChiSsa17Spider


@pytest.fixture()
def parsed_items():
    freezer = freeze_time('2018-11-07')
    freezer.start()
    spider = ChiSsa17Spider()
    res = file_response('files/chi_ssa_17.html')
    parsed_items = [item for item in spider.parse(res)]
    freezer.stop()
    return parsed_items


def test_start(parsed_items):
    assert parsed_items[0]['start'] == {
        'date': date(2018, 1, 24),
        'time': time(10, 0),
        'note': ''
    }


def test_id(parsed_items):
    assert parsed_items[0]['id'] == (
        'chi_ssa_17/201801241000/x/ssa_17_commission'
    )


def test_status(parsed_items):
    assert parsed_items[0]['status'] == PASSED
    assert parsed_items[-1]['status'] == TENTATIVE


def test_documents(parsed_items):
    assert parsed_items[0]['documents'] == [{
        'url': (
            'https://drive.google.com/open?id='
            '1XdwmrLKkUGc2LShNwerRDV6BbFjgvXwX'
        ),
        'note': 'Minutes'
    }]
    assert parsed_items[-1]['documents'] == []


@pytest.mark.parametrize('item', parsed_items())
def test_name(item):
    assert item['name'] == 'SSA #17 Commission'


@pytest.mark.parametrize('item', parsed_items())
def test_description(item):
    assert item['event_description'] == ''


@pytest.mark.parametrize('item', parsed_items())
def test_end(item):
    assert item['end']['date'] == item['start']['date']
    assert item['end']['time'] is None


@pytest.mark.parametrize('item', parsed_items())
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items())
def test_location(item):
    spider = ChiSsa17Spider()
    assert item['location'] == spider.location


@pytest.mark.parametrize('item', parsed_items())
def test_classification(item):
    assert item['classification'] == COMMISSION


@pytest.mark.parametrize('item', parsed_items())
def test_sources(item):
    assert len(item['sources']) == 1


@pytest.mark.parametrize('item', parsed_items())
def test__type(item):
    assert item['_type'] == 'event'
