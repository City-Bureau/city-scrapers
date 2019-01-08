from datetime import date, time

import pytest
from freezegun import freeze_time
from tests.utils import file_response

from city_scrapers.constants import BOARD, TENTATIVE
from city_scrapers.spiders.chi_teacherpension import ChiTeacherPensionSpider

freezer = freeze_time('2018-12-30')
freezer.start()

test_response = file_response('files/chi_teacherpension.html')
spider = ChiTeacherPensionSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]

freezer.stop()


def test_name():
    assert parsed_items[0]['name'] == 'Regular Board Meeting'


def test_start_time():
    assert parsed_items[0]['start'] == {'date': date(2019, 1, 17), 'time': time(9, 30), 'note': ''}


def test_end_time():
    assert parsed_items[0]['end'] == {'date': date(2019, 1, 17), 'time': None, 'note': ''}


def test_id():
    assert parsed_items[0]['id'] == 'chi_teacherpension/201901170930/x/regular_board_meeting'


def test_classification():
    assert parsed_items[0]['classification'] == BOARD


def test_status():
    assert parsed_items[0]['status'] == TENTATIVE


def test_documents():
    assert parsed_items[0]['documents'] == []
    assert parsed_items[18]['documents'] == [{
        'note': 'Meeting Agenda',
        'url': 'https://www.ctpf.org/sites/main/files/file-attachments/010419_rtw_agenda.pdf'
    }]


@pytest.mark.parametrize('item', parsed_items)
def test_description(item):
    assert item['description'] == ''


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'


@pytest.mark.parametrize('item', parsed_items)
def test_location(item):
    assert item['location'] == {
        'address': '203 N LaSalle St, Suite 2600 Board Room, Chicago, IL 60601',
        'name': 'CTPF office',
        'neighborhood': 'Loop',
    }


@pytest.mark.parametrize('item', parsed_items)
def test_sources(item):
    assert item['sources'] == [{'url': 'http://www.example.com', 'note': ''}]
