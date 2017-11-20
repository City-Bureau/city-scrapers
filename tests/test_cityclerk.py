import json
from documenters_aggregator.spiders.cityclerk import CityclerkSpider

test_response = []
with open('tests/files/cityclerk.json') as f:
    for line in f:
        test_response.append(json.loads(line))
spider = CityclerkSpider()
parsed_items = [spider._parse_item(item) for item in test_response[0]]


def test_name():
    assert parsed_items[0]['name'] == 'Joint Committee: Finance; Transportation and Public Way'


def test_description():
    assert parsed_items[0]['description'] == ''


def test_start_time():
    assert parsed_items[0]['start_time'] == '2017-10-16T15:00:00+00:00'


def test_end_time():
    assert parsed_items[0]['end_time'] is None


def test_id():
    assert parsed_items[0]['id'] == 'cityclerk/201710161500/ocd-event-86094f46-cf45-46f8-89e2-0bf783e7aa12/joint_committee_finance_transportation_and_public_way'


def test_all_day():
    assert parsed_items[0]['all_day'] is False


def test_classification():
    assert parsed_items[0]['classification'] is None


def test_status():
    assert parsed_items[0]['status'] == 'cancelled'


def test__type():
    assert parsed_items[0]['_type'] == 'event'
