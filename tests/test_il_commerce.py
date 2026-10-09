from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import (
    ADVISORY_COMMITTEE,
    BOARD,
    COMMISSION,
    TENTATIVE,
)
from city_scrapers_core.utils import file_response
from freezegun import freeze_time
from scrapy.http import HtmlResponse

from city_scrapers.spiders.il_commerce import IlCommerceSpider

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
def committee_item(spider):
    return _parse_detail(
        spider, "il_commerce_committee.html", "julie-committee-meeting/223017"
    )[0]


@pytest.fixture(scope="module")
def board_item(spider):
    return _parse_detail(
        spider, "il_commerce_board.html", "motor-carrier-employee-board/21731"
    )[0]


def test_count(parsed_requests):
    assert len(parsed_requests) == 96
    for request in parsed_requests:
        assert "/meetings/meeting/" in request.url


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
        "address": "527 East Capitol Avenue Springfield, Illinois 62701",
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
    assert hearing_item["location"] == {
        "name": "Illinois Commerce Commission",
        "address": "",
    }
    assert hearing_item["links"] == []


def test_committee(committee_item):
    assert (
        committee_item["title"]
        == "Underground Utility Damage Prevention Advisory Committee"
    )
    assert committee_item["start"] == datetime(2026, 10, 21, 10, 0)
    assert committee_item["classification"] == ADVISORY_COMMITTEE
    assert committee_item["location"] == {
        "name": "Video Conference - ICC Springfield & Offices of JULIE, Inc",
        "address": "",
    }


def test_board(board_item):
    assert board_item["title"] == "Motor Carrier Employee Board"
    assert board_item["start"] == datetime(2026, 10, 20, 14, 0)
    assert board_item["classification"] == BOARD
    assert board_item["location"] == {
        "name": "Transportation Information Center, First Floor, Leland Building",
        "address": "527 East Capitol Avenue Springfield, Illinois 62701",
    }


def test_undated_page_logs_and_skips(spider, caplog):
    response = HtmlResponse(
        url=MEETING_URL + "hearing/1",
        body=b'<div class="soi-icc-container"><div class="row"><div class="col-12">'
        b"<h2>Illinois Commerce Commission</h2></div></div></div>",
    )
    with caplog.at_level("WARNING"):
        assert list(spider._parse_event_page(response)) == []
    assert "Could not parse start time" in caplog.text
