# -*- coding: utf-8 -*-
import pytest

from tests.utils import file_response
from datetime import date, time
from city_scrapers.constants import COMMITTEE
from city_scrapers.spiders.il_labor import IlLaborSpider


test_response = file_response('files/il_labor.html', url='https://www.illinois.gov/ilrb/meetings/Pages/default.aspx')
spider = IlLaborSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]

def test_name():
    assert parsed_items[0]['name'] == 'Local panel meeting'


@pytest.mark.parametrize('item', parsed_items)
def test_description(item):
    assert item['event_description'] == "The State and Local Panel's of the Illinois Labor Relations Board meet separately on a monthly basis to discuss issues and cases pending before the Panels.\n    Meetings are open to the public and are conducted in accordance with the Illinois Open Meetings Act."


@pytest.mark.parametrize('item', parsed_items)
def test_timezone(item):
    assert item['timezone'] == 'America/Chicago'


def test_start_time():
    assert parsed_items[0]['start']['date'] == date(2018, 7, 10)
    assert parsed_items[0]['start']['time'] == time(10, 0)


@pytest.mark.parametrize('item', parsed_items)
def test_end_time(item):
    assert parsed_items[0]['end']['date'] == date(2018, 7, 10)
    assert parsed_items[0]['end']['time'] == time(13, 0)


# def test_id():
#    assert parsed_items[1]['id'] == 'il_labor/201806121300/x/state_panel_meeting'


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


# @pytest.mark.parametrize('item', parsed_items)
# def test_classification(item):
#     assert item['classification'] == COMMITTEE


@pytest.mark.parametrize('item', parsed_items)
def test_status(item):
    assert item['status'] == 'tentative'


def test_location():
    assert parsed_items[0]['location'] == {
        'url': '',
        'name': '',
        'address': 'Room S-401, 160 N. LaSalle Street, Chicago, IL'
    }


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'


@pytest.mark.parametrize('item', parsed_items)
def test_sources(item):
    assert item['sources'] == [{'url': 'https://www.illinois.gov/ilrb/meetings/Pages/default.aspx', 'note': ''}]
