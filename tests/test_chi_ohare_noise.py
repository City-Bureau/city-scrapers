import datetime as dt
from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, COMMITTEE, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_ohare_noise import ChiOhareNoiseSpider

spider = ChiOhareNoiseSpider()

freezer = freeze_time("2020-08-22")
freezer.start()

test_response = file_response(
    join(dirname(__file__), "files/chi_ohare_noise", "chi_ohare_noise.html"),
    url=(
        "https://www.oharenoise.org/about-oncc"
        + "/oncc-meetings/month.calendar/2019/02/03/-"
    ),
)

parsed_items = [item for item in spider.ChiOhareNoiseSubSpider1().parse(test_response)]

freezer.stop()


def test_tests():
    assert len(parsed_items) == 45


parsed_sub_items = []
for i in range(5):
    test_response_2 = file_response(
        join(
            dirname(__file__),
            "files/chi_ohare_noise",
            "chi_ohare_noise_meetings_sub_{0}.html".format(i + 1),
        ),
        url=(
            "https://www.oharenoise.org/about-oncc/"
            + "oncc-meetings/month.calendar/2019/02/03/-"
        ),
    )
    parsed_sub_items.append(
        spider.ChiOhareNoiseSubSpider1()._parse_details(test_response_2)
    )


def test_title():
    assert parsed_sub_items[0]["title"] == (
        "O'Hare Noise Compatibility Commission" + " Meeting (via video/teleconference)"
    )
    assert parsed_sub_items[1]["title"] == (
        "Fly Quiet Committee" + " (via video/teleconference)"
    )
    assert parsed_sub_items[2]["title"] == "Executive Committee Meeting"
    assert parsed_sub_items[3]["title"] == "Executive Committee Meeting"
    assert parsed_sub_items[4]["title"] == "Fly Quiet Committee"


def test_description():
    assert parsed_sub_items[0]["description"] == "Join Zoom Meeting"
    assert parsed_sub_items[1]["description"] == "Join Zoom Meeting"
    assert parsed_sub_items[2]["description"] == ""
    assert parsed_sub_items[3]["description"] == ""
    assert parsed_sub_items[4]["description"] == ""


def test_start():
    assert parsed_sub_items[0]["start"] == datetime(2020, 6, 5, 8, 0)
    assert parsed_sub_items[1]["start"] == datetime(2020, 5, 26, 9, 30)
    assert parsed_sub_items[2]["start"] == datetime(2020, 2, 10, 10, 30)
    assert parsed_sub_items[3]["start"] == datetime(2020, 1, 6, 10, 30)
    assert parsed_sub_items[4]["start"] == datetime(2020, 12, 8, 9, 30)


def test_end():
    assert parsed_sub_items[0]["end"] == datetime(2020, 6, 5, 9, 0)
    assert parsed_sub_items[1]["end"] == datetime(2020, 5, 26, 10, 30)
    assert parsed_sub_items[2]["end"] == datetime(2020, 2, 10, 11, 30)
    assert parsed_sub_items[3]["end"] == datetime(2020, 1, 6, 11, 30)
    assert parsed_sub_items[4]["end"] == datetime(2020, 12, 8, 10, 30)


def test_status():
    assert parsed_sub_items[0]["status"] == PASSED
    assert parsed_sub_items[1]["status"] == PASSED
    assert parsed_sub_items[2]["status"] == PASSED
    assert parsed_sub_items[3]["status"] == PASSED
    assert parsed_sub_items[4]["status"] == TENTATIVE


def test_location():
    assert parsed_sub_items[0]["location"] == {
        "name": "(via video/teleconference)",
        "address": "(via video/teleconference)",
    }
    assert parsed_sub_items[1]["location"] == {
        "name": "(via video/teleconference)",
        "address": "(via video/teleconference)",
    }
    assert parsed_sub_items[2]["location"] == {
        "name": "Aviation Administration Building",
        "address": "10510 W. Zemke Rd",
    }
    assert parsed_sub_items[3]["location"] == {
        "name": "Aviation Administration Building",
        "address": "10510 W. Zemke Rd",
    }
    assert parsed_sub_items[4]["location"] == {
        "name": "Chicago Dept. of Aviation Building",
        "address": "10510 W. Zemke Road, Chicago, IL, Conference Room 1",
    }


def test_source():
    src = "https://www.oharenoise.org/about-oncc"
    src += "/oncc-meetings/month.calendar/2019/02/03/-"
    assert parsed_sub_items[0]["source"] == src
    assert parsed_sub_items[1]["source"] == src
    assert parsed_sub_items[2]["source"] == src
    assert parsed_sub_items[3]["source"] == src
    assert parsed_sub_items[4]["source"] == src


def test_classification():
    assert parsed_sub_items[0]["classification"] == COMMISSION
    assert parsed_sub_items[1]["classification"] == COMMITTEE
    assert parsed_sub_items[2]["classification"] == COMMITTEE
    assert parsed_sub_items[3]["classification"] == COMMITTEE
    assert parsed_sub_items[4]["classification"] == COMMITTEE


@pytest.mark.parametrize("item", parsed_sub_items)
def test_all_day(item):
    assert item["all_day"] is False


# Parsing for second sub spider
test_response_3 = file_response(
    join(
        dirname(__file__),
        "files/chi_ohare_noise",
        "chi_ohare_noise_minutes_agenda.html",
    ),
    url="https://www.oharenoise.org/about-oncc/agendas-and-minutes",
)

parsed_items_3 = [
    item for item in spider.ChiOhareNoiseSubSpider2().parse(test_response_3)
]


def test_title_3():
    assert parsed_items_3[0]["title"] == "Executive Committee"
    assert parsed_items_3[1]["title"] == "Fly Quiet Committee"
    assert parsed_items_3[2]["title"] == "Technical Committee"
    assert parsed_items_3[3]["title"] == "Strategic Planning"
    assert parsed_items_3[4]["title"] == "Fly Quiet Committee"
    assert parsed_items_3[5]["title"] == "ONCC General Meeting"
    assert parsed_items_3[6]["title"] == "Executive Committee"
    assert parsed_items_3[7]["title"] == "Fly Quiet Committee"
    assert parsed_items_3[8]["title"] == "Technical Committee"
    assert parsed_items_3[9]["title"] == "Ad Hoc Governance Committee"
    assert parsed_items_3[10]["title"] == "Residential Sound Insulation Committee"
    assert parsed_items_3[11]["title"] == "Ad-Hoc Nominating Committee"
    assert parsed_items_3[12]["title"] == "Executive Committee"
    assert parsed_items_3[13]["title"] == "Fly Quiet Committee"
    assert parsed_items_3[14]["title"] == "Ad Hoc Governance Committee"
    assert parsed_items_3[15]["title"] == "Technical Committee"
    assert parsed_items_3[16]["title"] == "Executive Committee"
    assert parsed_items_3[17]["title"] == "Fly Quiet Committee"
    assert parsed_items_3[18]["title"] == "Ad Hoc Governance Committee"
    assert parsed_items_3[19]["title"] == "ONCC General Meeting"


def test_start_3():
    assert parsed_items_3[0]["start"] == dt.datetime(2020, 8, 31, 0, 0)
    assert parsed_items_3[1]["start"] == dt.datetime(2020, 8, 20, 0, 0)
    assert parsed_items_3[2]["start"] == dt.datetime(2020, 8, 18, 0, 0)
    assert parsed_items_3[3]["start"] == dt.datetime(2020, 8, 13, 0, 0)
    assert parsed_items_3[4]["start"] == dt.datetime(2020, 6, 23, 0, 0)
    assert parsed_items_3[5]["start"] == dt.datetime(2020, 6, 5, 0, 0)
    assert parsed_items_3[6]["start"] == dt.datetime(2020, 6, 1, 0, 0)
    assert parsed_items_3[7]["start"] == dt.datetime(2020, 5, 26, 0, 0)
    assert parsed_items_3[8]["start"] == dt.datetime(2020, 5, 19, 0, 0)
    assert parsed_items_3[9]["start"] == dt.datetime(2020, 5, 19, 0, 0)
    assert parsed_items_3[10]["start"] == dt.datetime(2020, 5, 13, 0, 0)
    assert parsed_items_3[11]["start"] == dt.datetime(2020, 5, 12, 0, 0)
    assert parsed_items_3[12]["start"] == dt.datetime(2020, 4, 27, 0, 0)
    assert parsed_items_3[13]["start"] == dt.datetime(2020, 4, 21, 0, 0)
    assert parsed_items_3[14]["start"] == dt.datetime(2020, 4, 20, 0, 0)
    assert parsed_items_3[15]["start"] == dt.datetime(2020, 4, 14, 0, 0)
    assert parsed_items_3[16]["start"] == dt.datetime(2020, 3, 30, 0, 0)
    assert parsed_items_3[17]["start"] == dt.datetime(2020, 2, 25, 0, 0)
    assert parsed_items_3[18]["start"] == dt.datetime(2020, 2, 18, 0, 0)
    assert parsed_items_3[19]["start"] == dt.datetime(2020, 2, 14, 0, 0)


def test_status_3():
    assert parsed_items_3[0]["status"] == PASSED
    assert parsed_items_3[1]["status"] == PASSED
    assert parsed_items_3[2]["status"] == PASSED
    assert parsed_items_3[3]["status"] == PASSED
    assert parsed_items_3[4]["status"] == PASSED
    assert parsed_items_3[5]["status"] == PASSED
    assert parsed_items_3[6]["status"] == PASSED
    assert parsed_items_3[7]["status"] == PASSED
    assert parsed_items_3[8]["status"] == PASSED
    assert parsed_items_3[9]["status"] == PASSED
    assert parsed_items_3[10]["status"] == PASSED
    assert parsed_items_3[11]["status"] == PASSED
    assert parsed_items_3[12]["status"] == PASSED
    assert parsed_items_3[13]["status"] == PASSED
    assert parsed_items_3[14]["status"] == PASSED
    assert parsed_items_3[15]["status"] == PASSED
    assert parsed_items_3[16]["status"] == PASSED
    assert parsed_items_3[17]["status"] == PASSED
    assert parsed_items_3[18]["status"] == PASSED
    assert parsed_items_3[19]["status"] == PASSED


def test_links_3():
    assert parsed_items_3[0]["links"] == [
        {
            "href": "https://www.oharenoise.org/about-oncc/agendas-and-minutes"
            + "?format=raw&task=download&fid=651",
            "title": "Agenda",
        }
    ]
    assert len(parsed_items_3[0]["links"]) == 1
    assert parsed_items_3[1]["links"] == [
        {
            "href": "https://www.oharenoise.org/about-oncc/agendas-and-minutes"
            + "?format=raw&task=download&fid=645",
            "title": "Agenda",
        }
    ]
    assert len(parsed_items_3[1]["links"]) == 1
    assert parsed_items_3[2]["links"] == [
        {
            "href": "https://www.oharenoise.org/about-oncc/agendas-and-minutes"
            + "?format=raw&task=download&fid=644",
            "title": "Agenda",
        }
    ]
    assert len(parsed_items_3[2]["links"]) == 1
    assert parsed_items_3[3]["links"] == [
        {
            "href": "https://www.oharenoise.org/about-oncc/agendas-and-minutes"
            + "?format=raw&task=download&fid=643",
            "title": "Agenda",
        }
    ]
    assert len(parsed_items_3[3]["links"]) == 1
    assert parsed_items_3[4]["links"] == [
        {
            "href": "https://www.oharenoise.org/about-oncc/agendas-and-minutes"
            + "?format=raw&task=download&fid=632",
            "title": "Agenda",
        },
        {
            "href": "https://www.oharenoise.org/about-oncc/agendas-and-minutes"
            + "?format=raw&task=download&fid=650",
            "title": "Minutes",
        },
    ]
    assert len(parsed_items_3[4]["links"]) == 2
    assert parsed_items_3[5]["links"] == [
        {
            "href": "https://www.oharenoise.org/about-oncc/agendas-and-minutes"
            + "?format=raw&task=download&fid=631",
            "title": "Agenda",
        }
    ]
    assert len(parsed_items_3[5]["links"]) == 1
    assert parsed_items_3[6]["links"] == [
        {
            "href": "https://www.oharenoise.org/about-oncc/agendas-and-minutes"
            + "?format=raw&task=download&fid=629",
            "title": "Agenda",
        },
        {
            "href": "https://www.oharenoise.org/about-oncc/agendas-and-minutes"
            + "?format=raw&task=download&fid=646",
            "title": "Minutes",
        },
    ]
    assert len(parsed_items_3[6]["links"]) == 2
    assert parsed_items_3[7]["links"] == [
        {
            "href": "https://www.oharenoise.org/about-oncc/agendas-and-minutes"
            + "?format=raw&task=download&fid=627",
            "title": "Agenda",
        },
        {
            "href": "https://www.oharenoise.org/about-oncc/agendas-and-minutes"
            + "?format=raw&task=download&fid=642",
            "title": "Minutes",
        },
    ]
    assert len(parsed_items_3[7]["links"]) == 2
    assert parsed_items_3[8]["links"] == [
        {
            "href": "https://www.oharenoise.org/about-oncc/agendas-and-minutes"
            + "?format=raw&task=download&fid=624",
            "title": "Agenda",
        },
        {
            "href": "https://www.oharenoise.org/about-oncc/agendas-and-minutes"
            + "?format=raw&task=download&fid=648",
            "title": "Minutes",
        },
    ]
    assert len(parsed_items_3[8]["links"]) == 2
    assert parsed_items_3[9]["links"] == [
        {
            "href": "https://www.oharenoise.org/about-oncc/agendas-and-minutes"
            + "?format=raw&task=download&fid=625",
            "title": "Agenda",
        }
    ]
    assert len(parsed_items_3[9]["links"]) == 1
    assert parsed_items_3[10]["links"] == [
        {
            "href": "https://www.oharenoise.org/about-oncc/agendas-and-minutes"
            + "?format=raw&task=download&fid=623",
            "title": "Agenda",
        }
    ]
    assert len(parsed_items_3[10]["links"]) == 1
    assert parsed_items_3[11]["links"] == [
        {
            "href": "https://www.oharenoise.org/about-oncc/agendas-and-minutes"
            + "?format=raw&task=download&fid=621",
            "title": "Agenda",
        },
        {
            "href": "https://www.oharenoise.org/about-oncc/agendas-and-minutes"
            + "?format=raw&task=download&fid=641",
            "title": "Minutes",
        },
    ]
    assert len(parsed_items_3[11]["links"]) == 2
    assert parsed_items_3[12]["links"] == [
        {
            "href": "https://www.oharenoise.org/about-oncc/agendas-and-minutes"
            + "?format=raw&task=download&fid=613",
            "title": "Agenda",
        },
        {
            "href": "https://www.oharenoise.org/about-oncc/agendas-and-minutes"
            + "?format=raw&task=download&fid=649",
            "title": "Minutes",
        },
    ]
    assert len(parsed_items_3[12]["links"]) == 2
    assert parsed_items_3[13]["links"] == [
        {
            "href": "https://www.oharenoise.org/about-oncc/agendas-and-minutes"
            + "?format=raw&task=download&fid=611",
            "title": "Agenda",
        },
        {
            "href": "https://www.oharenoise.org/about-oncc/agendas-and-minutes"
            + "?format=raw&task=download&fid=630",
            "title": "Minutes",
        },
    ]
    assert len(parsed_items_3[13]["links"]) == 2
    assert parsed_items_3[14]["links"] == [
        {
            "href": "https://www.oharenoise.org/about-oncc/agendas-and-minutes"
            + "?format=raw&task=download&fid=612",
            "title": "Agenda",
        },
        {
            "href": "https://www.oharenoise.org/about-oncc/agendas-and-minutes"
            + "?format=raw&task=download&fid=640",
            "title": "Minutes",
        },
    ]
    assert len(parsed_items_3[14]["links"]) == 2
    assert parsed_items_3[15]["links"] == [
        {
            "href": "https://www.oharenoise.org/about-oncc/agendas-and-minutes"
            + "?format=raw&task=download&fid=610",
            "title": "Agenda",
        },
        {
            "href": "https://www.oharenoise.org/about-oncc/agendas-and-minutes"
            + "?format=raw&task=download&fid=639",
            "title": "Minutes",
        },
    ]
    assert len(parsed_items_3[15]["links"]) == 2
    assert parsed_items_3[16]["links"] == [
        {
            "href": "https://www.oharenoise.org/about-oncc/agendas-and-minutes"
            + "?format=raw&task=download&fid=609",
            "title": "Agenda",
        },
        {
            "href": "https://www.oharenoise.org/about-oncc/agendas-and-minutes"
            + "?format=raw&task=download&fid=638",
            "title": "Minutes",
        },
    ]
    assert len(parsed_items_3[16]["links"]) == 2
    assert parsed_items_3[17]["links"] == [
        {
            "href": "https://www.oharenoise.org/about-oncc/agendas-and-minutes"
            + "?format=raw&task=download&fid=605",
            "title": "Agenda",
        },
        {
            "href": "https://www.oharenoise.org/about-oncc/agendas-and-minutes"
            + "?format=raw&task=download&fid=615",
            "title": "Minutes",
        },
    ]
    assert len(parsed_items_3[17]["links"]) == 2
    assert parsed_items_3[18]["links"] == [
        {
            "href": "https://www.oharenoise.org/about-oncc/agendas-and-minutes"
            + "?format=raw&task=download&fid=603",
            "title": "Agenda",
        },
        {
            "href": "https://www.oharenoise.org/about-oncc/agendas-and-minutes"
            + "?format=raw&task=download&fid=618",
            "title": "Minutes",
        },
    ]
    assert len(parsed_items_3[18]["links"]) == 2
    assert parsed_items_3[19]["links"] == [
        {
            "href": "https://www.oharenoise.org/about-oncc/agendas-and-minutes"
            + "?format=raw&task=download&fid=604",
            "title": "Agenda",
        },
        {
            "href": "https://www.oharenoise.org/about-oncc/agendas-and-minutes"
            + "?format=raw&task=download&fid=637",
            "title": "Minutes",
        },
    ]
    assert len(parsed_items_3[19]["links"]) == 2
