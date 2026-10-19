from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.constants import COMMISSION, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_metro_planning import ChiMetroPlanningSpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_metro_planning.html"),
    url="https://www.cmap.illinois.gov/events",
)
spider = ChiMetroPlanningSpider()

freezer = freeze_time("2022-04-18")

freezer.start()

parsed_items = [item for item in spider.parse(test_response)]
# print(parsed_items)
freezer.stop()


def test_count():
    assert len(parsed_items) == 12


def test_title():
    assert parsed_items[0]["title"] == "Chicago Metropolitan Agency for Planning"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 4, 18, 11, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"]
        == "chi_license_appeal/201901161100/x/license_appeal_commission"
    )


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == spider.location


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://www.chicago.gov/city/en/depts/lac/supp_info/2009hearings.html"
    )


def test_links():
    assert parsed_items[0]["links"] == []


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


def test_all_day():
    assert parsed_items[0]["all_day"] is False
