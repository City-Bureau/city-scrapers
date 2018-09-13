import pytest

from freezegun import freeze_time
from tests.utils import file_response
from city_scrapers.constants import COMMITTEE
from city_scrapers.spiders.chi_transit import ChiTransitSpider
from datetime import date, time

freezer = freeze_time('2018-01-01 12:00:00')
freezer.start()

test_response = file_response('files/chi_transit.html',
    url='https://www.transitchicago.com/board/notices-agendas-minutes/')
spider = ChiTransitSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]

freezer.stop()


def test_meeting_count():
    assert len(parsed_items) == 23

def test_unique_id_count():
    assert len(set([item['id'] for item in parsed_items])) == 23

def test_name():
    assert parsed_items[0]['name'] == 'Employee Retirement Review Committee Meeting'

def test_description():
    assert parsed_items[0]['event_description'] == ''

def test_start():
    EXPECTED_START = {
        'date': date(2018, 6, 15),
        'time': time(14, 0),
        'note': ''
    }
    assert parsed_items[0]['start'] == EXPECTED_START

def test_end():
    EXPECTED_END = {
        'date': date(2018, 6, 15),
        'time': time(17, 0),
        'note': 'estimated 3 hours after start time'
    }
    assert parsed_items[0]['end'] == EXPECTED_END


def test_classification():
    assert parsed_items[0]['classification'] == COMMITTEE


def test_id():
    assert parsed_items[0]['id'] == 'chi_transit/201806151400/x/employee_retirement_review_committee_meeting'


def test_status():
    assert parsed_items[0]['status'] == 'confirmed'


def test_location():
    assert parsed_items[0]['location'] == {
        'neighborhood': 'west loop',
        'name': 'Chicago Transit Authority 2nd Floor Boardroom',
        'address': '567 West Lake Street Chicago, IL'
    }


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url': 'https://www.transitchicago.com/board/notices-agendas-minutes/',
        'note': ''
   }]

def test_documents():
    assert parsed_items[0]['documents'] == [
        {
            'note': 'Meeting Notice',
            'url': 'http://www.transitchicago.com/assets/1/21/061818_ERR_Notice.pdf?20564'
        },
        {
            'note': 'Agenda',
            'url': 'http://www.transitchicago.com/assets/1/21/061818_ERR_Agenda.pdf?20565'
        },
    ]


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert parsed_items[0]['_type'] == 'event'
