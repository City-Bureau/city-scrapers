from datetime import datetime
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import (
    ADVISORY_COMMITTEE,
    BOARD,
    CANCELLED,
    COMMITTEE,
    PASSED,
    TENTATIVE,
)
from city_scrapers_core.utils import file_response
from freezegun import freeze_time
from scrapy.settings import Settings

from city_scrapers.spiders.il_criminal_justice_information import (
    IlCriminalJusticeInformationSpider,
)

test_response = file_response(
    join(dirname(__file__), "files", "il_criminal_justice_information.html"),
    url="http://www.icjia.state.il.us/about/overview",
)
spider = IlCriminalJusticeInformationSpider()
spider.settings = Settings(values={"CITY_SCRAPERS_ARCHIVE": False})

freezer = freeze_time("2019-04-27")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 46


def test_title():
    assert parsed_items[0]["title"] == "Authority Board"
    assert parsed_items[-1]["title"] == "Strategic Opportunities Committee"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 12, 19, 10)
    assert parsed_items[6]["start"] == datetime(2018, 8, 22, 10, 45)
    assert parsed_items[21]["start"] == datetime(2018, 6, 21, 10, 0)


def test_end():
    assert parsed_items[0]["end"] is None
    assert parsed_items[6]["end"] == datetime(2018, 8, 22, 12)
    assert parsed_items[13]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"]
        == "il_criminal_justice_information/201912191000/x/authority_board"
    )


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE
    assert parsed_items[4]["status"] == CANCELLED
    assert parsed_items[-1]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Illinois Criminal Justice Information Authority",
        "address": "300 W Adams St, Suite 200,Chicago, IL 60606, 2nd Floor Building Conference Room",  # noqa
    }
    assert parsed_items[6]["location"] == {
        "address": "3000 South Dirksen Parkway, Springfield, IL 62703",
        "name": "Crowne Plaza Springfield",
    }


def test_source():
    assert parsed_items[0]["source"] == "http://www.icjia.state.il.us/about/overview"


def test_links():
    assert parsed_items[0]["links"] == []
    assert parsed_items[5]["links"] == [
        {
            "href": "http://www.icjia.state.il.us/assets/pdf/Meetings/12-11-18/Authority_Board_Meeting_Agenda_Memo_Materials_121118.pdf",  # noqa
            "title": "Materials",
        },
        {
            "href": "http://www.icjia.org/assets/pdf/Meetings/2019-04-24/AuthorityBoardMeeting%20Materials4.24.19.pdf",  # noqa
            "title": "Minutes",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == BOARD
    assert parsed_items[23]["classification"] == ADVISORY_COMMITTEE
    assert parsed_items[-1]["classification"] == COMMITTEE
