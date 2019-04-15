from datetime import datetime

import pytest
from city_scrapers_core.constants import COMMISSION, PASSED
from tests.utils import file_response

from city_scrapers.spiders.chi_development_fund import ChiDevelopmentFundSpider

test_response = file_response(
    'files/chi_development_fund_chicago_developmentfund.html',
    'https://www.chicago.gov/city/en/depts/dcd/supp_info/chicago_developmentfund.html'
)
spider = ChiDevelopmentFundSpider()
parsed_items = [item for item in spider.parse(test_response)]


def test_meeting_count():
    assert len(parsed_items) == 42


def test_unique_id_count():
    assert len(set([item['id'] for item in parsed_items])) == 42


def test_title():
    assert parsed_items[0]['title'] == 'Chicago Development Fund: Advisory Board'


def test_description():
    assert parsed_items[0]['description'] == ''


def test_start():
    assert parsed_items[0]['start'] == datetime(2018, 4, 18)


def test_end():
    assert parsed_items[0]['end'] is None


def test_time_notes():
    assert parsed_items[0]['time_notes'] == 'See agenda for time'


def test_id():
    assert parsed_items[0][
        'id'] == 'chi_development_fund/201804180000/x/chicago_development_fund_advisory_board'


def test_status():
    assert parsed_items[0]['status'] == PASSED


def test_location():
    assert parsed_items[0]['location'] == {
        'name': 'City Hall',
        'address': '121 N LaSalle St, Room 1000, Chicago, IL 60602'
    }


def test_sources():
    assert parsed_items[0][
        'source'
    ] == 'https://www.chicago.gov/city/en/depts/dcd/supp_info/chicago_developmentfund.html'  # noqa


def test_links():
    assert parsed_items[0]['links'] == [{
        'href':
            'https://www.chicago.gov/content/dam/city/depts/dcd/agendas/CDF_Advisor_Board_Agenda_April_2018.pdf',  # noqa
        'title': 'Agenda'
    }]
    assert parsed_items[-1]['links'] == []


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == COMMISSION
