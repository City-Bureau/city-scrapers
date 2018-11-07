from datetime import date, time

import pytest
from freezegun import freeze_time

from tests.utils import file_response
from city_scrapers.constants import CONFIRMED, PASSED, COMMISSION
from city_scrapers.spiders.chi_ssa_42 import ChiSsa42Spider


@pytest.fixture()
def parsed_items():
    freezer = freeze_time('2018-11-07')
    freezer.start()
    spider = ChiSsa42Spider()
    res = file_response('files/chi_ssa_42.html')
    minutes_res = file_response('files/chi_ssa_42_minutes.html')
    parsed_items = [
        item for item in spider._parse_items(res, upcoming=True)
    ] + [item for item in spider._parse_items(minutes_res)]
    freezer.stop()
    return parsed_items


def test_start(parsed_items):
    assert parsed_items[0]['start'] == {
        'date': date(2018, 11, 8),
        'time': time(18, 30),
        'note': ''
    }
    assert parsed_items[1]['start'] == {
        'date': date(2018, 9, 20),
        'time': time(18, 30),
        'note': '',
    }


def test_id(parsed_items):
    assert parsed_items[0]['id'] == (
        'chi_ssa_42/201811081830/x/ssa_42_commission'
    )


def test_status(parsed_items):
    assert parsed_items[0]['status'] == CONFIRMED
    assert parsed_items[-1]['status'] == PASSED


def test_documents(parsed_items):
    assert parsed_items[0]['documents'] == []
    assert parsed_items[1]['documents'] == [
        {
            'url': (
                'https://ssa42.org/wp-content/uploads/sites/6/2018/'
                '09/SSAMeetingAgendaSeptember202018.pdf'
            ), 'note': 'Agenda'
        }, {
            'url': (
                'https://ssa42.org/wp-content/uploads/sites/6/2018/'
                '11/SSAMEETINGMINUTES_Sep202018.pdf'
            ),
            'note': 'Minutes'
        }
    ]


def test_name(parsed_items):
    assert parsed_items[0]['name'] == 'SSA #42 Commission'
    assert parsed_items[4]['name'] == 'SSA #42 Commission - Closed Meeting'


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
    spider = ChiSsa42Spider()
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
