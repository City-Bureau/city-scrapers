from datetime import date, time

import pytest
from freezegun import freeze_time

from tests.utils import file_response
from city_scrapers.constants import BOARD, COMMITTEE, PASSED
from city_scrapers.spiders.chi_low_income_housing_trust_fund import (
    ChiLowIncomeHousingTrustFundSpider
)


@pytest.fixture
def parsed_items():
    freezer = freeze_time('2018-10-31')
    freezer.start()
    spider = ChiLowIncomeHousingTrustFundSpider()
    cal_res = file_response('files/chi_low_income_housing_trust_fund.html')
    parsed_items = []
    for item in spider._parse_calendar(cal_res):
        detail_res = file_response(
            'files/chi_low_income_housing_trust_fund_detail.html'
        )
        detail_res.meta['item'] = item
        parsed_items.append(spider._parse_detail(detail_res))
    freezer.stop()
    return parsed_items


def test_name(parsed_items):
    assert parsed_items[0]['name'] == 'Finance Committee'
    assert parsed_items[1]['name'] == 'Allocations Committee'
    assert parsed_items[2]['name'] == 'Board Meeting'


def test_start(parsed_items):
    assert parsed_items[0]['start'] == {
        'date': date(2018, 10, 4),
        'time': time(10, 0),
        'note': ''
    }


def test_end(parsed_items):
    assert parsed_items[0]['end'] == {
        'date': date(2018, 10, 4),
        'time': time(11, 0),
        'note': ''
    }


def test_id(parsed_items):
    assert parsed_items[0]['id'] == (
        'chi_low_income_housing_trust_fund/201810041000/x/finance_committee'
    )


def test_classification(parsed_items):
    assert parsed_items[0]['classification'] == COMMITTEE
    assert parsed_items[2]['classification'] == BOARD


def test_status(parsed_items):
    assert parsed_items[0]['status'] == PASSED


def test_description(parsed_items):
    assert parsed_items[0]['event_description'] == (
        'Meeting of the CLIHTF Finance Committee.  To attend, send Name and '
        'Planned Attendance Date to info@chicagotrustfund.org.  Regular '
        'Meeting Location:  Chicago City Hall, Rm. 1006c.'
    )


def test_location(parsed_items):
    assert parsed_items[0]['location'] == {
        'address': '121 N. La Salle - Room 1006 Chicago, IL 60602',
        'name': '',
        'neighborhood': '',
    }


@pytest.mark.parametrize('item', parsed_items())
def test_documents(item):
    assert item['documents'] == []


@pytest.mark.parametrize('item', parsed_items())
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items())
def test_sources(item):
    assert len(item['sources']) == 1


@pytest.mark.parametrize('item', parsed_items())
def test__type(item):
    assert item['_type'] == 'event'
