import json
from datetime import date, time
from urllib.parse import parse_qs

import pytest
from freezegun import freeze_time

from city_scrapers.constants import CITY_COUNCIL
from city_scrapers.spiders.chi_citycouncil import ChiCityCouncilSpider
from tests.utils import file_response, read_test_file_content

INITIAL_REQUEST = 'https://ocd.datamade.us/events/?' \
                  'start_date__gt=2017-10-16&' \
                  'jurisdiction=ocd-jurisdiction/country:us/state:il/place:chicago/government'

spider = ChiCityCouncilSpider()


@pytest.fixture('module')
def parsed_item():
    freezer = freeze_time('2018-01-01 12:00:01')
    freezer.start()
    item = file_response('files/chi_citycouncil_event.json', url=INITIAL_REQUEST)
    parsed = spider._parse_item(item)
    freezer.stop()
    return parsed


def test_parse():
    response = file_response('files/chi_citycouncil_feed.json', url=INITIAL_REQUEST)
    requests = list(spider.parse(response))
    assert len(requests) == 2


def test_gen_requests():
    test_response = json.loads(read_test_file_content('files/chi_citycouncil_feed.json'))
    event_requests = [item for item in spider._gen_requests(test_response)]
    assert event_requests == [
        'https://ocd.datamade.us/ocd-event/86094f46-cf45-46f8-89e2-0bf783e7aa12/',
        'https://ocd.datamade.us/ocd-event/93d62d20-b1dc-4d71-9e96-60c99c837e90/',
    ]


def test_addtl_pages():
    more = json.loads('{"meta": {"page": 1, "per_page": 100, "total_count": 160, "count": 100, "max_page": 2}}')
    assert spider._addtl_pages(more) is True
    no_more = json.loads('{"meta": {"page": 1, "per_page": 100, "total_count": 2, "count": 2, "max_page": 1}}')
    assert spider._addtl_pages(no_more) is False


def test_next_page():
    more = json.loads('{"meta": {"page": 1, "per_page": 100, "total_count": 160, "count": 100, "max_page": 2}}')
    original_params = parse_qs(INITIAL_REQUEST)
    next_page = spider._next_page(more)
    static_params = {k: v for k, v in original_params.items() if k != 'page'}
    assert static_params == original_params
    assert next_page == 2


def test_parse_documents():
    documents = [
        {
            "date": "",
            "note": "Notice",
            "links": [
                {
                    "url": "http://media.legistar.com/chic/meetings/633C3556-29C4-4645-A916-E767E00A98CC/Notice,%2003-22-2018.pdf",
                    "media_type": "application/pdf"
                }
            ]
        }
    ]
    assert spider._parse_documents(documents)[0] == \
           {'url': documents[0]['links'][0]['url'], 'note': "Notice"}


# Item fields
def test_start(parsed_item):
    expected_start = {
        'date': date(2017, 10, 16),
        'time': time(10, 00),
        'note': ''
    }
    assert parsed_item['start'] == expected_start


def test_end(parsed_item):
    expected_end = {
        'date': date(2017, 10, 16),
        'time': None,
        'note': ''
    }
    assert parsed_item['end'] == expected_end


def test_name(parsed_item):
    assert parsed_item['name'] == 'Joint Committee: Finance; Transportation and Public Way'


def test_description(parsed_item):
    assert parsed_item['event_description'] == ""


def test_location(parsed_item):
    expected_location = {'address': '121 N LaSalle Dr, Chicago, IL',
                         'name': 'Council Chambers ,  City Hall'}
    assert parsed_item['location'] == expected_location


def test_documents(parsed_item):
    assert parsed_item['documents'] == [{
        "url": "http://media.legistar.com/chic/meetings/B5103C52-1793-4B07-9F28-E0A1223E1540/Fin%20CANCELLED%2010-16_20171010085450.pdf",
        "note": "Cancellation Notice",
    }]


def test_id(parsed_item):
    assert parsed_item['id'] == \
           'chi_citycouncil/201710161000/ocd-event-86094f46-cf45-46f8-89e2-0bf783e7aa12/joint_committee_finance_transportation_and_public_way'


def test_all_day(parsed_item):
    assert parsed_item['all_day'] is False


def test_classification(parsed_item):
    assert parsed_item['classification'] == CITY_COUNCIL


def test_status(parsed_item):
    assert parsed_item['status'] == 'cancelled'


def test__type(parsed_item):
    assert parsed_item['_type'] == 'event'


def test_sources(parsed_item):
    expected_sources = [
        {
            "url": "http://webapi.legistar.com/v1/chicago/events/4954",
            "note": "api"
        },
        {
            "url": "https://chicago.legistar.com/MeetingDetail.aspx?ID=565455&GUID=B5103C52-1793-4B07-9F28-E0A1223E1540&Options=info&Search=",
            "note": "web"
        }
    ]
    assert parsed_item['sources'] == expected_sources
