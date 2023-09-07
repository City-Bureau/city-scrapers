import json
from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_northwest_home_equity import ChiNorthwestHomeEquitySpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_northwest_home_equity.html"),
    url="https://nwheap.com/category/meet-minutes-and-agendas/",
)

path_to_json = join(dirname(__file__), "files", "chi_northwest_home_equity")
url_to_local = json.loads(open(join(path_to_json, "url_to_local.json")).read())

for link, local in url_to_local.items():
    url_to_local[link] = join(
        dirname(__file__), "files", "chi_northwest_home_equity", local
    )

spider = ChiNorthwestHomeEquitySpider()


class MockRequest:
    def __call__(self, url, callback):
        return callback(self._request(url))

    def _request(self, url):
        return file_response(url_to_local[url], url=url)


@pytest.fixture()
def parsed_items(monkeypatch):
    freezer = freeze_time("2023-09-04")
    freezer.start()
    monkeypatch.setattr("scrapy.Request", MockRequest())
    parsed_items = list(spider.parse(test_response))
    freezer.stop()
    return parsed_items


def test_length(parsed_items):
    assert len(parsed_items) == 7


def test_title(parsed_items):
    assert parsed_items[0]["title"] == "Governing Commissioners Public Meeting"


def test_description(parsed_items):
    assert parsed_items[0]["description"] == ""


def test_start(parsed_items):
    assert parsed_items[0]["start"] == datetime(2023, 10, 19, 18, 30)


def test_end(parsed_items):
    assert parsed_items[0]["end"] == datetime(2023, 10, 19, 19, 30)


def test_location(parsed_items):
    assert parsed_items[0]["location"] == {
        "name": "",
        "address": "3234 N. Central Ave.",
    }


def test_source(parsed_items):
    source = "https://nwheap.com/events/governing-commissioners-public-meeting-18/"
    assert parsed_items[0]["source"] == source


def test_time_notes(parsed_items):
    assert parsed_items[0]["time_notes"] == ""


def test_id(parsed_items):
    base = "chi_northwest_home_equity/202310191830/x/"
    id = base + "governing_commissioners_public_meeting"
    assert parsed_items[0]["id"] == id


def test_status(parsed_items):
    assert parsed_items[0]["status"] == "tentative"


def test_links(parsed_items):
    assert parsed_items[0]["links"] == [
        {
            "href": "https://nwheap.com/locations/3234-n-central-ave/",
            "title": "3234 N. Central Ave.",
        }
    ]


def test_classification(parsed_items):
    assert parsed_items[0]["classification"] == COMMISSION
