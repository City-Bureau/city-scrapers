from datetime import datetime

import pytest
from city_scrapers_core.constants import ADVISORY_COMMITTEE, BOARD, COMMITTEE, PASSED
from tests.utils import file_response

from city_scrapers.spiders.det_regional_transit_authority import DetRegionalTransitAuthoritySpider

test_response = file_response(
    'files/det_regional_transit_authority.html',
    url='http://www.rtamichigan.org/board-and-committee-meetings/'
)
spider = DetRegionalTransitAuthoritySpider()
parsed_items = [item for item in spider.parse(test_response)]


def test_count():
    # 7 committees * 12 mo (exclude on TBD meeting)
    assert len(parsed_items) == 83


def test_title():
    assert parsed_items[0]['title'] == 'Board of Directors'


def test_all_committees():
    titles = {item['title'] for item in parsed_items}
    assert titles == {
        'Board of Directors', 'Citizens Advisory Committee', 'Executive and Policy Committee',
        'Finance and Budget Committee', 'Funding Allocation Committee',
        'Planning and Service Coordination Committee', 'Providers Advisory Council'
    }


def test_description():
    assert parsed_items[0]['description'] == ''


def test_start():
    assert parsed_items[0]['start'] == datetime(2018, 1, 25, 12)
    assert parsed_items[-1]['start'] == datetime(2018, 12, 13, 10)


def test_end():
    assert parsed_items[0]['end'] is None


def test_id():
    assert parsed_items[0]['id'
                           ] == 'det_regional_transit_authority/201801251200/x/board_of_directors'


def test_status():
    assert parsed_items[0]['status'] == PASSED


def test_location():
    assert parsed_items[0]['location'] == spider.location


def test_source():
    assert parsed_items[0]['source'] == 'http://www.rtamichigan.org/board-and-committee-meetings/'


def test_links():
    item = [
        item for item in parsed_items if item['title'] == 'Finance and Budget Committee'
        and item['start'].date() == datetime(2018, 1, 25).date()
    ][0]
    assert item['links'] == [
        {
            'href': 'https://drive.google.com/open?id=1rycPraD6eINTXUApH6bCR4lpdz8UqVJq',
            'title': 'DATE/TIME CHANGE'
        },
        {
            'href': 'https://drive.google.com/open?id=1FbQG4lt3NFQFDKfT82hfV5mstahkJj9j',
            'title': 'Agenda & Documents'
        },
        {
            'href':
                'https://drive.google.com/file/d/1Iu12ploe2-ltpPjB-sBgWievmDl49q60/view?usp=sharing',  # noqa
            'title': 'Meeting Summary'
        },
    ]


def test_classification():
    bod = [item for item in parsed_items if item['title'] == 'Board of Directors'][0]
    ca = [item for item in parsed_items if item['title'] == 'Citizens Advisory Committee'][0]
    epc = [item for item in parsed_items if item['title'] == 'Executive and Policy Committee'][0]
    assert bod['classification'] == BOARD
    assert ca['classification'] == ADVISORY_COMMITTEE
    assert epc['classification'] == COMMITTEE


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False
