from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.constants import ADVISORY_COMMITTEE, BOARD, COMMITTEE, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.cook_county import CookCountySpider

test_response = file_response(
    join(dirname(__file__), "files", "cook_county_event.html"),
    url="https://www.cookcountyil.gov/event/public-hearing-zoning-board-appeals-2",
)
spider = CookCountySpider()

freezer = freeze_time("2019-10-16")
freezer.start()
item = spider._parse_event(test_response)
freezer.stop()


def test_title():
    assert item["title"] == "Public Hearing - Zoning Board of Appeals"


def test_start():
    assert item["start"] == datetime(2019, 10, 2, 13)


def test_end():
    assert item["end"] == datetime(2019, 10, 2, 15)


def test_time_notes():
    assert item["time_notes"] == ""


def test_id():
    assert (
        item["id"]
        == "cook_county/201910021300/x/public_hearing_zoning_board_of_appeals"
    )


def test_all_day():
    assert item["all_day"] is False


def test_classification():
    assert spider._parse_classification("Board of Commissioners") == BOARD
    assert (
        spider._parse_classification("Economic Development Advisory Committee")
        == ADVISORY_COMMITTEE
    )
    assert spider._parse_classification("Finance Committee") == COMMITTEE
    assert (
        spider._parse_classification("Finance Subcommittee on Litigation") == COMMITTEE
    )
    assert (
        spider._parse_classification("Finance Subcommittee on Workers Compensation")
        == COMMITTEE
    )
    assert (
        spider._parse_classification(
            "Committee of Suburban Cook County Commissioners - PACE"
        )
        == COMMITTEE
    )
    assert spider._parse_classification("Rules & Administration Committee") == COMMITTEE
    assert spider._parse_classification("Roads & Bridges Committee") == COMMITTEE
    assert spider._parse_classification("Zoning & Building Committee") == COMMITTEE
    assert (
        spider._parse_classification("Justice Advisory Council") == ADVISORY_COMMITTEE
    )
    assert spider._parse_classification("JAC Council Meeting") == ADVISORY_COMMITTEE


def test_status():
    assert item["status"] == PASSED


def test_location():
    assert item["location"] == {
        "name": "",
        "address": "69 W. Washington Street Chicago , IL  60602",
    }


def test_sources():
    assert (
        item["source"]
        == "https://www.cookcountyil.gov/event/public-hearing-zoning-board-appeals-2"
    )


def test_description():
    assert item["description"] == (
        "A Public Hearing has been scheduled for the Cook County Zoning Board of "
        "Appeals on      Wednesday, October 2, 2019 at 1:00PM at "
        "69 W. Washington - 22nd Floor Conference Room, Chicago, Illinois 60602 "
        "Public Hearing"
    )


def test_links():
    assert item["links"] == [
        {
            "href": "https://www.cookcountyil.gov/sites/default/files/zba-agenda_10.2.19_-_final.pdf",  # noqa
            "title": "ZBA 10-2-2019 Agenda",
        }
    ]
