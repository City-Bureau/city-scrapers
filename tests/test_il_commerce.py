from datetime import datetime
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import COMMISSION, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.il_commerce import IlCommerceSpider

test_response = file_response(
    join(dirname(__file__), "files", "il_commerce.html"),
    url="https://www.icc.illinois.gov/meetings?dts=32&scm=True&sps=True&sh=True&sjc=True&ssh=False&smceb=True",  # noqa
)
test_detail_response = file_response(
    join(dirname(__file__), "files", "il_commerce_detail.html"),
    url="https://www.icc.illinois.gov/meetings/meeting/hearing/138529",
)
spider = IlCommerceSpider()

freezer = freeze_time("2023-12-01")
freezer.start()

parsed_requests = [item for item in spider.parse(test_response)]
parsed_item = [item for item in spider._parse_event_page(test_detail_response)][0]

freezer.stop()


def test_count():
    parsed_requests = [item for item in spider.parse(test_response)]
    print(parsed_requests)
    assert len(parsed_requests) == 74


def test_title():
    assert parsed_item["title"] == "Regular Open Meeting"


def test_description():
    assert parsed_item["description"] == ""


def test_start():
    assert parsed_item["start"] == datetime(2023, 12, 14, 11, 30)


def test_end():
    assert parsed_item["end"] is None


def test_time_notes():
    assert parsed_item["time_notes"] == ""


def test_id():
    assert (
        parsed_item["id"] == "il_commerce/202312141130/x/regular_open_meeting"  # noqa
    )


def test_status():
    assert parsed_item["status"] == TENTATIVE


def test_location():
    assert parsed_item["location"] == {
        "name": "Eighth Floor, State of Illinois Building",
        "address": "160 North LaSalle Street Chicago, Illinois 60601",
    }


def test_source():
    assert parsed_item["source"] == test_detail_response.url


def test_links():
    assert parsed_item["links"] == [
        {
            "href": "https://www.icc.illinois.gov/efiling/agenda/public/coverletter?agid=21912",  # noqa
            "title": "Public Utility Cover Letter",
        },
        {
            "href": "https://www.icc.illinois.gov/efiling/agenda/public/agendareport?agid=21912",  # noqa
            "title": "Regular Open Meeting Agenda",
        },
        {
            "href": "https://www.icc.illinois.gov/efiling/agenda/public/coverletter?agid=21938",  # noqa
            "title": "Transportation Cover Letter",
        },
        {
            "href": "https://www.icc.illinois.gov/efiling/agenda/public/agendareport?agid=21938",  # noqa
            "title": "Bench Agenda",
        },
    ]


def test_classification():
    assert parsed_item["classification"] == COMMISSION


def test_all_day():
    assert parsed_item["all_day"] is False
