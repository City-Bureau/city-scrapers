import pytest
from datetime import date, time

from tests.utils import file_response
from city_scrapers.constants import BOARD
from city_scrapers.spiders.chi_pubhealth import ChiPubHealthSpider

test_response = file_response('files/chi_pubhealth.html', url='https://www.cityofchicago.org/city/en/depts/cdph/supp_info/boh/2018-board-of-health-meetings.html')
spider = ChiPubHealthSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]

def test_meeting_count():
    # 1 meeting per month
    assert len(parsed_items) == 12


def test_unique_id_count():
    assert len(set([item['id'] for item in parsed_items])) == 12


def test_name():
    assert parsed_items[0]['name'] == 'Board of Health Meeting'


def test_description():
    assert parsed_items[0]['event_description'] == 'The Chicago Board of Health is scheduled to meet on the third Wednesday of each month from 9:00am-10:30am. The meetings are held at the Chicago Department of Public Health, DePaul Center, 333 S. State Street, 2nd Floor Board Room. The specific dates, by month, for 2018 are:'


def test_start():
    EXPECTED_START = {
        'date': date(2018, 1, 17),
        'time': time(9, 0),
        'note': ''
    }
    assert parsed_items[0]['start'] == EXPECTED_START


def test_end():
    EXPECTED_END = {
        'date': date(2018, 1, 17),
        'time': time(10, 30),
        'note': ''
    }
    assert parsed_items[0]['end'] == EXPECTED_END


def test_id():
    assert parsed_items[0]['id'] == 'chi_pubhealth/201801170900/x/board_of_health_meeting'


def test_status():
    assert parsed_items[0]['status'] == 'passed'


def test_documents():
    EXPECTED_DOCUMENTS = [
        {
            'note': 'agenda',
            'url': 'https://www.cityofchicago.org/content/dam/city/depts/cdph/policy_planning/Board_of_Health/BOH_Agenda_Jan172018.pdf'
        },
        {
            'note': 'minutes',
            'url': 'https://www.cityofchicago.org/content/dam/city/depts/cdph/policy_planning/Board_of_Health/BOH_Minutes_Jan172018.pdf'
        }
    ]
    assert parsed_items[0]['documents'] == EXPECTED_DOCUMENTS


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == BOARD


@pytest.mark.parametrize('item', parsed_items)
def test_location(item):
    assert item['location'] == {
        'name': '2nd Floor Board Room, DePaul Center',
        'address': '333 S. State Street, Chicago, IL',
        'neighborhood': 'Loop'
    }


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'


@pytest.mark.parametrize('item', parsed_items)
def test_sources(item):
    assert item['sources'] == [{'url': test_response.url, 'note': ''}]