from datetime import date, time

import pytest

# Shared properties between two different page / meeting types
import scrapy
from freezegun import freeze_time

from city_scrapers.spiders.det_brownfield_redevelopment_authority import DetBrownfieldRedevelopmentAuthoritySpider
from tests.utils import file_response

LOCATION = {'neighborhood': '', 'name': 'DEGC, Guardian Building', 'address': '500 Griswold, Suite 2200, Detroit'}

DBRA = 'Board of Directors'
DBRA_CAC = 'Community Advisory Committee'

test_response = file_response('files/det_brownfield_redevelopment_authority.html',
                              'http://www.degc.org/public-authorities/dbra/')
freezer = freeze_time('2018-07-28 12:00:01')
spider = DetBrownfieldRedevelopmentAuthoritySpider()
freezer.start()
parsed_items = [item for item in spider._next_meeting(test_response) if isinstance(item, dict)]
freezer.stop()


def test_initial_request_count():
    items = list(spider.parse(test_response))
    assert len(items) == 5
    urls = {r.url for r in items if isinstance(r, scrapy.Request)}
    assert urls == {
        'http://www.degc.org/public-authorities/dbra/fy-2018-2019-notices-agendas-and-minutes/',
        'http://www.degc.org/public-authorities/dbra/fy-2017-2018-meetings/',
        'http://www.degc.org/public-authorities/dbra/dbra-fy-2016-2017-meetings/'
    }
    items = [i for i in items if isinstance(i, dict)]
    assert len(items) == 2


# current meeting http://www.degc.org/public-authorities/dbra/
def test_name():
    assert parsed_items[0]['name'] == DBRA
    assert parsed_items[1]['name'] == DBRA_CAC


def test_description():
    assert parsed_items[0]['event_description'] == ''


def test_start():
    assert parsed_items[0]['start'] == {
        'date': date(2018, 7, 25),
        'time': time(16, 00),
        'note': ''
    }
    assert parsed_items[1]['start'] == {
        'date': date(2018, 7, 25),
        'time': time(17, 00),
        'note': ''
    }


def test_end():
    assert parsed_items[0]['end'] == {
        'date': None,
        'time': None,
        'note': ''
    }


def test_id():
    assert parsed_items[0]['id'] == 'det_brownfield_redevelopment_authority/201807251600/x/board_of_directors'
    assert parsed_items[1]['id'] == 'det_brownfield_redevelopment_authority/201807251700/x/community_advisory_committee'


def test_status():
    assert parsed_items[0]['status'] == 'passed'


def test_location():
    assert parsed_items[0]['location'] == LOCATION


def test_sources():
    assert parsed_items[0]['sources'] == [
        {'url': 'http://www.degc.org/public-authorities/dbra/', 'note': ''}
    ]


def test_documents():
    assert parsed_items[0]['documents'] == []


def test_classification():
    assert parsed_items[0]['classification'] == 'Board'
    assert parsed_items[1]['classification'] == 'Advisory Committee'


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'


# # previous meetings e.g. http://www.degc.org/public-authorities/dbra/fy-2017-2018-meetings/
test_prev_response = file_response('files/det_brownfield_redevelopment_authority_prev.html',
                                   'http://www.degc.org/public-authorities/dbra/fy-2017-2018-meetings/')
parsed_prev_items = [item for item in spider._parse_prev_meetings(test_prev_response) if isinstance(item, dict)]
parsed_prev_items = sorted(parsed_prev_items, key=lambda x: x['start']['date'], reverse=True)


def test_request_count():
    requests = list(spider._prev_meetings(test_response))
    urls = {r.url for r in requests}
    assert len(requests) == 3
    assert urls == {
        'http://www.degc.org/public-authorities/dbra/fy-2018-2019-notices-agendas-and-minutes/',
        'http://www.degc.org/public-authorities/dbra/fy-2017-2018-meetings/',
        'http://www.degc.org/public-authorities/dbra/dbra-fy-2016-2017-meetings/'
    }


def test_prev_meeting_count():
    # 2017-2018 page (20 meetings)
    ids = {item['id'] for item in parsed_prev_items}
    assert len(parsed_prev_items) == 34
    assert len(ids) == 34


def test_prev_name():
    assert parsed_prev_items[0]['name'] == DBRA


def test_prev_description():
    assert parsed_prev_items[0]['event_description'] == ''


def test_prev_start():
    assert parsed_prev_items[0]['start'] == {
        'date': date(2018, 6, 27), 'time': None, 'note': ''
    }


def test_prev_end():
    assert parsed_prev_items[0]['end'] == {
        'date': None, 'time': None, 'note': ''
    }


def test_prev_id():
    assert parsed_prev_items[0]['id'] \
           == 'det_brownfield_redevelopment_authority/201806270000/x/board_of_directors'


def test_prev_status():
    assert parsed_prev_items[0]['status'] == 'passed'


def test_prev_location():
    assert parsed_prev_items[0]['location'] == LOCATION


def test_prev_sources():
    assert parsed_prev_items[0]['sources'] == [
        {'url': 'http://www.degc.org/public-authorities/dbra/fy-2017-2018-meetings/', 'note': ''}
    ]


def test_prev_documents():
    assert parsed_prev_items[0]['documents'] == [
        {
            'url': 'http://www.degc.org/wp-content/uploads/DBRA-062718-Regular-Meeting-Agenda-Only.pdf',
            'note': 'agenda',
        }
    ]


def test_prev_classification():
    assert parsed_prev_items[0]['classification'] == 'Board'
    assert parsed_prev_items[1]['classification'] == 'Advisory Committee'


@pytest.mark.parametrize('item', parsed_prev_items)
def test_prev_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_prev_items)
def test__prev_type(item):
    assert item['_type'] == 'event'
