from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.constants import ADVISORY_COMMITTEE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.il_corrections import IlCorrectionsSpider

test_pdf_response = file_response(
    join(dirname(__file__), "files", "il_corrections.pdf"),
    url="https://www2.illinois.gov/idoc/aboutus/advisoryboard/Documents/"
    "Agenda%20-%20November%204th-2019.pdf",
    mode="rb",
)

test_response = file_response(
    join(dirname(__file__), "files", "il_corrections.html"),
    url="https://www2.illinois.gov/idoc/aboutus/advisoryboard/Pages/default.aspx",
)

spider = IlCorrectionsSpider()

freezer = freeze_time("2020-12-08")
freezer.start()

parsed_dates = spider._parse_all_links(test_response)
test_generator = spider._meeting(test_pdf_response, "November 4, 2019")
test_meeting = next(test_generator)

freezer.stop()


def test_meeting_count():
    assert len(parsed_dates) == 41

def test_title():
    assert (
        test_meeting["title"] == "Adult Advisory Board / Women's Subcommittee Meeting"
    )


def test_description():
    assert test_meeting["description"] == ""


def test_start():
    assert test_meeting["start"] == datetime(2019, 11, 4, 10, 30)


def test_end():
    assert test_meeting["end"] == datetime(2019, 11, 4, 12, 0)


def test_id():
    assert (
        test_meeting["id"] == "il_corrections/201911041030/x/"
        "adult_advisory_board_women_s_subcommittee_meeting"
    )


def test_status():
    assert test_meeting["status"] == "passed"


def test_location():
    assert test_meeting["location"] == {
        "address": "1096 1350th St, Lincoln, IL 62656",
        "name": "Logan Correctional Center",
    }


def test_source():
    assert (
        test_meeting["source"]
        == "https://www2.illinois.gov/idoc/aboutus/advisoryboard/Documents/"
        "Agenda%20-%20November%204th-2019.pdf"
    )


def test_links():
    assert test_meeting["links"] == [
        {
            "href": "https://www2.illinois.gov/idoc/aboutus/advisoryboard/"
            "Documents/Agenda%20-%20November%204th-2019.pdf",
            "title": "Agenda",
        }
    ]


def test_classification():
    assert test_meeting["classification"] == ADVISORY_COMMITTEE


def test_all_day():
    assert test_meeting["all_day"] is False
