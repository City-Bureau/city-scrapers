from datetime import datetime
from operator import itemgetter
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import COMMISSION, COMMITTEE, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.il_environmental_justice import IlEnvironmentalJusticeSpider

test_response = file_response(
    join(dirname(__file__), "files", "il_environmental_justice.html"),
    url="https://www2.illinois.gov/epa/topics/environmental-justice/commission/Pages/meetings.aspx",  # noqa
)
spider = IlEnvironmentalJusticeSpider()

freezer = freeze_time("2019-07-19")
freezer.start()

parsed_items = sorted(
    [item for item in spider.parse(test_response)], key=itemgetter("start")
)

freezer.stop()


def test_count():
    assert len(parsed_items) == 43


def test_title():
    assert parsed_items[20]["title"] == "Brownfields Redevelopment Subcommittee"
    assert parsed_items[-1]["title"] == "Commission"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[-1]["start"] == datetime(2019, 6, 4, 9, 30)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == "See agenda to confirm details"


def test_id():
    assert (
        parsed_items[-1]["id"] == "il_environmental_justice/201906040930/x/commission"
    )


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == spider.location


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://www2.illinois.gov/epa/topics/environmental-justice/commission/Pages/meetings.aspx"  # noqa
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://www2.illinois.gov/epa/Documents/iepa/environmental-justice/agenda/2013/agenda-08142013.pdf",  # noqa
            "title": "Agenda",
        },
        {
            "href": "https://www2.illinois.gov/epa/Documents/iepa/environmental-justice/minutes/2013/minutes-08142013.pdf",  # noqa
            "title": "Minutes",
        },
    ]
    assert parsed_items[-1]["links"] == [
        {
            "href": "https://www2.illinois.gov/epa/topics/environmental-justice/commission/Documents/EJ_Commission_Invite_2nd_2019.pdf",  # noqa
            "title": "Meeting Notice",
        },
        {
            "href": "https://www2.illinois.gov/epa/topics/environmental-justice/commission/Documents/Agenda_for_June_4_2019_Commission_on_Environmental_Justice.pdf",  # noqa
            "title": "Agenda",
        },
        {
            "href": "https://www2.illinois.gov/epa/topics/environmental-justice/commission/Documents/EJ%20Commission%20meeting%20-%202nd%20Quarter-20190604%201451-1.mp4",  # noqa
            "title": "Audio Minutes",
        },
    ]


def test_links_length():
    # No individual item's link list should be empty or have more than 3 links
    link_lengths = [len(item["links"]) for item in parsed_items]
    assert min(link_lengths) == 1
    assert max(link_lengths) == 3


def test_classification():
    assert parsed_items[-1]["classification"] == COMMISSION
    assert parsed_items[20]["classification"] == COMMITTEE


def test_all_day():
    assert parsed_items[0]["all_day"] is False
