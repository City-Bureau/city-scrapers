from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.constants import BOARD, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.cook_electoral import CookElectoralSpider

home_response = file_response(
    join(dirname(__file__), "files", "cook_electoral_home.aspx.html"),
    url="https://aba.cookcountyclerk.com/boardmeetingsearch.aspx",
)
standard_response = file_response(
    join(dirname(__file__), "files", "cook_electoral_standard.aspx.html"),
    url="https://aba.cookcountyclerk.com/boardmeetingsearch.aspx",
)
special_response = file_response(
    join(dirname(__file__), "files", "cook_electoral_special.aspx.html"),
    url="https://aba.cookcountyclerk.com/boardmeetingsearch.aspx",
)
spider = CookElectoralSpider()

freezer = freeze_time("2020-01-01")
freezer.start()

parsed_standard = next(spider._parse_meeting(standard_response))
parsed_special = next(spider._parse_meeting(special_response))

freezer.stop()


def test_find_year_and_meetings():
    year, meeting_ids = spider._find_year_and_meetings(home_response)
    assert year == "2020"
    assert meeting_ids == [
        "562",
        "544",
        "545",
        "546",
        "563",
        "547",
        "548",
        "549",
        "550",
        "551",
        "552",
        "553",
        "554",
        "555",
        "556",
        "557",
        "558",
        "559",
        "560",
        "561",
    ]


def test_title():
    assert parsed_standard["title"] == "Board Of Commissioners Of Cook County Meeting"
    assert (
        parsed_special["title"]
        == "Special Board Of Commissioners Of Cook County Meeting"
    )


def test_description():
    assert parsed_standard["description"] == ""


def test_start():
    assert parsed_standard["start"] == datetime(2020, 1, 15, 13, 0)


def test_id():
    assert (
        parsed_standard["id"]
        == "cook_electoral/202001151300/x/board_of_commissioners_of_cook_county_meeting"
    )


def test_status():
    assert parsed_standard["status"] == TENTATIVE


def test_location():
    assert parsed_standard["location"] == {
        "name": "County Board Room, County Building",
        "address": "118 N. Clark Street, 5th Floor, Chicago IL",
    }


def test_source():
    assert (
        parsed_standard["source"]
        == "https://aba.cookcountyclerk.com/boardmeetingsearch.aspx"
    )


def test_links():
    assert parsed_standard["links"] == [
        {
            "title": "January 15, 2020 Consent Agenda",
            "href": "http://aba-clerk.s3-website-us-east-1.amazonaws.com/Agenda_pdf_011520_562.pdf",  # noqa
        },
        {
            "title": "January 15, 2020 Resolutions",
            "href": "http://aba-clerk.s3-website-us-east-1.amazonaws.com/Resolution_pdf_011520_562.pdf",  # noqa
        },
        {
            "title": "January 15, 2020 Consent Journal",
            "href": "http://aba-clerk.s3-website-us-east-1.amazonaws.com/Journal_pdf_011520_562.pdf",  # noqa
        },
    ]


def test_classification():
    assert parsed_standard["classification"] == BOARD
