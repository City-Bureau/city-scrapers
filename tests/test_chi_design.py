from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.utils import file_response
from city_scrapers_core.constants import ADVISORY_COMMITTEE, PASSED
from freezegun import freeze_time

from city_scrapers.spiders.chi_design import ChiDesignSpider

test_response_main = file_response(
    join(dirname(__file__), "files", "chi_design.html"),
    url="https://www.chicago.gov/city/en/depts/dcd/supp_info/committee-on-design.html",
)

test_response_meeting_august = file_response(
    join(dirname(__file__), "files", "chi_design_august.html"),
    url="https://www.chicago.gov/city/en/depts/dcd/supp_info/committee-on-design/august-2021.html",
)

test_response_meeting_november = file_response(
    join(dirname(__file__), "files", "chi_design_november.html"),
    url="https://www.chicago.gov/city/en/depts/dcd/supp_info/committee-on-design/november-2021.html",
)


# test_response_meeting_october = file_response(
#     join(dirname(__file__), "files", "chi_design_october.html"),
#     url="https://www.chicago.gov/city/en/depts/dcd/supp_info/committee-on-design/october-2021.html",
# )
#
# test_response_meeting_november = file_response(
#     join(dirname(__file__), "files", "chi_design_november.html"),
#     url="https://www.chicago.gov/city/en/depts/dcd/supp_info/committee-on-design/november-2021.html",
# )

test_response_meetings = [test_response_meeting_august, test_response_meeting_november]
spider = ChiDesignSpider()

freezer = freeze_time("2021-11-11")
freezer.start()

parsed_items = [item for meeting in test_response_meetings for item in spider.parse_meeting(meeting)]

freezer.stop()


def test_finds_all_meetings():
    requests = spider.parse(test_response_main)
    assert len(list(requests)) == 4


def test_title():
    assert parsed_items[0]["title"] == "Committee on Design"


def test_description():
    description = ('The applicant proposes to develop a 410’ tall, 26-story mixed-use office and '
                   'commercial building containing 184 parking spaces, 650,000 SF of office, and '
                   '9,000 sf of commercial/retail/restaurant at 315 N. May and a 369’ tall, '
                   '33-story mixed use building containing 377 residential units, 96 parking '
                   'spaces, and ground floor commercial/retail/restaurant uses at 1112 W. '
                   'Carroll, together these projects hope to enhance the vibrant character and '
                   'active ethos of the Fulton Market neighborhood. A roughly 30,000 SF park is '
                   'planned for the East portion of the residential site and will offer much '
                   'needed green space to the community of this area.'
                   '\n'
                   'The historic Laramie Bank Building will be restored and reopened to the '
                   'public with a new bank, café, Blues Museum, and business incubator space. It '
                   'will be operated by a community board and profits will be reinvested into '
                   'the neighborhood, building generational wealth. The vacant parcels will be '
                   'redeveloped into a six-story, 76-unit residential building, with a mix of 1, '
                   '2, and 3 bedroom units. Tenant amenities will include an outdoor rooftop '
                   'deck, fitness room, computer room, common space on each floor and a 1st '
                   'floor community room for events and social gatherings.')
    assert parsed_items[0]["description"] == description


def test_start():
    assert parsed_items[0]["start"] == datetime(2021, 8, 11, 13, 30)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == "chi_design/202108111330/x/committee_on_design"


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "",
        "address": "Virtual Meeting"
    }


def test_source():
    assert parsed_items[0]["source"] == test_response_meeting_august.url


@pytest.mark.xfail("AssertionError")
def test_links():
    assert parsed_items[1]["links"] == [{
        "href": "https://livestream.com/accounts/28669066/events/9117952",
        "title": "will be live streamed"
    }, {
        "href": "https://us06web.zoom.us/j/84508604903",
        "title": "Zoom session"
    }, {
        "href": "https://www.chicago.gov/content/dam/city/depts/dcd/cod/ag_isw_cod.pdf",
        "title": "Draft Presentation"
    }, {
        "href": "https://www.chicago.gov/content/dam/city/depts/dcd/cod/eng_isw_cod.pdf",
        "title": "Draft Presentation"
    }, {
        "href": "https://www.chicago.gov/content/dam/city/depts/dcd/cod/111021_cod_agenda.pdf",
        "title": "Agenda"
    }, {
        "href": "https://livestream.com/accounts/28669066/events/9117952",
        "title": "Live Stream"
    }, {
        "href": "https://us06web.zoom.us/j/84508604903",
        "title": "Join Zoom, Passcode: 492217"
    },

    ]


def test_classification():
    assert parsed_items[0]["classification"] == ADVISORY_COMMITTEE


def test_all_day():
    assert parsed_items[0]["all_day"] is False
