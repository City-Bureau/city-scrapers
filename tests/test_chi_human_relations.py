from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_human_relations import ChiHumanRelationsSpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_human_relations.html"),
    url="https://www.chicago.gov/city/en/depts/cchr/supp_info/BoardMeetingInformation.html",  # noqa
)
spider = ChiHumanRelationsSpider()

freezer = freeze_time("2024-05-01")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]
parsed_item = parsed_items[0]
freezer.stop()


def test_title():
    assert (
        parsed_item["title"] == "Chicago Commission on Human Relations Board Meeting"
    )  # noqa


def test_description():
    assert parsed_item["description"] == ""


def test_start():
    assert parsed_item["start"] == datetime(2024, 5, 9, 9, 30)


def test_end():
    assert parsed_item["end"] is None


def test_time_notes():
    assert parsed_item["time_notes"] == ""


def test_id():
    assert (
        parsed_item["id"]
        == "chi_human_relations/202405090930/x/chicago_commission_on_human_relations_board_meeting"  # noqa
    )


def test_status():
    assert parsed_item["status"] == TENTATIVE


def test_location():
    assert parsed_item["location"] == {
        "name": "Chicago Commission on Human Relations - board room",
        "address": "740 N Sedgwick St, 4th Floor Boardroom, Chicago, IL 60654",
    }


def test_source():
    assert (
        parsed_item["source"]
        == "https://www.chicago.gov/city/en/depts/cchr/supp_info/BoardMeetingInformation.html"  # noqa
    )


def test_links():
    assert parsed_item["links"] == [
        {
            "title": "Meeting materials",
            "href": "https://www.chicago.gov/city/en/depts/cchr/supp_info/BoardMeetingInformation.html",  # noqa
        }
    ]


def test_classification():
    assert parsed_item["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
