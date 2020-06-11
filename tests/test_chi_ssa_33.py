from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, COMMITTEE, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ssa_33 import ChiSsa33Spider

test_links_response = file_response(
    join(dirname(__file__), "files", "chi_ssa_33_links.html"),
    url="http://www.wickerparkbucktown.com/ssa/june-19-2019/",
)

test_response = file_response(
    join(dirname(__file__), "files", "chi_ssa_33_results.html"),
    url=(
        "http://www.wickerparkbucktown.com/index.php?submenu=ssa_events&src=events&srctype=events_lister_SSA&y=2019&m=6"  # noqa
    ),
)
spider = ChiSsa33Spider()

freezer = freeze_time("2019-07-01")
freezer.start()

spider._parse_docs(test_links_response)
parsed_items = [item for item in spider.parse_events(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 8


def test_title():
    assert parsed_items[0]["title"] == "Clean & Green Committee"
    assert parsed_items[5]["title"] == "WPB SSA #33 Commission Meeting"


def test_description():
    assert (
        parsed_items[0]["description"]
        == "1st Monday of the month @ 9am. The committee is tasked with improving the cleanliness/appearance of WPB’s streetscapes and other green sustainability initiatives."  # noqa
    )


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 6, 3, 9)


def test_end():
    assert parsed_items[0]["end"] == datetime(2019, 6, 3, 10, 30)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == "chi_ssa_33/201906030900/x/clean_green_committee"


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Janik's Cafe",
        "address": "2011 W Division St. Chicago, IL",
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "http://www.wickerparkbucktown.com/events/2019/06/03/ssa/clean-green-committee-ssa-33/21429/"  # noqa
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "http://www.wickerparkbucktown.com/clientuploads/SSA/Agendas_&_Minutes/6_18_19/2019_JUNE_-_MINUTES_-_Clean_&_Green.pdf",  # noqa
            "title": "Clean and Green Committee Report",
        }
    ]
    assert parsed_items[5]["links"] == [
        {
            "href": "http://www.wickerparkbucktown.com/clientuploads/SSA/Agendas_&_Minutes/6_18_19/SSA_Commission_-_JUNE_-_Agenda.pdf",  # noqa
            "title": "Agenda",
        },
        {
            "href": "http://www.wickerparkbucktown.com/clientuploads/SSA/Agendas_&_Minutes/6_18_19/SSA_Commission_-_JUNE_-_Minutes.pdf",  # noqa
            "title": "Minutes",
        },
        {
            "href": "http://www.wickerparkbucktown.com/clientuploads/SSA/Agendas_&_Minutes/6_18_19/Monthly_Accountants_Report__05-31-19.pdf",  # noqa
            "title": "Bookkeeper’s Report Overview",
        },
        {
            "href": "http://www.wickerparkbucktown.com/clientuploads/SSA/Agendas_&_Minutes/6_18_19/Financials/Stmt_of_Fin_Activity-Month_of_May_31_19.pdf",  # noqa
            "title": "Statement of Financial Activities",
        },
        {
            "href": "http://www.wickerparkbucktown.com/clientuploads/SSA/Agendas_&_Minutes/6_18_19/Financials/Stmt_of_Fin_Position_-_May_31_2019.pdf",  # noqa
            "title": "Statement of Financial Position",
        },
        {
            "href": "http://www.wickerparkbucktown.com/clientuploads/SSA/Agendas_&_Minutes/6_18_19/Financials/Budget_v_Actual-May_31_2019.pdf",  # noqa
            "title": "Budget vs. Actual",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMITTEE
    assert parsed_items[5]["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
