from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.wayne_land_bank import WayneLandBankSpider

test_response = file_response(
    join(dirname(__file__), "files", "wayne_land_bank.html"),
    url="https://public-wclb.epropertyplus.com/landmgmtpub/app/base/customPage",
)
spider = WayneLandBankSpider()

freezer = freeze_time("2019-10-08")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Board of Directors"
    assert parsed_items[1]["title"] == "Board of Directors Special Meeting"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 1, 17, 14, 0)
    assert parsed_items[1]["start"] == datetime(2019, 2, 20, 11, 0)
    assert parsed_items[2]["start"] == datetime(2019, 4, 18, 14, 0)
    assert parsed_items[3]["start"] == datetime(2019, 8, 15, 14, 0)
    assert parsed_items[4]["start"] == datetime(2019, 11, 21, 14, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == "wayne_land_bank/201901171400/x/board_of_directors"
    assert parsed_items[1]["id"] == "wayne_land_bank/201902201100/x/board_of_directors"\
                                    + "_special_meeting"


def test_status():
    assert parsed_items[0]["status"] == "passed"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Wayne County Treasurer's Office",
        "address": "400 Monroe St 5th Floor, Detroit, MI 48226"
    }


def test_source():
    assert parsed_items[0][
        "source"] == "https://public-wclb.epropertyplus.com/landmgmtpub/app/base/customPage"


def test_links():
    assert parsed_items[0]["links"] == []


def test_classification():
    assert parsed_items[0]["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
