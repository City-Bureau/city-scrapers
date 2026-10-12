from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import (
    ADVISORY_COMMITTEE,
    BOARD,
    COMMISSION,
    FORUM,
    PASSED,
    TENTATIVE,
)
from city_scrapers_core.utils import file_response
from freezegun import freeze_time
from scrapy.http import HtmlResponse

from city_scrapers.spiders.il_commerce import IlCommerceSpider

DEFAULT_LOCATION = {
    "name": "Illinois Commerce Commission",
    "address": "527 East Capitol Avenue, Springfield, IL 62701",
}

LIST_URL = "https://www.icc.illinois.gov/meetings?dts=32&scm=True&sps=True&sh=True&sjc=True&ssh=False&smceb=True"  # noqa
MEETING_URL = "https://www.icc.illinois.gov/meetings/meeting/"


@pytest.fixture(scope="module")
def spider():
    return IlCommerceSpider()


def _parse_detail(spider, file_name, path):
    response = file_response(
        join(dirname(__file__), "files", file_name), url=MEETING_URL + path
    )
    with freeze_time("2026-10-09"):
        return list(spider._parse_event_page(response))


@pytest.fixture(scope="module")
def parsed_requests(spider):
    response = file_response(
        join(dirname(__file__), "files", "il_commerce_list.html"), url=LIST_URL
    )
    with freeze_time("2026-10-09"):
        return list(spider.parse(response))


@pytest.fixture(scope="module")
def parsed_item(spider):
    items = _parse_detail(spider, "il_commerce.html", "commission-meeting/21716")
    return items[0]


@pytest.fixture(scope="module")
def hearing_item(spider):
    return _parse_detail(spider, "il_commerce_hearing.html", "hearing/151045")[0]


@pytest.fixture(scope="module")
def public_forum_item(spider):
    return _parse_detail(spider, "il_commerce_public_forum.html", "hearing/151131")[0]


def _detail_page(heading, location="", description=""):
    """
    A detail page with the structure of the ICC's own pages, for location and title
    variants that differ from the saved pages only in a few lines.
    """
    body = """
        <div class="container soi-container soi-icc-container"><div class="row">
        <div class="col-12">
            <h2>{}</h2>
            <h3 class="mt-4">September 14, 2026 at 10:00 AM</h3>
            <p>{}</p>
            <div class="row mt-4"><div class="col-12">{}</div></div>
        </div></div></div>
    """.format(heading, description, location)
    return HtmlResponse(url=MEETING_URL + "hearing/1", body=body.encode())


ICC_HEADING = 'Illinois Commerce Commission <span class="d-block">{}</span>'
VARIANT_PAGES = {
    "board": _detail_page(
        'Motor Carrier Employee Board <span class="d-block">'
        "Motor Carrier Employee Board Meeting</span>",
        "<h4>Illinois Commerce Commission</h4><p>527 East Capitol Avenue<br>"
        "Transportation Information Center, First Floor, Leland Building<br>"
        "<span>Springfield, Illinois 62701</span></p>",
    ),
    "committee": _detail_page(
        ICC_HEADING.format("Underground Utility Damage Prevention Advisory Committee"),
        "<h4>Video Conference - ICC Springfield &amp; Offices of JULIE, Inc</h4>",
    ),
    "multi_line": _detail_page(
        ICC_HEADING.format("Evidentiary for 26-0364"),
        "<h4>Illinois Commerce Commission</h4><p>160 North LaSalle Street<br>"
        "State of Illinois Building<br>Eighth Floor<br>Main Hearing Room<br>"
        "<span>Chicago, IL 60601</span></p>",
    ),
    "webex": _detail_page(
        ICC_HEADING.format("Evidentiary for 26-0007"),
        "<h4>Illinois Commerce Commission</h4><p>527 East Capitol Avenue<br>"
        "Webex<br><span>Springfield, IL 62701</span></p>",
    ),
    "policy_session": _detail_page(
        ICC_HEADING.format("Summer Preparedness Policy Session")
        + '<span class="d-block">Summer Preparedness Policy Session for '
        "06/11/2026 9:00 AM</span>",
        "<h4>Illinois Commerce Commission</h4>",
    ),
    "webinar": _detail_page(
        ICC_HEADING.format("Public Forum for HHG Tariff Webinar"),
        "<h4>Illinois Commerce Commission</h4>",
        "HHG Tariff Webinar<br><br>This Webinar will take place remotely via WebEx.",
    ),
    "case_schedule": _detail_page(
        ICC_HEADING.format("Hearing for T26-0001"), description="Status Hearing"
    ),
}


@pytest.fixture(scope="module")
def variant_items(spider):
    with freeze_time("2026-10-09"):
        return {
            name: list(spider._parse_event_page(response))[0]
            for name, response in VARIANT_PAGES.items()
        }


@pytest.fixture(scope="module")
def start_request(spider):
    with freeze_time("2026-10-09"):
        return list(spider.start_requests())


@pytest.fixture(scope="module")
def month_list_body():
    with open(join(dirname(__file__), "files", "il_commerce_list.html"), "rb") as f:
        return f.read()


def _parse_month(spider, body, month):
    response = HtmlResponse(url=LIST_URL, body=body)
    with freeze_time("2026-10-09"):
        return list(spider.parse(response, month=month))


def test_count(parsed_requests):
    assert len(parsed_requests) == 123
    for request in parsed_requests:
        assert "/meetings/meeting/" in request.url


def test_skips_cancelled_listing_replaced_by_active_one(parsed_requests):
    # "Status for 26-0158" on June 4, 2026 11:00 AM is listed twice: the old
    # listing is marked cancelled and the new one is active
    urls = [request.url for request in parsed_requests]
    assert any("hearing/151071" in url for url in urls)
    assert not any("hearing/150977" in url for url in urls)


def test_keeps_cancelled_listing_without_replacement(parsed_requests):
    # Cancelled on the calendar with no other listing at the same title and time
    assert any("hearing/150945" in request.url for request in parsed_requests)


def test_title(parsed_item):
    assert parsed_item["title"] == "Regular Open Meeting"


def test_description(parsed_item):
    assert parsed_item["description"] == ""


def test_start(parsed_item):
    assert parsed_item["start"] == datetime(2026, 10, 15, 11, 30)


def test_end(parsed_item):
    assert parsed_item["end"] is None


def test_time_notes(parsed_item):
    assert parsed_item["time_notes"] == ""


def test_id(parsed_item):
    assert parsed_item["id"] == "il_commerce/202610151130/x/regular_open_meeting"


def test_status(parsed_item):
    assert parsed_item["status"] == TENTATIVE


def test_location(parsed_item):
    assert parsed_item["location"] == {
        "name": "Hearing Room A, First Floor, Leland Building",
        "address": "527 East Capitol Avenue, Springfield, IL 62701",
    }


def test_source(parsed_item):
    assert parsed_item["source"] == MEETING_URL + "commission-meeting/21716"


def test_links(parsed_item):
    assert parsed_item["links"] == [
        {
            "href": "https://www.icc.illinois.gov/attachments/print/coverletter?agid=22192",  # noqa
            "title": "Transportation Cover Letter",
        },
        {
            "href": "https://www.icc.illinois.gov/attachments/print/agendareport?agid=22192",  # noqa
            "title": "Bench Agenda",
        },
    ]


def test_classification(parsed_item):
    assert parsed_item["classification"] == COMMISSION


def test_all_day(parsed_item):
    assert parsed_item["all_day"] is False


def test_hearing(hearing_item):
    assert hearing_item["title"] == "Status for 26-0331"
    assert hearing_item["start"] == datetime(2026, 10, 13, 10, 0)
    assert hearing_item["description"].startswith(
        "MidAmerican Energy Company Proposed general increase electric rates"
    )
    assert hearing_item["classification"] == COMMISSION
    assert hearing_item["location"] == DEFAULT_LOCATION
    assert hearing_item["links"] == []


def test_public_forum_venue_from_description(public_forum_item):
    assert public_forum_item["title"] == "Public Forum for 26-0065"
    assert public_forum_item["classification"] == FORUM
    assert public_forum_item["start"] == datetime(2026, 7, 15, 19, 0)
    assert public_forum_item["status"] == PASSED
    assert public_forum_item["location"] == {
        "name": "Roosevelt University, 10th Floor Library",
        "address": "430 S. Michigan Ave., Chicago, IL 60605",
    }


def test_board(variant_items):
    item = variant_items["board"]
    assert item["title"] == "Motor Carrier Employee Board"
    assert item["classification"] == BOARD
    assert item["location"] == {
        "name": "Transportation Information Center, First Floor, Leland Building",
        "address": "527 East Capitol Avenue, Springfield, IL 62701",
    }


def test_committee_video_conference(variant_items):
    item = variant_items["committee"]
    assert item["title"] == "Underground Utility Damage Prevention Advisory Committee"
    assert item["classification"] == ADVISORY_COMMITTEE
    assert item["location"] == {
        "name": "Video Conference - ICC Springfield & Offices of JULIE, Inc",
        "address": "",
    }


def test_multi_line_location(variant_items):
    assert variant_items["multi_line"]["location"] == {
        "name": "State of Illinois Building, Eighth Floor, Main Hearing Room",
        "address": "160 North LaSalle Street, Chicago, IL 60601",
    }


def test_webex_location(variant_items):
    assert variant_items["webex"]["location"] == {"name": "Webex", "address": ""}


def test_policy_session_title(variant_items):
    # The heading has a second span repeating the name with the date
    item = variant_items["policy_session"]
    assert item["title"] == "Summer Preparedness Policy Session"
    assert item["classification"] == COMMISSION


def test_webinar_forum_location(variant_items):
    item = variant_items["webinar"]
    assert item["classification"] == FORUM
    assert item["location"] == {"name": "Webex", "address": ""}


def test_case_schedule_without_location(variant_items):
    item = variant_items["case_schedule"]
    assert item["title"] == "Hearing for T26-0001"
    assert item["location"] == DEFAULT_LOCATION


def test_unexpected_location_format_logs(spider, caplog):
    response = _detail_page(
        ICC_HEADING.format("Hearing for 26-0001"),
        "<h4>Illinois Commerce Commission</h4><p>Springfield, IL 62701</p>",
    )
    with caplog.at_level("WARNING"):
        item = list(spider._parse_event_page(response))[0]
    assert item["location"] == {
        "name": "Illinois Commerce Commission",
        "address": "Springfield, IL 62701",
    }
    assert "Unexpected location format" in caplog.text


def test_start_request_begins_one_year_back(start_request):
    assert len(start_request) == 1
    request = start_request[0]
    # 2025-10-01 00:00 in .NET ticks, the format of the calendar's own links
    assert "bd=638948736000000000" in request.url
    assert "dts=32" in request.url
    assert request.cb_kwargs == {"month": datetime(2025, 10, 1)}


def test_month_requests_next_month(spider, month_list_body):
    requests = _parse_month(spider, month_list_body, datetime(2026, 6, 1))
    assert len(requests) == 124
    next_month = requests[-1]
    assert next_month.cb_kwargs == {"month": datetime(2026, 7, 1)}
    # 2026-07-01 00:00 in .NET ticks
    assert "bd=639184608000000000" in next_month.url


def test_empty_future_month_stops_paging(spider, caplog):
    with caplog.at_level("WARNING"):
        assert _parse_month(spider, b"<html></html>", datetime(2027, 4, 1)) == []
    assert caplog.text == ""


def test_empty_past_month_logs_and_continues(spider, caplog):
    with caplog.at_level("WARNING"):
        requests = _parse_month(spider, b"<html></html>", datetime(2026, 9, 1))
    assert [r.cb_kwargs for r in requests] == [{"month": datetime(2026, 10, 1)}]
    assert "No meetings found" in caplog.text


def test_undated_page_logs_and_skips(spider, caplog):
    response = HtmlResponse(
        url=MEETING_URL + "hearing/1",
        body=b'<div class="soi-icc-container"><div class="row"><div class="col-12">'
        b"<h2>Illinois Commerce Commission</h2></div></div></div>",
    )
    with caplog.at_level("WARNING"):
        assert list(spider._parse_event_page(response)) == []
    assert "Could not parse start time" in caplog.text
