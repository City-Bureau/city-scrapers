from datetime import date, time

import pytest

from tests.utils import file_response
from city_scrapers.spiders.chi_plan_commission import Chi_plan_commissionSpider


test_response = file_response(
    'files/chi_plan_commission_chicago_plan_commission.html',
    'https://www.cityofchicago.org/city/en/depts/dcd/supp_info/chicago_plan_commission.html'
)
spider = Chi_plan_commissionSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_meeting_count():
    # 12 mtgs / yr * 10 yrs + 1 extra (March 2015)
    assert len(parsed_items) == 121


def test_unique_id():
    assert len(set([item['id'] for item in parsed_items])) == 121


def test__type():
    assert parsed_items[0]['_type'] == 'event'


def test_name():
    assert parsed_items[0]['name'] == 'Chicago Plan Commission'


def test_description():
    assert parsed_items[0]['event_description'] == \
           "The Chicago Plan Commission is responsible for the review of proposals that " \
           "involve Planned Developments (PDs), the Lakefront Protection Ordinance, Planned " \
           "Manufacturing Districts (PMDs), Industrial Corridors and Tax Increment Financing " \
           "(TIF) Districts. It also reviews proposed sales and acquisitions of public land " \
           "as well as certain long-range community plans. Established in 1909, the " \
           "commission has 22 members, including mayoral appointees made with City " \
           "Council consent. Staff services are provided by the Planning and Zoning Division " \
           "of the Department of Planning and Development (DPD). Meetings are held on " \
           "the third Thursday of every month, usually at City Hall, 121 N. LaSalle St., " \
           "in City Council chambers."


def test_start():
    assert parsed_items[0]['start'] == {
        'date': date(2018, 1, 18),
        'time': time(10, 0),
        'note': ''
    }


def test_end():
    assert parsed_items[0]['end'] == {
        'date': date(2018, 1, 18),
        'time': None,
        'note': ''
    }


def test_id():
    assert parsed_items[0]['id'] == 'chi_plan_commission/201801181000/x/chicago_plan_commission'


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
        'url': 'https://www.cityofchicago.org/city/en/depts/dcd/supp_info/chicago_plan_commission.html',
        'note': ''
    }]


def test_documents():
    assert parsed_items[0]['documents'] == [
        {
            'url': 'https://www.cityofchicago.org/content/dam/city/depts/zlup/Planning_and_Policy/Minutes/CPC_Jan_2018_Minutes.pdf',
            'note': 'Minutes'
        }, {
            'url': 'https://www.cityofchicago.org/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/CPC_Jan_2018_Map_rev.pdf',
            'note': 'Map'

        }]


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is True


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == 'Commission'



