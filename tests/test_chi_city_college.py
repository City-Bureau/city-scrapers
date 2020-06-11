from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.constants import BOARD, COMMITTEE, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_city_college import ChiCityCollegeSpider

freezer = freeze_time("2018-01-12")
freezer.start()
test_response = file_response(
    join(dirname(__file__), "files", "chi_city_college.html"),
    url="http://www.ccc.edu/events/Pages/March-2019-Board-and-Committee-Meetings.aspx",
)
spider = ChiCityCollegeSpider()
parsed_items = [item for item in spider.parse_event_page(test_response)]
freezer.stop()


def test_title():
    assert (
        parsed_items[0]["title"] == "Committee on Finance and Administrative Services"
    )
    assert parsed_items[1]["title"] == "Board of Trustees"


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 2, 7, 12, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_id():
    assert (
        parsed_items[0]["id"]
        == "chi_city_college/201902071200/x/committee_on_finance_and_administrative_services"  # noqa
    )


def test_all_day():
    assert parsed_items[0]["all_day"] is False


def test_classification():
    assert parsed_items[0]["classification"] == COMMITTEE
    assert parsed_items[1]["classification"] == BOARD


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Harold Washington College",
        "address": "30 East Lake Street 11th Floor Chicago, IL 60601",
    }


def test_description():
    assert parsed_items[0]["description"] == ""


def test_links():
    assert parsed_items[0]["links"] == []
