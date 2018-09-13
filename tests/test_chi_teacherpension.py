import pytest

from tests.utils import file_response
from datetime import datetime
from datetime import time
from city_scrapers.constants import BOARD
from city_scrapers.spiders.chi_teacherpension import ChiTeacherPensionSpider


test_response = file_response('files/chi_teacherpension.htm')
spider = ChiTeacherPensionSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[0]['name'] == 'Regular Board Meeting'


def test_description():
    assert parsed_items[0]['description'] == """The Chicago Teachers’ Pension Fund (CTPF) Board of Trustees meets monthly to discuss and make decisions on various issues, proceedings, and financial matters that affect the Fund. All meetings are held at 9:30 a.m. in the CTPF office unless otherwise noted. Meetings are open to the public, except when the Board goes into executive session."""


def test_start_time():
    assert parsed_items[0]['start'] == {'date': datetime(2018, 5, 17, 0, 0), 
                                        'time': time(9, 30), 
                                        'note': ''}


def test_end_time():
    assert parsed_items[0]['end'] == {'date': datetime(2018, 5, 17, 0, 0), 
                                        'time': None, 
                                        'note': ''}


def test_id():
    assert parsed_items[0]['id'] == 'chi_teacherpension/201805170930/x/regular_board_meeting'

def test_classification():
    assert parsed_items[0]['classification'] == BOARD


##### Parametrized Tests ####

@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_status(item):
    assert item['status'] == 'tentative'


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'

@pytest.mark.parametrize('item', parsed_items)
def test_location(item):
    assert item['location'] == {'address': '203 North LaSalle Street, Suite 2600, Board Room', 
                                'name': 'CTPF office', 
                                'neighborhood': 'Loop'}


@pytest.mark.parametrize('item', parsed_items)
def test_sources(item):
    assert item['sources'] == [{'url': 'http://www.example.com', 
                                'note': ''}]