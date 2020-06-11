from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.il_police_professionalism import (
    IlPoliceProfessionalismSpider,
)

test_response = file_response(
    join(dirname(__file__), "files", "il_police_professionalism.html"),
    url="https://www.isp.state.il.us/media/pressdetails.cfm?ID=1028",
)
spider = IlPoliceProfessionalismSpider()

freezer = freeze_time("2019-09-11")
freezer.start()

item = spider._parse_item(test_response)

freezer.stop()


def test_title():
    assert item["title"] == "Commission on Police Professionalism"


def test_start():
    assert item["start"] == datetime(2019, 3, 28, 14, 0)


def test_end():
    assert item["end"] is None


def test_time_notes():
    assert item["time_notes"] == ""


def test_id():
    assert (
        item["id"]
        == "il_police_professionalism/201903281400/x/commission_on_police_professionalism"  # noqa
    )


def test_status():
    assert item["status"] == "passed"


def test_location():
    assert item["location"] == {
        "name": "Illinois State Capitol",
        "address": "301 S 2nd St, Springfield, IL 62701",
    }


def test_source():
    assert (
        item["source"] == "https://www.isp.state.il.us/media/pressdetails.cfm?ID=1028"
    )


def test_links():
    assert item["links"] == [
        {
            "href": "https://www.isp.state.il.us/media/pressdetails.cfm?ID=1028",
            "title": "Agenda",
        }
    ]


def test_classification():
    assert item["classification"] == COMMISSION


def test_all_day():
    assert item["all_day"] is False
