from datetime import datetime
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import COMMISSION, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.il_criminal_justice_information import (
    IlCriminalJusticeInformationSpider,
)

test_response = file_response(
    join(dirname(__file__), "files", "il_criminal_justice_information.json"),
    url="https://agency.icjia-api.cloud/graphql",
)
spider = IlCriminalJusticeInformationSpider()

freezer = freeze_time("2024-07-16")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 19


def test_title():
    assert (
        parsed_items[0]["title"]
        == "TRAFFIC & PEDESTRIAN STOP STATISTICAL STUDY TASK FORCE: July 25, 2024"  # noqa
    )


def test_description():
    assert (
        parsed_items[0]["description"]
        == "Thursday, July 25, 2024\n11:30pm – 12:30pm\nLocation\nVia WebEx Video Conference/Teleconference"  # noqa
    )


def test_start():
    assert parsed_items[0]["start"] == datetime(2024, 7, 25, 11, 30)


def test_end():
    assert parsed_items[0]["end"] == datetime(2024, 7, 25, 12, 30)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"]
        == "il_criminal_justice_information/202407251130/x/traffic_pedestrian_stop_statistical_study_task_force_july_25_2024"  # noqa
    )


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "TBD",
        "address": "",
    }


def test_source():
    assert parsed_items[0]["source"] == "https://agency.icjia-api.cloud/graphql"  # noqa


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://agency.icjia-api.cloud/uploads/Traffic_Data_Stop_Task_Force_Agenda_07_24_24_KA_TL_df57bde328.pdf",  # noqa
            "title": "Traffic Data Stop Task Force Agenda 07-24-24 KA TL.pdf",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


def test_all_day():
    assert parsed_items[0]["all_day"] is False
