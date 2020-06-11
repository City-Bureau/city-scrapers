from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, PASSED
from city_scrapers_core.items import Meeting
from city_scrapers_core.utils import file_response
from freezegun import freeze_time
from scrapy.settings import Settings

from city_scrapers.spiders.chi_plan_commission import ChiPlanCommissionSpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_plan_commission.html"),
    url="https://chicago.gov/city/en/depts/dcd/supp_info/chicago_plan_commission.html",
)
test_detail_response = file_response(
    join(dirname(__file__), "files", "chi_plan_commission_detail.html"),
    url=(
        "https://www.chicago.gov/city/en/depts/dcd/supp_info/chicago_plan_commission/february-2020.html"  # noqa
    ),
)
spider = ChiPlanCommissionSpider()
spider.settings = Settings(values={"CITY_SCRAPERS_ARCHIVE": False})

freezer = freeze_time("2020-02-05")
freezer.start()

parsed_items = [
    item for item in spider.parse(test_response) if isinstance(item, Meeting)
]
parsed_detail = [
    item
    for item in spider._parse_detail(
        test_detail_response, start=datetime(2020, 2, 5, 10)
    )
][0]

freezer.stop()


def test_meeting_count():
    assert len(parsed_items) == 22


def test_unique_id():
    assert len(set([item["id"] for item in parsed_items])) == 22


def test_title():
    assert parsed_items[0]["title"] == "Commission"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2020, 1, 23, 10, 0)
    assert parsed_detail["start"] == datetime(2020, 2, 5, 10)


def test_end():
    assert parsed_items[0]["end"] is None


def test_id():
    assert parsed_items[0]["id"] == "chi_plan_commission/202001231000/x/commission"


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == spider.location


def test_source():
    assert parsed_items[0]["source"] == test_response.url


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/CPC_Jan_2020_Agenda.pdf",  # noqa
            "title": "Agenda ",
        },
        {
            "href": "https://chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/CPC_Jan_2020_Map_rev.pdf",  # noqa
            "title": "Map",
        },
    ]
    assert parsed_detail["links"] == [
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/dcd/supp_info/woodlawn/woodlawn_report_draft_01_29_2020.pdf",  # noqa
            "title": 'Draft "Woodlawn Plan Consolidation Report"',
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/02_2020/5616_s_maryland.pdf",  # noqa
            "title": "PD Amendment Application",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/02_2020/808_n_cleveland.pdf",  # noqa
            "title": "PD Amendment Application",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/02_2020/180_n_ada.pdf",  # noqa
            "title": "PD Amendment Application",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/02_2020/1150_w_lake.pdf",  # noqa
            "title": "PD Application",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/02_2020/725_w_randolph.pdf",  # noqa
            "title": "PD Amendment Application",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/02_2020/777_n_franklin.pdf",  # noqa
            "title": "PD Application",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/02_2020/141_w_diversey.pdf",  # noqa
            "title": "LPO Application",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/CPC_Feb_2020_Public_Notice.pdf",  # noqa
            "title": "Public Notice",
        },
    ]


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False


@pytest.mark.parametrize("item", parsed_items)
def test_classification(item):
    assert item["classification"] == COMMISSION
