from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import ADVISORY_COMMITTEE, BOARD, COMMITTEE, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.det_regional_transit_authority import DetRegionalTransitAuthoritySpider

test_response = file_response(
    join(dirname(__file__), "files", "det_regional_transit_authority.html"),
    url="http://www.rtamichigan.org/board-committee-meetings/",
)
spider = DetRegionalTransitAuthoritySpider()

freezer = freeze_time("2019-10-15")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 58


def test_title():
    assert parsed_items[0]["title"] == "Board of Directors"


def test_all_committees():
    titles = {item["title"] for item in parsed_items}
    assert titles == {
        "Board of Directors", "Citizens Advisory Committee", "Executive and Policy Committee",
        "Finance and Budget Committee", "Planning and Service Coordination Committee",
        "Providers Advisory Council"
    }


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 1, 17, 14, 0)
    assert parsed_items[-1]["start"] == datetime(2019, 9, 12, 10, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_id():
    assert parsed_items[0]["id"
                           ] == "det_regional_transit_authority/201901171400/x/board_of_directors"


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == spider.location


def test_source():
    assert parsed_items[0]["source"] == test_response.url


def test_links():
    assert parsed_items[
        0
    ]["links"
      ] == [{
          "href":
              "https://drive.google.com/file/d/15v3P0WhECD5wqvSgoOxOyPeBH0a0sXrY/view?usp=sharing",
          "title": "Meeting Notice"
      }, {
          "href":
              "https://drive.google.com/file/d/156c6S6EjD6bHxduTeuFFQOdCM7AyYob2/view?usp=sharing",
          "title": "Agenda & Documents"
      }, {
          "href":
              "https://drive.google.com/file/d/16VxOoX8jkjKrkKjcliwgl1s4c-BXAHZA/view?usp=sharing",
          "title": "Meeting Summary"
      }]


def test_classification():
    bod = [item for item in parsed_items if item["title"] == "Board of Directors"][0]
    ca = [item for item in parsed_items if item["title"] == "Citizens Advisory Committee"][0]
    epc = [item for item in parsed_items if item["title"] == "Executive and Policy Committee"][0]
    assert bod["classification"] == BOARD
    assert ca["classification"] == ADVISORY_COMMITTEE
    assert epc["classification"] == COMMITTEE


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
