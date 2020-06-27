from datetime import datetime
from os.path import dirname, join

import pytest
import scrapy
from city_scrapers_core.constants import BOARD, COMMITTEE, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_buildings import ChiBuildingsSpider

test_json_response = file_response(
    join(dirname(__file__), "files", "chi_buildings.json")
)
test_event_response = file_response(
    join(dirname(__file__), "files", "chi_buildings.html")
)

spider = ChiBuildingsSpider()


class MockRequest(object):
    meta = {}

    def __getitem__(self, key):
        return self.meta["meeting"].get(key)


def mock_request(*args, **kwargs):
    mock = MockRequest()
    mock.meta = {"meeting": {}}
    return mock


@pytest.fixture()
def parsed_items(monkeypatch):
    freezer = freeze_time("2018-12-19")
    freezer.start()
    monkeypatch.setattr(scrapy, "Request", mock_request)
    parsed_items = [item for item in spider.parse(test_json_response)]
    freezer.stop()
    return parsed_items


@pytest.fixture()
def parsed_event():
    return spider._parse_event(test_event_response)


def test_title(parsed_items):
    assert parsed_items[0]["title"] == "Administrative Operations Committee"


def test_classification(parsed_items):
    assert parsed_items[0]["classification"] == COMMITTEE
    assert parsed_items[1]["classification"] == BOARD
    assert parsed_items[2]["classification"] == COMMITTEE
    assert parsed_items[3]["classification"] == BOARD


def test_start(parsed_items):
    assert parsed_items[0]["start"] == datetime(2018, 12, 5, 10)


def test_end(parsed_items):
    assert parsed_items[0]["end"] is None


def test_id(parsed_items):
    assert parsed_items[0]["id"] == (
        "chi_buildings/201812051000/x/administrative_operations_committee"
    )


def test_description(parsed_items):
    assert parsed_items[0]["description"] == ""


def test_status(parsed_items):
    assert parsed_items[0]["status"] == PASSED


def test_source(parsed_items):
    assert parsed_items[0]["source"] == (
        "http://www.pbcchicago.com/events/event/pbc-administrative-operations-committee/"  # noqa
    )


def test_location(parsed_event):
    assert parsed_event["location"] == {
        "name": "Second Floor Board Room, Richard J. Daley Center",
        "address": "50 W. Washington Street Chicago, IL 60602",
    }


def test_links(parsed_event):
    assert parsed_event["links"] == [
        {
            "title": "Agenda",
            "href": "http://www.pbcchicago.com/wp-content/uploads/2018/11/MA_PBC_MPW_bdgeneral20181113.pdf",  # noqa
        },
        {
            "title": "Presentation",
            "href": "http://www.pbcchicago.com/wp-content/uploads/2018/11/BoardPresentation_20181113.pdf",  # noqa
        },
        {
            "title": "Summary",
            "href": "http://www.pbcchicago.com/wp-content/uploads/2018/11/Board-Summary.pdf",  # noqa
        },
        {
            "title": "Minutes",
            "href": "http://www.pbcchicago.com/wp-content/uploads/2018/12/A3.-MMR_NOVEMBERBOARDMINUTES_201812052.pdf",  # noqa
        },
    ]
