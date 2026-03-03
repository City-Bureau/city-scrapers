from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, TENTATIVE
from city_scrapers_core.items import Meeting
from city_scrapers_core.utils import file_response
from freezegun import freeze_time
from scrapy.http import Request
from scrapy.settings import Settings

from city_scrapers.spiders.chi_plan_commission import ChiPlanCommissionSpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_plan_commission.html"),
    url="https://www.chicago.gov/city/en/depts/dcd/chicago-plan-commission/meetings--agendas---video-archives.html?wcmmode=disabled",
)
test_detail_response = file_response(
    join(dirname(__file__), "files", "chi_plan_commission_detail.html"),
    url="https://www.chicago.gov/city/en/depts/dcd/supp_info/chicago_plan_commission/August_2025_Plan_Commission_Hearing.html",  # noqa
)

spider = ChiPlanCommissionSpider()
spider.settings = Settings(values={"CITY_SCRAPERS_ARCHIVE": False})

freezer = freeze_time("2026-03-02")
freezer.start()

parse_results = list(spider.parse(test_response))

parsed_items = [x for x in parse_results if isinstance(x, Meeting)]
parsed_requests = [x for x in parse_results if isinstance(x, Request)]

parsed_detail = [
    item
    for item in spider._parse_detail(test_detail_response, start=datetime(2025, 8, 21, 10))
][0]

freezer.stop()


def _sorted_by_start(items):
    return sorted(items, key=lambda x: x["start"])


def test_main_page_total_outputs_cover_12_meetings():
  
    assert len(parsed_items) == 9
    assert len(parsed_requests) == 13
    assert len(parse_results) == 22


def test_2026_meeting_items_are_apr_through_dec():
    expected_starts = [
        datetime(2026, 4, 16, 10, 0),
        datetime(2026, 5, 21, 10, 0),
        datetime(2026, 6, 18, 10, 0),
        datetime(2026, 7, 16, 10, 0),
        datetime(2026, 8, 20, 10, 0),
        datetime(2026, 9, 17, 10, 0),
        datetime(2026, 10, 15, 10, 0),
        datetime(2026, 11, 19, 10, 0),
        datetime(2026, 12, 17, 10, 0),
    ]
    items = _sorted_by_start(parsed_items)
    assert [i["start"] for i in items] == expected_starts


def test_2026_detail_requests_are_jan_feb_mar():
    urls = sorted([r.url for r in parsed_requests])
    expected_urls = sorted([
        "https://www.chicago.gov/content/city/en/depts/dcd/supp_info/chicago_plan_commission/January_2026_Plan_Commission_Hearing.html",
        "https://www.chicago.gov/content/city/en/depts/dcd/supp_info/chicago_plan_commission/February_2026_Plan_Commission_Hearing.html",
        "https://www.chicago.gov/content/city/en/depts/dcd/supp_info/chicago_plan_commission/March_2026_Plan_Commission_Hearing.html",
        "https://www.chicago.gov/content/city/en/depts/dcd/supp_info/chicago_plan_commission/March_2025_Plan_Commission_Hearing.html",
        "https://www.chicago.gov/content/city/en/depts/dcd/supp_info/chicago_plan_commission/April_2025_Plan_Commission_Hearing.html",
        "https://www.chicago.gov/content/city/en/depts/dcd/supp_info/chicago_plan_commission/May_2025_Plan_Commission_Hearing.html",
        "https://www.chicago.gov/content/city/en/depts/dcd/supp_info/chicago_plan_commission/June_2025_Plan_Commission_Hearing.html",
        "https://www.chicago.gov/content/city/en/depts/dcd/supp_info/chicago_plan_commission/July_2025_Plan_Commission_Hearing.html",
        "https://www.chicago.gov/content/city/en/depts/dcd/supp_info/chicago_plan_commission/August_2025_Plan_Commission_Hearing.html",
        "https://www.chicago.gov/content/city/en/depts/dcd/supp_info/chicago_plan_commission/September_2025_Plan_Commission_Hearing.html",
        "https://www.chicago.gov/content/city/en/depts/dcd/supp_info/chicago_plan_commission/October_2025_Plan_Commission_Hearing.html",
        "https://www.chicago.gov/content/city/en/depts/dcd/supp_info/chicago_plan_commission/November_2025_Plan_Commission_Hearing.html",
        "https://www.chicago.gov/content/city/en/depts/dcd/supp_info/chicago_plan_commission/December_2025_Plan_Commission_Hearing.html",
    ])
    assert urls == expected_urls


def test_unique_id_for_meeting_items():
    assert len(set([item["id"] for item in parsed_items])) == 9


def test_title_description_defaults():
    assert parsed_items[0]["title"] == "Commission"
    assert parsed_items[0]["description"] == ""


def test_start():
    items = _sorted_by_start(parsed_items)
    assert items[0]["start"] == datetime(2026, 4, 16, 10, 0)

    assert parsed_detail["start"] == datetime(2025, 8, 21, 10)


def test_end():
    assert parsed_items[0]["end"] is None


def test_id_format_matches_start_datetime():
    for item in parsed_items:
        dt_str = item["start"].strftime("%Y%m%d%H%M")
        assert f"/{dt_str}/" in item["id"]


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == spider.location


def test_source():
    assert parsed_items[0]["source"] == test_response.url


def test_links():
    assert parsed_items[0]["links"] == []
    assert parsed_detail["links"] == [
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/08_2025/7.31.2025_DRAFT_August_2025_PUBLIC_NOTICE.pdf",
            "title": "Public Notice",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/08_2025/DRAFT_AUGUST_21_2025_Agenda.pdf",
            "title": "Agenda",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/08_2025/Chicago_Plan_Commission_August_2025.pdf",
            "title": "Map",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/08_2025/Chicago_Plan_Commission_August_2025_with_Planning_Regions.pdf",
            "title": "Planning Region Map",
        },
        {
            "href": "https://youtube.com/watch?v=lhBdveUNxJQ",
            "title": "Video",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/08_2025/LPO_APP_790_6402-6420_S_Stony_Island_Ave.pdf",
            "title": "LPO Application",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/08_2025/6402-20_Stony_Island_Full_Packet_AS_FILED.pdf",
            "title": "PD Application",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/08_2025/20250821_6402-6420_S_Stony_Island_CPC_Presentation_R2.pdf",
            "title": "Presentation",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/08_2025/Written_Comments/6400_S_Stony_Island_Public_Comments_Against.pdf",
            "title": "Public Comments - Against",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/08_2025/Written_Comments/6400_S_Stony_Island_Public_Comments_Support.pdf",
            "title": "Public Comments - Support",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/08_2025/2025-07-29_FILED_Lakefront_Protection_Application_795.pdf",
            "title": "LPO Application",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/08_2025/2025.08.21_Metra_59th_&_60th_St_LPO_CPC_Presentation.pdf",
            "title": "Presentation",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/08_2025/Written_Comments/59th_Metra_Public_Comments_ALL.pdf",
            "title": "Public Comments",
        },
        {
            "href": "https://www.chicago.gov/city/en/depts/dcd/supp_info/major-taylor-trail-framework-plan.html",
            "title": "https://www.chicago.gov/city/en/depts/dcd/supp_info/major-taylor-trail-framework-plan.html",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/08_2025/2025_08_21_Major_Taylor_Trail%20Planning_CPC.pdf",
            "title": "Presentation",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/08_2025/Written_Comments/Major_Taylor_Trail_Framework_Public_Comments_ALL.pdf",
            "title": "Public Comments",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/08_2025/Written_Comments/Major_Taylor_Trail_Consolidation_Public_Comments_ALL.pdf",
            "title": "Public Comments",
        },
    ]


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False


@pytest.mark.parametrize("item", parsed_items)
def test_classification(item):
    assert item["classification"] == COMMISSION