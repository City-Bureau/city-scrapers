from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time
from scrapy.settings import Settings

from city_scrapers.spiders.chi_midway_noise import ChiMidwayNoiseSpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_midway_noise.html"),
    url="https://www.flychicago.com",
)
spider = ChiMidwayNoiseSpider()
spider.settings = Settings(values={"CITY_SCRAPERS_ARCHIVE": False})

freezer = freeze_time("2019-09-22")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 5


def test_title():
    assert parsed_items[0]["title"] == "Commission"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    expected_starts = [
        datetime(2018, 10, 25, 18, 30),
        datetime(2019, 1, 24, 18, 30),
        datetime(2019, 4, 25, 18, 30),
        datetime(2019, 7, 25, 18, 30),
        datetime(2019, 10, 24, 18, 30),
    ]

    for i in range(len(parsed_items)):
        assert parsed_items[i]["start"] == expected_starts[i]


@pytest.mark.parametrize("item", parsed_items)
def test_end(item):
    assert item["end"] is None


@pytest.mark.parametrize("item", parsed_items)
def test_time_notes(item):
    assert item["time_notes"] == "No start times given; past records indicate 6:30PM."


def test_id():
    expected_ids = [
        "chi_midway_noise/201810251830/x/commission",  # noqa
        "chi_midway_noise/201901241830/x/commission",  # noqa
        "chi_midway_noise/201904251830/x/commission",  # noqa
        "chi_midway_noise/201907251830/x/commission",  # noqa
        "chi_midway_noise/201910241830/x/commission",  # noqa
    ]

    for i in range(len(parsed_items)):
        assert parsed_items[i]["id"] == expected_ids[i]


def test_status():
    assert parsed_items[0]["status"] == PASSED
    assert parsed_items[-1]["status"] == TENTATIVE


@pytest.mark.parametrize("item", parsed_items)
def test_location(item):
    assert item["location"] == {
        "name": "The Mayfield",
        "address": "6072 S. Archer Ave., Chicago, IL 60638",
    }


@pytest.mark.parametrize("item", parsed_items)
def test_source(item):
    assert (
        item["source"]
        == "https://www.flychicago.com/community/MDWnoise/AdditionalResources/pages/default.aspx"  # noqa
    )


def test_links():
    expected_links = list()
    expected_links.append(
        [
            {  # October 25, 2018
                "href": "https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/2018.10_Meeting_Agenda.pdf",  # noqa
                "title": "Agenda",
            }
        ]
    )

    expected_links.append(
        [  # January 24, 2019
            {
                "href": "https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/2019.01_Meeting_Agenda.pdf",  # noqa
                "title": "Agenda",
            },
            {
                "href": "https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/Meeting_Minutes_2019.01.24_FINAL.pdf",  # noqa
                "title": "Minutes",
            },
        ]
    )

    expected_links.append(
        [
            {  # April 25, 2019
                "href": "https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/2019.04_Meeting_Agenda.pdf",  # noqa
                "title": "Agenda",
            }
        ]
    )

    expected_links.append(
        [
            {  # July 25, 2019
                "href": "https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/2019.07_Meeting_Agenda.pdf",  # noqa
                "title": "Agenda",
            }
        ]
    )

    expected_links.append([])  # October 24, 2019 - has no documents

    for i in range(len(parsed_items)):
        assert parsed_items[i]["links"] == expected_links[i]


@pytest.mark.parametrize("item", parsed_items)
def test_classification(item):
    assert item["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
