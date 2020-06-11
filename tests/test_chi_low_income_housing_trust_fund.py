from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, COMMITTEE, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_low_income_housing_trust_fund import (
    ChiLowIncomeHousingTrustFundSpider,
)

freezer = freeze_time("2018-10-31")
freezer.start()
spider = ChiLowIncomeHousingTrustFundSpider()
cal_res = file_response(
    join(dirname(__file__), "files", "chi_low_income_housing_trust_fund.html")
)
parsed_items = []
for item in spider._parse_calendar(cal_res):
    detail_res = file_response(
        join(
            dirname(__file__), "files", "chi_low_income_housing_trust_fund_detail.html"
        )
    )
    detail_res.meta["item"] = item
    parsed_items.append(spider._parse_detail(detail_res))
freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Finance Committee"
    assert parsed_items[1]["title"] == "Allocations Committee"
    assert parsed_items[2]["title"] == "Board Meeting"


def test_start():
    assert parsed_items[0]["start"] == datetime(2018, 10, 4, 10, 0)


def test_end():
    assert parsed_items[0]["end"] == datetime(2018, 10, 4, 11, 0)


def test_id():
    assert parsed_items[0]["id"] == (
        "chi_low_income_housing_trust_fund/201810041000/x/finance_committee"
    )


def test_classification():
    assert parsed_items[0]["classification"] == COMMITTEE
    assert parsed_items[2]["classification"] == BOARD


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_description():
    assert parsed_items[0]["description"] == (
        "Meeting of the CLIHTF Finance Committee.  To attend, send Name and "
        "Planned Attendance Date to info@chicagotrustfund.org.  Regular "
        "Meeting Location:  Chicago City Hall, Rm. 1006c."
    )


def test_location():
    assert parsed_items[0]["location"] == {
        "address": "121 N. La Salle - Room 1006 Chicago, IL 60602",
        "name": "",
    }


@pytest.mark.parametrize("item", parsed_items)
def test_links(item):
    assert item["links"] == []


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
