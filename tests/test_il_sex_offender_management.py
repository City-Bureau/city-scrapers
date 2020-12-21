from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.constants import BOARD, CANCELLED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.il_sex_offender_management import (
    IlSexOffenderManagementSpider,
)

test_pdf_response = file_response(
    join(dirname(__file__), "files", "il_sex_offender_management.pdf"),
    url=(
        "https://www2.illinois.gov/idoc/Documents/SOMB%20Meeting%20Agenda%202019%20August.pdf"  # noqa
    ),
    mode="rb",
)

test_response = file_response(
    join(dirname(__file__), "files", "il_sex_offender_management.html"),
    url="https://www2.illinois.gov/idoc/Pages/SexOffenderManagementBoard.aspx",
)
spider = IlSexOffenderManagementSpider()

freezer = freeze_time("2020-12-12")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

# make sure correct number of meetings are found
assert len(parsed_items) == 30

# make sure example pdf was able to be scraped by crawler from website
ref = "https://www2.illinois.gov/idoc/Documents/SOMB%20Meeting%20Agenda%202019%20August.pdf"  # noqa

# should be the second scraped meeting
assert ref in str(parsed_items[1])

# check if meeting object created from PDF is correct
parsed_items = [item for item in spider._parse_documents(test_pdf_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Management Board"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 8, 1, 10, 30)


def test_end():
    assert parsed_items[0]["end"] == datetime(2019, 8, 1, 12, 30)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == "See agenda to confirm details"


def test_id():
    id = "il_sex_offender_management/201908011030/x/management_board"
    assert parsed_items[0]["id"] == id


def test_status():
    assert parsed_items[0]["status"] == CANCELLED


def test_location():
    assert parsed_items[0]["location"] == {"name": "See meeting details", "address": ""}


def test_source():
    ref = "https://www2.illinois.gov/idoc/Pages/SexOffenderManagementBoard.aspx"
    assert parsed_items[0]["source"] == ref


def test_links():
    ref = "https://www2.illinois.gov/idoc/Documents/SOMB%20Meeting%20Agenda%202019%20August.pdf"  # noqa
    assert parsed_items[0]["links"] == [{"title": "Meeting Agenda", "href": ref}]


def test_classification():
    assert parsed_items[0]["classification"] == BOARD


def test_all_day():
    assert parsed_items[0]["all_day"] is False
