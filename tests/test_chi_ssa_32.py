from os.path import dirname, join

from city_scrapers_core.constants import COMMISSION, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ssa_32 import ChiSsa32Spider

test_response = file_response(
    join(dirname(__file__), "files", "chi_ssa_32.json"),
    url="https://auburngresham.wixsite.com/ssa32/calendar",
)

spider = ChiSsa32Spider()

freezer = freeze_time("2019-11-09")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "SSA #69 Commissioners"


def test_description():
    assert parsed_items[0]["description"] == (
        " SSA #69 Commissioners Meeting:\n"
        " Corresponding Dates: \n"
        "February 12, 2019; July 23, 2019; and  November 12, 2019\n"
        " Location: 7901 S. Racine, Chicago, IL 60620\n"
        " Time: 8:30 am to 10:00 am"
    )


def test_start():
    assert str(parsed_items[0]["start"]) == "2019-11-12 09:30:00"


def test_end():
    assert str(parsed_items[0]["end"]) == "2019-11-12 11:00:00"


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == "chi_ssa_32/201911120930/x/ssa_69_commissioners"


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "",
        "address": "7901 S Racine Ave, Chicago, IL 60620, USA",
    }


def test_source():
    url_p = "https://www.google.com/calendar/event?eid="
    url_s1 = "MWQxMDU2cDhmZmVjZjBmN2JqZHRuMmtncDEgZ2FnZGNjaGljYWdvQG0&ctz=GMT-05:00"
    assert parsed_items[0]["source"] == url_p + url_s1


def test_links():
    assert parsed_items[0]["links"] == []


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


def test_all_day():
    assert parsed_items[0]["all_day"] is False
