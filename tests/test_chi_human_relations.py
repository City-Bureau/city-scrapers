from datetime import datetime
from operator import itemgetter
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import COMMISSION, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_human_relations import ChiHumanRelationsSpider

test_pdf_response = file_response(
    join(dirname(__file__), "files", "chi_human_relations.pdf"),
    url=(
        "https://www.chicago.gov/content/dam/city/depts/cchr/BoardMeetings/2019CCHRBoardMeetingSchedule.pdf"  # noqa
    ),
    mode="rb",
)
test_response = file_response(
    join(dirname(__file__), "files", "chi_human_relations.html"),
    url="https://www.chicago.gov/city/en/depts/cchr/supp_info/BoardMeetingInformation.html",  # noqa
)
spider = ChiHumanRelationsSpider()

freezer = freeze_time("2019-07-20")
freezer.start()

spider._parse_schedule_pdf(test_pdf_response)
parsed_items = sorted(
    [item for item in spider._parse_documents(test_response)], key=itemgetter("start"),
)

freezer.stop()


def test_count():
    assert len(parsed_items) == 5


def test_title():
    assert parsed_items[0]["title"] == "Board of Commissioners"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 1, 10, 15, 30)


def test_end():
    assert parsed_items[0]["end"] == datetime(2019, 1, 10, 17)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == "See agenda to confirm details"


def test_id():
    assert (
        parsed_items[0]["id"]
        == "chi_human_relations/201901101530/x/board_of_commissioners"
    )


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == spider.location


def test_source():
    assert (
        parsed_items[0]["source"] == "https://www.chicago.gov/city/en/depts/cchr.html"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/cchr/BoardMeetings/BoardAgenda/2019JanuaryBoardAgenda.pdf",  # noqa
            "title": "Agenda",
        },
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/cchr/BoardMeetings/BoardMinutes/2019JanuaryMinutesCCHR%20Board.pdf",  # noqa
            "title": "Minutes",
        },
    ]
    assert parsed_items[-1]["links"] == []


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


def test_all_day():
    assert parsed_items[0]["all_day"] is False
