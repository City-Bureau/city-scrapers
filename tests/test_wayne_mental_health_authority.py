from datetime import datetime
from operator import itemgetter
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import ADVISORY_COMMITTEE, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.wayne_mental_health_authority import WayneMentalHealthAuthoritySpider

test_response = file_response(
    join(dirname(__file__), "files", "wayne_mental_health_authority.html"),
    url=(
        "https://www.dwihn.org/about-us/dwmha-authority-board/board-directors-2017-committee-and-board-meeting-schedule/"  # noqa
    ),
)
test_doc_response = file_response(
    join(dirname(__file__), "files", "wayne_mental_health_authority_docs.html"),
    url="https://www.dwihn.org/about-us/dwmha-authority-board/board-meeting-documents/",
)
spider = WayneMentalHealthAuthoritySpider()

freezer = freeze_time("2019-08-29")
freezer.start()

spider._parse_documents(test_doc_response)
parsed_items = sorted([item for item in spider._parse_schedule(test_response)],
                      key=itemgetter("start"))

freezer.stop()


def test_count():
    assert len(parsed_items) == 74


def test_title():
    assert parsed_items[0]["title"] == "Recipient Rights Advisory Committee"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 1, 7, 13, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0][
        "id"] == "wayne_mental_health_authority/201901071300/x/recipient_rights_advisory_committee"


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == spider.location


def test_source():
    assert parsed_items[0][
        "source"
    ] == "https://www.dwihn.org/about-us/dwmha-authority-board/board-directors-2017-committee-and-board-meeting-schedule/"  # noqa


def test_links():
    assert parsed_items[0]["links"] == []
    assert parsed_items[11]["links"] == [{
        "href": "https://www.dwmha.com/index.php/download_file/1421/",
        "title": "Agenda"
    }, {
        "href": "https://www.dwmha.com/index.php/download_file/1427/",
        "title": "Resolution #1 - Provider Network"
    }, {
        "href": "https://www.dwmha.com/index.php/download_file/1428/",
        "title": "Resolution #2 - 298 Pilot Project"
    }, {
        "href": "https://www.dwmha.com/index.php/download_file/1429/",
        "title": "Resolution #3 - Funding to PIHP Milliman's Recommendation"
    }]


def test_classification():
    assert parsed_items[0]["classification"] == ADVISORY_COMMITTEE


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
