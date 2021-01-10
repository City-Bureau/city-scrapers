from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ssa_31 import ChiSsa31Spider

test_response = file_response(
    join(dirname(__file__), "files", "chi_ssa_31.html"),
    url="http://ravenswoodchicago.org/ssa-31-commission-meetings/",
)
spider = ChiSsa31Spider()

freezer = freeze_time("2021-01-10")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Minutes TBD"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2021, 1, 21, 14, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_id():
    assert parsed_items[0]["id"] == "chi_ssa_31/202101211400/x/minutes_tbd"


def test_status():
    assert parsed_items[0]["status"] == "tentative"


def test_location():
    assert parsed_items[0]["location"] == {"name": "Confirm with agency", "address": ""}


def test_source():
    assert (
        parsed_items[0]["source"]
        == "http://ravenswoodchicago.org/" + "ssa-31-commission-meetings/"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": (
                "https://drive.google.com/"
                + "file/d/1Vwr0ZP5cnlBVA04Dcn9B7Z1ByCJNib09/view?usp=sharing"
            ),
            "title": "Agenda",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION
