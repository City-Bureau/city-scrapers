# -*- coding: utf-8 -*-
from datetime import date, time

import pytest
from freezegun import freeze_time
from tests.utils import file_response

from city_scrapers.constants import BOARD, PASSED
from city_scrapers.spiders.il_labor import IlLaborSpider

freezer = freeze_time('2018-12-12')
freezer.start()
test_response = file_response(
    'files/il_labor.html', url='https://www.illinois.gov/ilrb/meetings/Pages/default.aspx'
)
spider = IlLaborSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]
freezer.stop()


def test_name():
    assert parsed_items[0]['name'] == 'Local Panel Meeting'


@pytest.mark.parametrize('item', parsed_items)
def test_description(item):
    assert item[
        'event_description'
    ] == "The State and Local Panel's of the Illinois Labor Relations Board meet separately on a monthly basis to discuss issues and cases pending before the Panels. Meetings are open to the public and are conducted in accordance with the Illinois Open Meetings Act."  # noqa


@pytest.mark.parametrize('item', parsed_items)
def test_timezone(item):
    assert item['timezone'] == 'America/Chicago'


def test_start_time():
    assert parsed_items[0]['start']['date'] == date(2018, 12, 11)
    assert parsed_items[0]['start']['time'] == time(9, 0)


def test_end_time():
    assert parsed_items[0]['end']['date'] == date(2018, 12, 11)
    assert parsed_items[0]['end']['time'] == time(12, 0)


def test_id():
    assert parsed_items[0]['id'] == 'il_labor/201812110900/x/local_panel_meeting'


def test_documents():
    assert parsed_items[0]['documents'] == [{
        'url': 'https://www2.illinois.gov/ilrb/Documents/LPAgenda.pdf',
        'note': 'Agenda',
    }]


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == BOARD


@pytest.mark.parametrize('item', parsed_items)
def test_status(item):
    assert item['status'] == PASSED


def test_location():
    assert parsed_items[0]['location'] == {
        'url': '',
        'name': '',
        'address': '160 N. LaSalle Street, Room S-401, Chicago, IL'
    }


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'


@pytest.mark.parametrize('item', parsed_items)
def test_sources(item):
    assert item['sources'] == [{
        'url': 'https://www.illinois.gov/ilrb/meetings/Pages/default.aspx',
        'note': ''
    }]
