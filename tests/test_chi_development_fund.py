from datetime import date, time

import pytest

from tests.utils import file_response
from city_scrapers.spiders.chi_development_fund import Chi_development_fundSpider

test_response = file_response(
    'files/chi_development_fund_chicago_developmentfund.html',
    'https://www.cityofchicago.org/city/en/depts/dcd/supp_info/chicago_developmentfund.html'
)
spider = Chi_development_fundSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_meeting_count():
    assert len(parsed_items) == 57


def test_unique_id_count():
    assert len(set([item['id'] for item in parsed_items])) == 57


def test__type():
    assert parsed_items[0]['_type'] == 'event'


def test_name():
    assert parsed_items[0]['name'] == 'Chicago Development Fund (Advisory Board)'


def test_description():
    assert parsed_items[0]['event_description'] == \
           'The Chicago City Council established the Chicago Development Fund (CDF) in July 2005. CDF is an Illinois ' \
           'not-for-profit corporation that allocates New Markets Tax Credits to help stimulate private sector ' \
           'investment in economically distressed communities. The tax credits are converted into investment capital ' \
           'for community and economic development projects in qualified low-income census tracts.'


def test_start():
    assert parsed_items[0]['start'] == {
        'date': date(2018, 4, 18),
        'time': None,
        'note': 'see agenda document for time'
    }


def test_end():
    assert parsed_items[0]['end'] == {
        'date': date(2018, 4, 18),
        'time': None,
        'note': ''
    }


def test_id():
    assert parsed_items[0]['id'] == 'chi_development_fund/201804180000/x/chicago_development_fund_advisory_board'


def test_status():
   assert parsed_items[0]['status'] == 'passed'


def test_location():
    assert parsed_items[0]['location'] == {
        'neighborhood': '',
        'name': 'City Hall',
        'address': '121 N. LaSalle St., Room 1000'
    }


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url': 'https://www.cityofchicago.org/city/en/depts/dcd/supp_info/chicago_developmentfund.html',
        'note': ''
    }]


def test_documents():
    assert parsed_items[0]['documents'] == [
        {
            'url': 'https://www.cityofchicago.org/content/dam/city/depts/dcd/agendas/CDF_Advisor_Board_Agenda_April_2018.pdf',
            'note': 'Agenda'
        }
    ]
    assert parsed_items[-1]['documents'] == [
        {
            'url': 'https://www.cityofchicago.org/content/dam/city/depts/dcd/supp_info/agendas/CDF_GB_Agenda_April2009.pdf',
            'note': 'Agenda'
        }
    ]


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == 'Commission'
