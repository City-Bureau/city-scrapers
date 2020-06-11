from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ssa_73 import ChiSsa73Spider

test_response = file_response(
    join(dirname(__file__), "files", "chi_ssa_73.html"),
    url="https://chinatownssa73.org/meeting-schedule/",
)
spider = ChiSsa73Spider()

freezer = freeze_time("2019-05-28")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


@pytest.mark.parametrize("item", parsed_items)
def test_title(item):
    assert item["title"] == "SSA #73 Chinatown Board"


@pytest.mark.parametrize("item", parsed_items)
def test_description(item):
    assert item["description"] == ""


def test_start():
    assert parsed_items[1]["start"] == datetime(2019, 2, 26, 18, 30)


@pytest.mark.parametrize("item", parsed_items)
def test_end(item):
    assert item["end"] is None


def test_id():
    assert parsed_items[0]["id"] == "chi_ssa_73/201901221830/x/ssa_73_chinatown_board"
    assert parsed_items[8]["id"] == "chi_ssa_73/201909241830/x/ssa_73_chinatown_board"


def test_status():
    assert parsed_items[0]["status"] == PASSED
    assert parsed_items[5]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Leonard M. Louie Fieldhouse",
        "address": "1700 S. Wentworth Avenue, Chicago, Illinois",
    }


@pytest.mark.parametrize("item", parsed_items)
def test_source(item):
    assert item["source"] == "https://chinatownssa73.org/meeting-schedule/"


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://chinatownssa73.org/wp-content/uploads/2019/01/Agenda-1-22-19.pdf",  # noqa
            "title": "Agenda",
        },
        {
            "href": "https://chinatownssa73.org/wp-content/uploads/2019/02/Minutes-1-22-2019.pdf",  # noqa
            "title": "Minutes",
        },
    ]
    assert parsed_items[5]["links"] == []


@pytest.mark.parametrize("item", parsed_items)
def test_classification(item):
    assert item["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
