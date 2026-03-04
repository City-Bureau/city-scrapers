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


def _sorted_by_start(items):
    return sorted(items, key=lambda x: x["start"])


def _normalize_chicago_url(url: str) -> str:
    return url.replace(
        "https://www.chicago.gov/city/en/",
        "https://www.chicago.gov/content/city/en/",
    )


def _starts_in_year(items, year: int):
    return [i for i in items if i["start"].year == year]


@pytest.fixture(scope="module")
def spider_results():
    spider = ChiPlanCommissionSpider()
    spider.settings = Settings(values={"CITY_SCRAPERS_ARCHIVE": False})

    test_response = file_response(
        join(dirname(__file__), "files", "chi_plan_commission.html"),
        url="https://www.chicago.gov/city/en/depts/dcd/chicago-plan-commission/meetings--agendas---video-archives.html?wcmmode=disabled",  # noqa
    )
    test_detail_response = file_response(
        join(dirname(__file__), "files", "chi_plan_commission_detail.html"),
        url="https://www.chicago.gov/city/en/depts/dcd/supp_info/chicago_plan_commission/August_2025_Plan_Commission_Hearing.html",  # noqa
    )

    with freeze_time("2026-03-02"):
        parse_results = list(spider.parse(test_response))

        parsed_items = [x for x in parse_results if isinstance(x, Meeting)]
        parsed_requests = [x for x in parse_results if isinstance(x, Request)]

        parsed_detail = list(
            spider._parse_detail(test_detail_response, start=datetime(2025, 8, 21, 10))
        )[0]

    return {
        "spider": spider,
        "test_response": test_response,
        "parse_results": parse_results,
        "parsed_items": parsed_items,
        "parsed_requests": parsed_requests,
        "parsed_detail": parsed_detail,
    }


def _get_first_2026_item(parsed_items):
    items_2026 = _sorted_by_start(_starts_in_year(parsed_items, 2026))
    assert items_2026
    return items_2026[0]


def test_main_page_outputs_include_items_and_requests(spider_results):
    parsed_items = spider_results["parsed_items"]
    parsed_requests = spider_results["parsed_requests"]
    parse_results = spider_results["parse_results"]

    assert len(parsed_items) > 0
    assert len(parsed_requests) > 0
    assert len(parse_results) == len(parsed_items) + len(parsed_requests)


def test_2026_meeting_items_are_apr_through_dec(spider_results):
    parsed_items = spider_results["parsed_items"]

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
    items_2026 = _sorted_by_start(_starts_in_year(parsed_items, 2026))
    assert [i["start"] for i in items_2026] == expected_starts


def test_detail_requests_include_expected_months(spider_results):
    parsed_requests = spider_results["parsed_requests"]
    urls = sorted({_normalize_chicago_url(r.url) for r in parsed_requests})

    expected_subset = sorted(
        [
            "https://www.chicago.gov/content/city/en/depts/dcd/supp_info/chicago_plan_commission/January_2026_Plan_Commission_Hearing.html",  # noqa
            "https://www.chicago.gov/content/city/en/depts/dcd/supp_info/chicago_plan_commission/February_2026_Plan_Commission_Hearing.html",  # noqa
            "https://www.chicago.gov/content/city/en/depts/dcd/supp_info/chicago_plan_commission/March_2026_Plan_Commission_Hearing.html",  # noqa
            "https://www.chicago.gov/content/city/en/depts/dcd/supp_info/chicago_plan_commission/March_2025_Plan_Commission_Hearing.html",  # noqa
            "https://www.chicago.gov/content/city/en/depts/dcd/supp_info/chicago_plan_commission/April_2025_Plan_Commission_Hearing.html",  # noqa
            "https://www.chicago.gov/content/city/en/depts/dcd/supp_info/chicago_plan_commission/May_2025_Plan_Commission_Hearing.html",  # noqa
            "https://www.chicago.gov/content/city/en/depts/dcd/supp_info/chicago_plan_commission/June_2025_Plan_Commission_Hearing.html",  # noqa
            "https://www.chicago.gov/content/city/en/depts/dcd/supp_info/chicago_plan_commission/July_2025_Plan_Commission_Hearing.html",  # noqa
            "https://www.chicago.gov/content/city/en/depts/dcd/supp_info/chicago_plan_commission/August_2025_Plan_Commission_Hearing.html",  # noqa
            "https://www.chicago.gov/content/city/en/depts/dcd/supp_info/chicago_plan_commission/September_2025_Plan_Commission_Hearing.html",  # noqa
            "https://www.chicago.gov/content/city/en/depts/dcd/supp_info/chicago_plan_commission/October_2025_Plan_Commission_Hearing.html",  # noqa
            "https://www.chicago.gov/content/city/en/depts/dcd/supp_info/chicago_plan_commission/November_2025_Plan_Commission_Hearing.html",  # noqa
            "https://www.chicago.gov/content/city/en/depts/dcd/supp_info/chicago_plan_commission/December_2025_Plan_Commission_Hearing.html",  # noqa
        ]
    )

    missing = [u for u in expected_subset if u not in urls]
    assert missing == []


def test_main_page_meetings_have_no_links(spider_results):
    for item in spider_results["parsed_items"]:
        assert item["links"] == []


def test_unique_id_for_meeting_items(spider_results):
    parsed_items = spider_results["parsed_items"]
    assert len(set([item["id"] for item in parsed_items])) == 9


def test_title_description_defaults(spider_results):
    parsed_items = spider_results["parsed_items"]
    item = _get_first_2026_item(parsed_items)
    assert item["title"] == "Commission"
    assert item["description"] == ""


def test_start(spider_results):
    parsed_items = spider_results["parsed_items"]
    parsed_detail = spider_results["parsed_detail"]

    items_2026 = _sorted_by_start(_starts_in_year(parsed_items, 2026))
    assert items_2026[0]["start"] == datetime(2026, 4, 16, 10, 0)

    assert parsed_detail["start"] == datetime(2025, 8, 21, 10, 0)


def test_end_is_none_for_all_meetings(spider_results):
    parsed_items = spider_results["parsed_items"]
    parsed_detail = spider_results["parsed_detail"]

    for item in parsed_items:
        assert item["end"] is None

    assert parsed_detail["end"] is None


def test_id_format_matches_start_datetime(spider_results):
    for item in spider_results["parsed_items"]:
        dt_str = item["start"].strftime("%Y%m%d%H%M")
        assert f"/{dt_str}/" in item["id"]


def test_status(spider_results):
    parsed_items = spider_results["parsed_items"]
    item = _get_first_2026_item(parsed_items)
    assert item["status"] == TENTATIVE


def test_location(spider_results):
    spider = spider_results["spider"]
    parsed_items = spider_results["parsed_items"]
    item = _get_first_2026_item(parsed_items)
    assert item["location"] == spider.location


def test_source(spider_results):
    test_response = spider_results["test_response"]
    parsed_items = spider_results["parsed_items"]
    item = _get_first_2026_item(parsed_items)
    assert item["source"] == test_response.url


def test_links(spider_results):
    parsed_items = spider_results["parsed_items"]
    parsed_detail = spider_results["parsed_detail"]

    item = _get_first_2026_item(parsed_items)
    assert item["links"] == []

    assert parsed_detail["links"] == [
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/08_2025/7.31.2025_DRAFT_August_2025_PUBLIC_NOTICE.pdf",  # noqa
            "title": "Public Notice",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/08_2025/DRAFT_AUGUST_21_2025_Agenda.pdf",  # noqa
            "title": "Agenda",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/08_2025/Chicago_Plan_Commission_August_2025.pdf",  # noqa
            "title": "Map",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/08_2025/Chicago_Plan_Commission_August_2025_with_Planning_Regions.pdf",  # noqa
            "title": "Planning Region Map",
        },
        {
            "href": "https://youtube.com/watch?v=lhBdveUNxJQ",
            "title": "Video",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/08_2025/LPO_APP_790_6402-6420_S_Stony_Island_Ave.pdf",  # noqa
            "title": "LPO Application",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/08_2025/6402-20_Stony_Island_Full_Packet_AS_FILED.pdf",  # noqa
            "title": "PD Application",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/08_2025/20250821_6402-6420_S_Stony_Island_CPC_Presentation_R2.pdf",  # noqa
            "title": "Presentation",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/08_2025/Written_Comments/6400_S_Stony_Island_Public_Comments_Against.pdf",  # noqa
            "title": "Public Comments - Against",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/08_2025/Written_Comments/6400_S_Stony_Island_Public_Comments_Support.pdf",  # noqa
            "title": "Public Comments - Support",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/08_2025/2025-07-29_FILED_Lakefront_Protection_Application_795.pdf",  # noqa
            "title": "LPO Application",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/08_2025/2025.08.21_Metra_59th_&_60th_St_LPO_CPC_Presentation.pdf",  # noqa
            "title": "Presentation",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/08_2025/Written_Comments/59th_Metra_Public_Comments_ALL.pdf",  # noqa
            "title": "Public Comments",
        },
        {
            "href": "https://www.chicago.gov/city/en/depts/dcd/supp_info/major-taylor-trail-framework-plan.html",  # noqa
            "title": "https://www.chicago.gov/city/en/depts/dcd/supp_info/major-taylor-trail-framework-plan.html",  # noqa
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/08_2025/2025_08_21_Major_Taylor_Trail%20Planning_CPC.pdf",  # noqa
            "title": "Presentation",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/08_2025/Written_Comments/Major_Taylor_Trail_Framework_Public_Comments_ALL.pdf",  # noqa
            "title": "Public Comments",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/zlup/Planning_and_Policy/Agendas/cpc_materials/08_2025/Written_Comments/Major_Taylor_Trail_Consolidation_Public_Comments_ALL.pdf",  # noqa
            "title": "Public Comments",
        },
    ]


@pytest.mark.parametrize("item", ["parsed_items"])
def test_all_day(spider_results, item):
    for meeting in spider_results[item]:
        assert meeting["all_day"] is False


@pytest.mark.parametrize("item", ["parsed_items"])
def test_classification(spider_results, item):
    for meeting in spider_results[item]:
        assert meeting["classification"] == COMMISSION
