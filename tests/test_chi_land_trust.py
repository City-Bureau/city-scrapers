from datetime import datetime
from operator import itemgetter
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import BOARD, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_land_trust import ChiLandTrustSpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_land_trust.html"),
    url="https://www.chicago.gov/city/en/depts/doh/supp_info/chicago_communitylandtrust0.html",  # noqa
)
spider = ChiLandTrustSpider()

freezer = freeze_time("2019-07-11")
freezer.start()

parsed_items = sorted(
    [item for item in spider.parse(test_response)], key=itemgetter("start")
)

freezer.stop()


def test_count():
    assert len(parsed_items) == 13


def test_title():
    assert parsed_items[-6]["title"] == "Board of Directors"


def test_description():
    assert parsed_items[-6]["description"] == ""


def test_start():
    assert parsed_items[-6]["start"] == datetime(2019, 2, 7, 9, 0)


def test_end():
    assert parsed_items[-6]["end"] is None


def test_time_notes():
    assert parsed_items[-6]["time_notes"] == "See agenda to confirm time"


def test_id():
    assert parsed_items[-6]["id"] == "chi_land_trust/201902070900/x/board_of_directors"


def test_status():
    assert parsed_items[-6]["status"] == PASSED


def test_location():
    assert parsed_items[-6]["location"] == spider.location


def test_source():
    assert (
        parsed_items[-6]["source"]
        == "https://www.chicago.gov/city/en/depts/doh/supp_info/chicago_communitylandtrust0.html"  # noqa
    )


def test_links():
    assert parsed_items[-6]["links"] == [
        {
            "href": "https://www.chicago.gov/content/dam/city/depts/doh/general/CCLT_February_2019_Agernda.pdf",  # noqa
            "title": "Agenda",
        }
    ]


def test_classification():
    assert parsed_items[-6]["classification"] == BOARD


def test_all_day():
    assert parsed_items[-6]["all_day"] is False
