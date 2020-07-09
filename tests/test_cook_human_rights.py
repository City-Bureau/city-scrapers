from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.cook_human_rights import CookHumanRightsSpider

test_response = file_response(
    join(dirname(__file__), "files", "cook_human_rights.html"),
    url="https://www.cookcountyil.gov/event/cook-county-commission-human-rights-meeting-3",
)
test_response_filepage = file_response(
    join(dirname(__file__), "files", "cook_human_rights_file.html"),
    url="https://www.cookcountyil.gov/file/10402/",
)

spider = CookHumanRightsSpider()

freezer = freeze_time("2020-07-09")
freezer.start()
fake_formatted_date = datetime.strftime(
    datetime.strptime("July 2019", "%B %Y"), "%y-%m")
test_response_filepage.meta['formatted_date'] = fake_formatted_date
spider._parse_links(test_response_filepage)
parsed_items = spider._parse_event(test_response)

freezer.stop()


def test_title():
    assert parsed_items["title"] == "Commission on Human Rights"


def test_description():
    assert parsed_items["description"] == "Special Meeting of the Cook County Commission on Human Rights"


def test_start():
    assert parsed_items["start"] == datetime(2019, 7, 16, 11, 30)


def test_end():
    assert parsed_items["end"] == datetime(2019, 7, 16, 13, 30)


def test_time_notes():
    assert parsed_items["time_notes"] == "Regular meetings are held on the second Thursday of every other month"


def test_id():
    assert parsed_items["id"] == "cook_human_rights/201907161130/x/commission_on_human_rights"


def test_status():
    assert parsed_items["status"] == "passed"


def test_location():
    assert parsed_items["location"] == {
        "name": "",
        "address": "69 W. Washington Street, Suite 3040 Chicago IL 60602"
    }


def test_source():
    assert parsed_items["source"] == "https://www.cookcountyil.gov/event/cook-county-commission-human-rights-meeting-3"


def test_links():
    # Currently there is no Minutes published in last 6 months.
    assert parsed_items["links"] == [{'href': 'https://www.cookcountyil.gov/sites/default/files/july_16_2019_special_meeting_minutes_-_draft_-_sep_6_2019.pdf',
                                      'title': 'Minutes'}]


def test_classification():
    assert parsed_items["classification"] == COMMISSION


def test_all_day():
    assert parsed_items["all_day"] is False
