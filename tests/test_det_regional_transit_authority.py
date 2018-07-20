from datetime import date, time

import pytest

from city_scrapers.spiders.det_regional_transit_authority import DetRegionalTransitAuthoritySpider
from tests.utils import file_response

test_response = file_response('files/det_regional_transit_authority.html',
                              'http://www.rtamichigan.org/board-and-committee-meetings/')
spider = DetRegionalTransitAuthoritySpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_count():
    # 7 committees * 12 mo (exclude on TBD meeting)
    a = parsed_items
    assert len(parsed_items) == 83


def test_name():
    assert parsed_items[0]['name'] == 'Board of Directors'


def test_all_committees():
    names = {item['name'] for item in parsed_items}
    assert names == {'Board of Directors',
                     'Citizens Advisory Committee',
                     'Executive and Policy Committee',
                     'Finance and Budget Committee',
                     'Funding Allocation Committee',
                     'Planning and Service Coordination Committee',
                     'Providers Advisory Council'
                     }


def test_description():
    assert parsed_items[0]['event_description'] == ''


def test_start():
    assert parsed_items[0]['start'] == {
        'date': date(2018, 1, 25),
        'time': time(12, 0),
        'note': ''
    }
    assert parsed_items[-1]['start'] == {
        'date': date(2018, 12, 13),
        'time': time(10, 0),
        'note': ''
    }


def test_end():
    assert parsed_items[0]['end'] == {
        'date': None,
        'time': None,
        'note': ''
    }


def test_id():
    assert parsed_items[0]['id'] == 'det_regional_transit_authority/201801251200/x/board_of_directors'


def test_status():
    assert parsed_items[0]['status'] == 'passed'


def test_location():
    assert parsed_items[0]['location'] == {
        'neighborhood': '',
        'name': 'RTA Office',
        'address': '1001 Woodward Avenue, Suite 1400, Detroit, MI 48226'
    }


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url': 'http://www.rtamichigan.org/board-and-committee-meetings/',
        'note': ''
    }]


def test_documents():
    item = [item for item in parsed_items
            if item['name'] == 'Finance and Budget Committee'
            and item['start']['date'] == date(2018, 1, 25)][0]
    assert item['documents'] == [
        {
            'url': 'https://drive.google.com/open?id=1rycPraD6eINTXUApH6bCR4lpdz8UqVJq',
            'note': 'DATE/TIME CHANGE'
        },
        {
            'url': 'https://drive.google.com/open?id=1FbQG4lt3NFQFDKfT82hfV5mstahkJj9j',
            'note': 'Agenda & Documents'
        },
        {
            'url': 'https://drive.google.com/file/d/1Iu12ploe2-ltpPjB-sBgWievmDl49q60/view?usp=sharing',
            'note': 'Meeting Summary'
        },

    ]


def test_classification():
    bod = [item for item in parsed_items if item['name'] == 'Board of Directors'][0]
    ca = [item for item in parsed_items if item['name'] == 'Citizens Advisory Committee'][0]
    epc = [item for item in parsed_items if item['name'] == 'Executive and Policy Committee'][0]
    assert bod['classification'] == 'Board'
    assert ca['classification'] == 'Advisory Committee'
    assert epc['classification'] == 'Committee'


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert parsed_items[0]['_type'] == 'event'
