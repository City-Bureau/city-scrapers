from datetime import datetime

import pytest
from city_scrapers_core.constants import BOARD, PASSED
from freezegun import freeze_time
from tests.utils import file_response

from city_scrapers.spiders.il_labor import IlLaborSpider

freezer = freeze_time('2018-12-12')
freezer.start()
test_response = file_response(
    'files/il_labor.html', url='https://www.illinois.gov/ilrb/meetings/Pages/default.aspx'
)
spider = IlLaborSpider()
parsed_items = [item for item in spider.parse(test_response)]
freezer.stop()


def test_title():
    assert parsed_items[0]['title'] == 'Local Panel Meeting'


@pytest.mark.parametrize('item', parsed_items)
def test_description(item):
    assert item[
        'description'
    ] == "The State and Local Panel's of the Illinois Labor Relations Board meet separately on a monthly basis to discuss issues and cases pending before the Panels. Meetings are open to the public and are conducted in accordance with the Illinois Open Meetings Act."  # noqa


def test_start():
    assert parsed_items[0]['start'] == datetime(2018, 12, 11, 9)


def test_end():
    assert parsed_items[0]['end'] is None


def test_id():
    assert parsed_items[0]['id'] == 'il_labor/201812110900/x/local_panel_meeting'


def test_links():
    assert parsed_items[0]['links'] == [{
        'href': 'https://www.illinois.gov/ilrb/Documents/LPAgenda.pdf',
        'title': 'Agenda',
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
        'name': '',
        'address': '160 N. LaSalle Street, Room S-401, Chicago, IL'
    }


@pytest.mark.parametrize('item', parsed_items)
def test_source(item):
    assert item['source'] == 'https://www.illinois.gov/ilrb/meetings/Pages/default.aspx'
