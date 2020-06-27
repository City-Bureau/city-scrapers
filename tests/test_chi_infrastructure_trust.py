from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD
from city_scrapers_core.utils import file_response
from freezegun import freeze_time
from scrapy.settings import Settings

from city_scrapers.spiders.chi_infrastructure_trust import ChiInfrastructureTrustSpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_infrastructure_trust.html"),
    url="http://chicagoinfrastructure.org/public-records/meeting-records-2/",
)
spider = ChiInfrastructureTrustSpider()
spider.settings = Settings(values={"CITY_SCRAPERS_ARCHIVE": False})

freezer = freeze_time("2019-04-18")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 2


def test_title():
    assert parsed_items[0]["title"] == "Board of Directors"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2018, 12, 11, 0, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == "Confirm details in meeting documents"


def test_id():
    assert (
        parsed_items[0]["id"]
        == "chi_infrastructure_trust/201812110000/x/board_of_directors"
    )


def test_status():
    assert parsed_items[0]["status"] == "passed"


def test_location():
    assert parsed_items[0]["location"] == {
        "address": "140 South Dearborn Street, Suite 1400, Chicago, IL 60603",
        "name": "Metropolitan Planning Council",
    }


def test_source():
    assert parsed_items[0]["source"] == (
        "http://chicagoinfrastructure.org/" "public-records/meeting-records-2/"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "http://chicagoinfrastructure.org/wp-content/uploads/2018/12/"
            "Board-Meeting-Agenda-20181211.pdf",
            "title": "Meeting Agenda",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
