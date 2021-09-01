from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.minn_audit_comm import MinnAuditCommSpider

test_response = file_response(
    join(dirname(__file__), "files", "minn_audit_comm.html"),
    url="https://lims.minneapolismn.gov/Calendar/GetCalenderList?fromDate=Sep%201,%202021&toDate=null&meetingType=4&committeeId=1&pageCount=3000&offsetStart=0&abbreviation=undefined&keywords=",
)
spider = MinnAuditCommSpider()

freezer = freeze_time("2021-09-01")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


"""
Uncomment below
"""
def test_title():
    assert parsed_items[0]["title"] == "Audit Committee"


# def test_description():
#     assert parsed_items[0]["description"] == "EXPECTED DESCRIPTION"


def test_start():
    assert parsed_items[0]["start"] == datetime(2021, 10, 18, 10, 0)


def test_status():
    assert parsed_items[0]["status"] == "tentative"


def test_classification():
    assert parsed_items[0]["classification"] == "Committee"


# @pytest.mark.parametrize("item", parsed_items)
def test_all_day():
    assert parsed_items[0]["all_day"] is False
