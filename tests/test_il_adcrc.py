from datetime import datetime
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import COMMISSION, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

# Assuming there's a spider for this specific context
from city_scrapers.spiders.il_adcrc import IlAdcrcSpider

test_html_response = file_response(
    join(dirname(__file__), "files", "il_adcrc.html"),
    url="https://adcrc.illinois.gov/meetings.html",
)

test_json_response = file_response(
    join(dirname(__file__), "files", "il_adcrc.json"),
    url="https://adcrc.illinois.gov/content/soi/adcrc/en/meetings/jcr:content/responsivegrid/container/container_293684588/container/events_feed.model.json",  # noqa: E501
)
spider = IlAdcrcSpider()

freezer = freeze_time("2024-01-30")
freezer.start()

parse_html_response = next(spider.parse(test_html_response))
parsed_items = [item for item in spider.parse_json(test_json_response)]

freezer.stop()


def test_parsed_url():
    assert (
        parse_html_response.url
        == "https://adcrc.illinois.gov/content/soi/adcrc/en/meetings/jcr:content/responsivegrid/container/container_293684588/container/events_feed.model.json"  # noqa: E501
    )


def test_count():
    assert len(parsed_items) == 10


def test_title():
    assert (
        parsed_items[0]["title"] == "Research Subcommission Meeting - February 15, 2024"
    )


def test_description():
    expected_description = "Webinar number: 2634 343 4016 Webinar password: Rp4ht7K5HmV (77448755 from phones and video systems) Join by phone: +1-312-535-8110 United States Toll (Chicago) +1-415-655-0002 US Toll Access code: 2634 343 4016"  # noqa: E501
    assert parsed_items[0]["description"] == expected_description


def test_start():
    assert parsed_items[0]["start"] == datetime(2024, 2, 15, 10, 0)


def test_end():
    assert parsed_items[0]["end"] == datetime(2024, 2, 15, 12, 0)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""  # Assuming no special time notes


def test_id():
    assert (
        parsed_items[0]["id"]
        == "il_adcrc/202402151000/x/research_subcommission_meeting_february_15_2024"
    )


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "State of Illinois Office Building",
        "address": "555 W. Monroe, Chicago, IL",
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://adcrc.illinois.gov/content/soi/adcrc/en/meetings/jcr:content/responsivegrid/container/container_293684588/container/events_feed.model.json"  # noqa: E501
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://illinois.webex.com/illinois/j.php?MTID=ma9837fecab2aeef910300add0019513c",  # noqa: E501
            "title": "Virtual: WebEx",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


def test_all_day():
    assert parsed_items[0]["all_day"] is False
