from datetime import date, time

import pytest

from tests.utils import file_response
from city_scrapers.spiders.chi_zoning_board import ChiZoningBoardSpider


test_response = file_response('files/chi_zoning_board.html', 'https://www.cityofchicago.org/city/en/depts/dcd/supp_info/zoning_board_of_appeals.html')
spider = ChiZoningBoardSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_meeting_count():
    # 12 mtgs / yr * 10 yrs + 2 extra (May 2015, and August 2014)
    assert len(parsed_items) == 122


def test_unique_id_count():
    assert len(set([item['id'] for item in parsed_items])) == 122


def test__type():
    assert parsed_items[0]['_type'] == 'event'


def test_name():
    assert parsed_items[0]['name'] == 'Zoning Board of Appeals'


def test_description():
    assert parsed_items[0]['event_description'] == \
           "The Zoning Board of Appeals reviews land use issues that pertain to the Chicago Zoning Ordinance, " \
           "including proposed variations from the zoning code, special uses that require review to determine " \
           "compatibility with adjacent properties, and appeals of decisions made by the Zoning Administrator. " \
           "Established in 1923, the board has five members that are appointed by the Mayor with City Council " \
           "consent. Staff services are provided by the Zoning Ordinance Administration Division of the Department of " \
           "Planning and Development. Meetings are held on the third Friday of every month, usually at City Hall, " \
           "121 N. LaSalle St., in City Council chambers."


def test_start():
    assert parsed_items[0]['start'] == {
        'date': date(2018, 1, 19),
        'time': time(9, 0),
        'note': ''
    }


def test_end():
    assert parsed_items[0]['end'] == {
        'date': date(2018, 1, 19),
        'time': None,
        'note': ''
    }


def test_id():
    assert parsed_items[0]['id'] == 'chi_zoning_board/201801190900/x/zoning_board_of_appeals'


def test_status():
   assert parsed_items[0]['status'] == 'passed'


def test_location():
    assert parsed_items[0]['location'] == {
        'neighborhood': '',
        'name': 'City Hall',
        'address': '121 N. LaSalle St., in City Council chambers'
    }


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url': 'https://www.cityofchicago.org/city/en/depts/dcd/supp_info/zoning_board_of_appeals.html',
        'note': ''
    }]


def test_documents():
    assert parsed_items[0]['documents'] == [
        {
            'url': 'https://www.cityofchicago.org/content/dam/city/depts/zlup/Administrative_Reviews_and_Approvals/Agendas/ZBA_Jan_2018_Minutes_rev.pdf',
            'note': 'Minutes'
        }, {
            'url': 'https://www.cityofchicago.org/content/dam/city/depts/zlup/Administrative_Reviews_and_Approvals/Agendas/ZBA_Jan_2018_Map.pdf',
            'note': 'Map'

        }]


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is True


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == 'Commission'



