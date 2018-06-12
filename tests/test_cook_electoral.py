import pytest

from datetime import date, time
from tests.utils import file_response
from city_scrapers.spiders.cook_electoral import Cook_electoralSpider


"""
Uncomment below
"""

test_response = file_response('files/cook_electoral.html')
spider = Cook_electoralSpider()
parsed_items = [item for item in spider.parse_results(test_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[0]['name'] == 'Board Meeting'


def test_description():
    assert parsed_items[0]['description'] == ''


def test_start_time():
    assert parsed_items[0]['start']['date'] == date(2018, 1, 9)
    assert parsed_items[0]['start']['time'] == time(9, 0)


def test_end_time():
    assert parsed_items[0]['end'] == {}


def test_id():
    assert parsed_items[0]['id'] == 'cook_electoral/201801090900/x/board_meeting'


def test_location():
    assert parsed_items[0]['location'] == {
        'url': '',
        'name': 'County Board Room, County Building',
        'address': '118 N. Clark Street, 5th Floor, Chicago'
    }


def test_documents():
    assert parsed_items[0]['documents'] == [
        {
            'note': 'January 9, 2018 Consent Agenda',
            'url': 'http://aba-clerk.s3-website-us-east-1.amazonaws.com/Agenda_pdf_010918_490.pdf'
        },
        {
            'note': 'January 9, 2018 Consent Agenda - Second Set',
            'url': 'http://aba-clerk.s3-website-us-east-1.amazonaws.com/PostBoardAgenda_pdf_010918_490.pdf'
        },
        {
            'note': 'January 9, 2018 Consent Agenda - Third Set',
            'url': 'http://aba-clerk.s3-website-us-east-1.amazonaws.com/NewItemsAgenda_pdf_010918_490.pdf'
        },
        {
            'note': 'January 9, 2018 Resolutions',
            'url': 'http://aba-clerk.s3-website-us-east-1.amazonaws.com/Resolution_pdf_010918_490.pdf'
        },
        {
            'note': 'January 9, 2018 Consent Journal of Proceedings',
            'url': 'http://aba-clerk.s3-website-us-east-1.amazonaws.com/Journal_pdf_010918_490.pdf'
        }
    ]


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url': 'https://www.cookcountyclerk.com/service/board-meetings',
        'note': 'Must submit form to see any dates'
    }]

