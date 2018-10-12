from datetime import date, time

import pytest
from freezegun import freeze_time

from tests.utils import file_response
from city_scrapers.constants import PASSED, TENTATIVE, COMMISSION
from city_scrapers.spiders.chi_ssa_5 import ChiSsa5Spider

spider = ChiSsa5Spider()


@pytest.fixture()
def parsed_items():
    freezer = freeze_time('2018-10-12 12:00:00')
    freezer.start()
    minutes_req = file_response('files/chi_ssa_5_minutes.html')
    minutes_req.meta['items'] = spider._parse_current_year(
        file_response('files/chi_ssa_5.html')
    )
    parsed_items = [item for item in spider._parse_minutes(minutes_req)]
    freezer.stop()
    return parsed_items


def test_name(parsed_items):
    assert parsed_items[0]['name'] == 'Regular Commission Meeting'
    assert parsed_items[4]['name'] == 'Special Commission Meeting'


def test_start(parsed_items):
    assert parsed_items[0]['start'] == {
        'date': date(2018, 1, 25),
        'time': time(14, 0),
        'note': ''
    }


def test_id(parsed_items):
    assert parsed_items[0]['id'] == (
        'chi_ssa_5/201801251400/x/regular_commission_meeting'
    )


def test_status(parsed_items):
    assert parsed_items[0]['status'] == PASSED
    assert parsed_items[13]['status'] == TENTATIVE
    assert parsed_items[-1]['status'] == PASSED


def test_documents(parsed_items):
    assert parsed_items[0]['documents'] == [
        {
            'url': 'http://scpf-inc.org/wp-content/uploads/2018/04/January-Agenda.pdf',
            'note': 'Agenda',
        },
        {
            'url': 'http://scpf-inc.org/wp-content/uploads/2018/04/SSA-Meeting-Minutes-January-25-2018.pdf',
            'note': 'Minutes',
        }
    ]
    assert parsed_items[11]['documents'] == []


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
