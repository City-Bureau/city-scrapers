import pytest

import json
from documenters_aggregator.spiders.chi_citycouncil import Chi_citycouncilSpider

test_response = []
with open('tests/files/chi_citycouncil.json') as f:
    for line in f:
        test_response.append(json.loads(line))
spider = Chi_citycouncilSpider()
parsed_items = [spider._parse_item(item) for item in test_response[0]]


def test_name():
    assert parsed_items[0]['name'] == 'Joint Committee: Finance; Transportation and Public Way'


def test_description():
    assert parsed_items[0]['description'] == ''


def test_start_time():
    assert parsed_items[0]['start_time'].isoformat() == '2017-10-16T10:00:00-05:00'


def test_end_time():
    assert parsed_items[0]['end_time'] is None


def test_id():
    assert parsed_items[0]['id'] == 'chi_citycouncil/201710161000/ocd-event-86094f46-cf45-46f8-89e2-0bf783e7aa12/joint_committee_finance_transportation_and_public_way'


def test_all_day():
    assert parsed_items[0]['all_day'] is False


def test_classification():
    assert parsed_items[0]['classification'] == 'city council meeting'


def test_status():
    assert parsed_items[0]['status'] == 'cancelled'


def test__type():
    assert parsed_items[0]['_type'] == 'event'


def test_sources():
    EXPECTED_SOURCES = [{'note': 'ocd-api', 'url': 'https://ocd.datamade.us/ocd-event/86094f46-cf45-46f8-89e2-0bf783e7aa12/'},
                        {'note': 'web', 'url': 'https://chicago.legistar.com/MeetingDetail.aspx?ID=565455&GUID=B5103C52-1793-4B07-9F28-E0A1223E1540&Options=info&Search='},
                        {'note': 'api', 'url': 'http://webapi.legistar.com/v1/chicago/events/4954'}]
    assert parsed_items[0]['sources'] == EXPECTED_SOURCES


@pytest.mark.parametrize('item', parsed_items)
def test_timezone(item):
    assert item['timezone'] == 'America/Chicago'
