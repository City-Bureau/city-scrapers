from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_midway_noise import ChiMidwayNoiseSpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_midway_noise.html"),
    url="https://www.flychicago.com",
)
spider = ChiMidwayNoiseSpider()

freezer = freeze_time("2019-09-22")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 34


@pytest.mark.parametrize("item", parsed_items)
def test_title(item):
    assert item["title"] == "Midway Noise Compatibility Commission Meeting"


def test_description():
    c_e, c_r, r, s = 'Executive Committee Meeting', 'Residential Committee Meeting', \
                     'Regular Meeting', 'Special Meeting'
    expected_descs = [r, c_e, s, r, r, c_r, r, r, r, r, r, r, r, r, r, r, r, c_e, r, r, c_r, r,
                      r, r, r, r, c_e, r, r, r, r, r, r, r]
    for i in range(len(parsed_items)):
        assert parsed_items[i]["description"] == expected_descs[i]


def test_start():
    expected_starts = [datetime(2013, 1, 24, 18, 30),
                       datetime(2013, 2, 28, 18, 30),
                       datetime(2013, 4, 2, 18, 30),
                       datetime(2013, 4, 25, 18, 30),
                       datetime(2013, 7, 25, 18, 30),
                       datetime(2013, 10, 22, 18, 30),
                       datetime(2013, 10, 24, 18, 30),
                       datetime(2014, 1, 23, 18, 30),
                       datetime(2014, 4, 24, 18, 30),
                       datetime(2014, 7, 24, 18, 30),
                       datetime(2014, 10, 23, 18, 30),
                       datetime(2015, 1, 22, 18, 30),
                       datetime(2015, 4, 23, 18, 30),
                       datetime(2015, 7, 23, 18, 30),
                       datetime(2015, 10, 22, 18, 30),
                       datetime(2016, 1, 28, 18, 30),
                       datetime(2016, 4, 28, 18, 30),
                       datetime(2016, 7, 26, 18, 30),
                       datetime(2016, 7, 28, 18, 30),
                       datetime(2016, 10, 27, 18, 30),
                       datetime(2017, 1, 23, 18, 30),
                       datetime(2017, 1, 26, 18, 30),
                       datetime(2017, 4, 27, 18, 30),
                       datetime(2017, 7, 27, 18, 30),
                       datetime(2017, 10, 26, 18, 30),
                       datetime(2018, 1, 25, 18, 30),
                       datetime(2018, 1, 30, 18, 30),
                       datetime(2018, 4, 26, 18, 30),
                       datetime(2018, 7, 26, 18, 30),
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
    expected_ids = ["chi_midway_noise/201301241830/Regular Meeting/midway_noise_compatibility_commission_meeting",
                    "chi_midway_noise/201302281830/Executive Committee Meeting/midway_noise_compatibility_commission_meeting",
                    "chi_midway_noise/201304021830/Special Meeting/midway_noise_compatibility_commission_meeting",
                    "chi_midway_noise/201304251830/Regular Meeting/midway_noise_compatibility_commission_meeting",
                    "chi_midway_noise/201307251830/Regular Meeting/midway_noise_compatibility_commission_meeting",
                    "chi_midway_noise/201310221830/Residential Committee Meeting/midway_noise_compatibility_commission_meeting",
                    "chi_midway_noise/201310241830/Regular Meeting/midway_noise_compatibility_commission_meeting",
                    "chi_midway_noise/201401231830/Regular Meeting/midway_noise_compatibility_commission_meeting",
                    "chi_midway_noise/201404241830/Regular Meeting/midway_noise_compatibility_commission_meeting",
                    "chi_midway_noise/201407241830/Regular Meeting/midway_noise_compatibility_commission_meeting",
                    "chi_midway_noise/201410231830/Regular Meeting/midway_noise_compatibility_commission_meeting",
                    "chi_midway_noise/201501221830/Regular Meeting/midway_noise_compatibility_commission_meeting",
                    "chi_midway_noise/201504231830/Regular Meeting/midway_noise_compatibility_commission_meeting",
                    "chi_midway_noise/201507231830/Regular Meeting/midway_noise_compatibility_commission_meeting",
                    "chi_midway_noise/201510221830/Regular Meeting/midway_noise_compatibility_commission_meeting",
                    "chi_midway_noise/201601281830/Regular Meeting/midway_noise_compatibility_commission_meeting",
                    "chi_midway_noise/201604281830/Regular Meeting/midway_noise_compatibility_commission_meeting",
                    "chi_midway_noise/201607261830/Executive Committee Meeting/midway_noise_compatibility_commission_meeting",
                    "chi_midway_noise/201607281830/Regular Meeting/midway_noise_compatibility_commission_meeting",
                    "chi_midway_noise/201610271830/Regular Meeting/midway_noise_compatibility_commission_meeting",
                    "chi_midway_noise/201701231830/Residential Committee Meeting/midway_noise_compatibility_commission_meeting",
                    "chi_midway_noise/201701261830/Regular Meeting/midway_noise_compatibility_commission_meeting",
                    "chi_midway_noise/201704271830/Regular Meeting/midway_noise_compatibility_commission_meeting",
                    "chi_midway_noise/201707271830/Regular Meeting/midway_noise_compatibility_commission_meeting",
                    "chi_midway_noise/201710261830/Regular Meeting/midway_noise_compatibility_commission_meeting",
                    "chi_midway_noise/201801251830/Regular Meeting/midway_noise_compatibility_commission_meeting",
                    "chi_midway_noise/201801301830/Executive Committee Meeting/midway_noise_compatibility_commission_meeting",
                    "chi_midway_noise/201804261830/Regular Meeting/midway_noise_compatibility_commission_meeting",
                    "chi_midway_noise/201807261830/Regular Meeting/midway_noise_compatibility_commission_meeting",
                    "chi_midway_noise/201810251830/Regular Meeting/midway_noise_compatibility_commission_meeting",
                    "chi_midway_noise/201901241830/Regular Meeting/midway_noise_compatibility_commission_meeting",
                    "chi_midway_noise/201904251830/Regular Meeting/midway_noise_compatibility_commission_meeting",
                    "chi_midway_noise/201907251830/Regular Meeting/midway_noise_compatibility_commission_meeting",
                    "chi_midway_noise/201910241830/Regular Meeting/midway_noise_compatibility_commission_meeting"
                    ]

    for i in range(len(parsed_items)):
        assert parsed_items[i]["id"] == expected_ids[i]


def test_status():
    expected_statuses = [PASSED for i in range(33)]
    expected_statuses.append(TENTATIVE)
    for j in range(len(parsed_items)):
        assert parsed_items[j]["status"] == expected_statuses[j]


@pytest.mark.parametrize("item", parsed_items)
def test_location(item):
    assert item["location"] == {
        "name": "The Mayfield",
        "address": "6072 S. Archer Ave., Chicago, IL 60638"
    }


@pytest.mark.parametrize("item", parsed_items)
def test_source(item):
    assert item["source"] == "https://www.flychicago.com/community/MDWnoise/AdditionalResources/pages/default.aspx"


def test_links():
    expected_links = []
    expected_links.append([{'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/MeetingAgenda2013.01.24.pdf', 'title': 'Agenda'},  # January 24, 2013
                           {'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/MeetingMinutes2013.01.24.pdf', 'title': 'Minutes'}])

    expected_links.append([{'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/MeetingAgenda2013.02.28.pdf', 'title': 'Agenda'},  # February 28, 2013
                           {'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/MeetingMinutes2013.02.28.pdf', 'title': 'Minutes'}])

    expected_links.append([{'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/MeetingAgenda2013.04.02.pdf', 'title': 'Agenda'},  # April 2, 2013
                           {'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/MeetingMinutes2013.04.02.pdf', 'title': 'Minutes'}])

    expected_links.append([{'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/MeetingAgenda2013.04.25.pdf', 'title': 'Agenda'},  # April 25, 2013
                           {'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/MeetingMinutes2013.04.25.pdf', 'title': 'Minutes'}])

    expected_links.append([{'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/MeetingAgenda2013.07.25.pdf', 'title': 'Agenda'},  # July 25, 2013
                           {'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/MeetingMinutes20130725Final.pdf', 'title': 'Minutes'}])

    expected_links.append([{'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/2013.10MeetingAgendaResidential.pdf', 'title': 'Agenda'},  # October 22, 2013
                           {'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/MeetingMinutes2013.10.22%20FINAL.pdf', 'title': 'Minutes'}])

    expected_links.append([{'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/2013.10MeetingAgenda.pdf', 'title': 'Agenda'},  # October 24, 2013
                           {'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/MeetingMinutes2013.10.24.pdf', 'title': 'Minutes'}])

    expected_links.append([{'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/MeetingAgenda2014.01.23.pdf', 'title': 'Agenda'},  # January 23, 2014
                           {'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/MeetingMinutes2014.01.23%20FINAL.pdf', 'title': 'Minutes'}])

    expected_links.append([{'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/2014.04MeetingAgenda.pdf', 'title': 'Agenda'},  # April 24, 2014
                           {'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/MeetingMinutes2014.04.24%20FINAL.pdf', 'title': 'Minutes'}])

    expected_links.append([{'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/201407%20Meeting%20Agenda.pdf', 'title': 'Agenda'},  # July 24, 2014
                           {'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/MeetingMinutes2014.07.24%20FINAL.pdf', 'title': 'Minutes'}])

    expected_links.append([{'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/201410MeetingAgenda.pdf', 'title': 'Agenda'},  # October 23, 2014
                           {'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/MeetingMinutes2014.10.23%20FINAL.pdf', 'title': 'Minutes'}])

    expected_links.append([{'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/201501MeetingAgenda.pdf', 'title': 'Agenda'},  # January 22, 2015
                           {'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/MeetingMinutes2015.01.22FINAL.pdf', 'title': 'Minutes'}])

    expected_links.append([{'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/2015.04MeetingAgenda.pdf', 'title': 'Agenda'},  # April 23, 2015
                           {'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/MeetingMinutes2015.04.23FINAL.pdf', 'title': 'Minutes'}])

    expected_links.append([{'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/2015.07MeetingAgenda.pdf', 'title': 'Agenda'},  # July​ 23, 2015
                           {'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/MeetingMinutes_2015.07.23_FINAL.pdf', 'title': 'Minutes'}])

    expected_links.append([{'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/2015.10_Meeting_Agenda.pdf', 'title': 'Agenda'},  # October 22, 2015
                           {'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/MeetingMinutes_2015.10.22_FINAL.pdf', 'title': 'Minutes'}])

    expected_links.append([{'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/2016.01_Meeting_Agenda.pdf', 'title': 'Agenda'},  # January 28, 2016
                           {'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/Meeting_Minutes_2016.01.28_FINAL.pdf', 'title': 'Minutes'}])

    expected_links.append([{'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/2016.04MeetingAgenda.pdf', 'title': 'Agenda'},  # April 28, 2016
                           {'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/MeetingMinutes2016.04.28FINAL.pdf', 'title': 'Minutes'}])

    expected_links.append([{'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/2016.07.26ExecCmteMeetingAgenda.pdf', 'title': 'Agenda'}])  # July 26, 2016

    expected_links.append([{'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/2016.07MeetingAgenda.pdf', 'title': 'Agenda'},  # July 28, 2016
                           {'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/MeetingMinutes2016.07.28FINAL.pdf', 'title': 'Minutes'}])

    expected_links.append([{'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/2016.10MeetingAgenda.pdf', 'title': 'Agenda'},  # October 27, 2016
                           {'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/MeetingMinutes2016-10-27FINAL.pdf', 'title': 'Minutes'}])

    expected_links.append([{'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/2017.01_Residential_Meeting_Agenda.pdf', 'title': 'Agenda'}])  # January 23, 2017

    expected_links.append([{'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/2017.01_Meeting_Agenda.pdf', 'title': 'Agenda'},  # January 26, 2017
                           {'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/Meeting_Minutes_2017.01.26_FINAL.pdf', 'title': 'Minutes'}])

    expected_links.append([{'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/2017.04_Meeting_Agenda.pdf', 'title': 'Agenda'},  # April 27, 2017
                           {'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/Meeting_Minutes_2017.04.27_FINAL.pdf', 'title': 'Minutes'}])

    expected_links.append([{'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/2017.07_Meeting_Agenda.pdf', 'title': 'Agenda'},  # July 27, 2017
                           {'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/Meeting_Minutes_2017.07.27_FINAL.pdf', 'title': 'Minutes'}])

    expected_links.append([{'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/2017.10_Meeting_Agenda.pdf', 'title': 'Agenda'},  # October 26, 2017
                           {'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/Meeting_Minutes_2017.10.26_FINAL.pdf', 'title': 'Minutes'}])

    expected_links.append([{'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/2018.01_Meeting_Agenda.pdf', 'title': 'Agenda'},  # January 25, 2018
                           {'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/MeetingMinutes2018.01.25FINAL.pdf', 'title': 'Minutes'}])

    expected_links.append([{'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/2018.01_MeetingAgendaExecCmte.pdf', 'title': 'Agenda'}])  # January 30, 2018

    expected_links.append([{'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/2018.04_Meeting_Agenda.pdf', 'title': 'Agenda'}])  # April 26, 2018

    expected_links.append([{'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/2018.07.26_Meeting_Agenda.pdf', 'title': 'Agenda'}])  # July 26, 2018

    expected_links.append([{'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/2018.10_Meeting_Agenda.pdf', 'title': 'Agenda'}])  # October 25, 2018

    expected_links.append([{'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/2019.01_Meeting_Agenda.pdf', 'title': 'Agenda'},  # January 24, 2019
                           {'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/Meeting_Minutes_2019.01.24_FINAL.pdf', 'title': 'Minutes'}])

    expected_links.append([{'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/2019.04_Meeting_Agenda.pdf', 'title': 'Agenda'}])  # April 25, 2019

    expected_links.append([{'href': 'https://www.flychicago.com/SiteCollectionDocuments/Community/Noise/Midway/AR/2019.07_Meeting_Agenda.pdf', 'title': 'Agenda'}])  # July 25, 2019

    expected_links.append([])  # October 24, 2019 - this one is in the future and has no documents yet.

    for i in range(len(parsed_items)):
        assert parsed_items[i]["links"] == expected_links[i]


@pytest.mark.parametrize("item", parsed_items)
def test_classification(item):
    assert item["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
