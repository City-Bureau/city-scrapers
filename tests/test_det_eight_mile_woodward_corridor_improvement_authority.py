from datetime import date, time

import pytest

from city_scrapers.spiders.det_eight_mile_woodward_corridor_improvement_authority import \
    DetEightMileWoodwardCorridorImprovementAuthoritySpider
from tests.utils import file_response

# Shared properties between two different page / meeting types
SOURCES = [{'url': 'http://www.degc.org/public-authorities/emwcia/', 'note': ''}]

LOCATION = {'neighborhood': '', 'name': 'DEGC, Guardian Building', 'address': '500 Griswold, Suite 2200, Detroit'}

NAME = 'Eight Mile Woodward Corridor Improvement Authority'

test_response = file_response('files/det_eight_mile_woodward_corridor_improvement_authority.html',
                              'http://www.degc.org/public-authorities/emwcia/')
spider = DetEightMileWoodwardCorridorImprovementAuthoritySpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


# current meeting (e.g. http://www.degc.org/public-authorities/emwcia/)
def test_name():
    assert parsed_items[0]['name'] == NAME


def test_description():
    assert parsed_items[0]['event_description'] == ''


def test_start():
    assert parsed_items[0]['start'] == {
        'date': date(2018, 8, 14), 'time': time(14, 00), 'note': ''
    }


def test_end():
    assert parsed_items[0]['end'] == {
        'date': None, 'time': None, 'note': ''
    }


def test_id():
    assert parsed_items[0][
               'id'] == 'det_eight_mile_woodward_corridor_improvement_authority/201808141400/x/eight_mile_woodward_corridor_improvement_authority'


def test_status():
    assert parsed_items[0]['status'] == 'tentative'


def test_location():
    assert parsed_items[0]['location'] == LOCATION


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url': 'http://www.degc.org/public-authorities/emwcia/',
        'note': ''
    }]


def test_documents():
    assert parsed_items[0]['documents'] == []


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] is 'Board'


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'


# previous meetings e.g. http://www.degc.org/public-authorities/emwcia/emwcia-fy-2016-2017-meetings/
test_prev_response = file_response('files/det_eight_mile_woodward_corridor_improvement_authority_prev.html',
                                   'http://www.degc.org/public-authorities/emwcia/')
parsed_prev_items = [item for item in spider._parse_previous(test_prev_response) if isinstance(item, dict)]


def test_requests():
    requests = list(spider._prev_meetings(test_response))
    urls = {r.url for r in requests}
    assert len(requests) == 2
    assert urls == {
        'http://www.degc.org/public-authorities/emwcia/fy-2017-2018-meetings/',
        'http://www.degc.org/public-authorities/emwcia/emwcia-fy-2016-2017-meetings/'
    }


def test_prev_meeting_count():
    # only looking at 2016-2017 page (4 meetings)
    assert len(parsed_prev_items) == 4


def test_prev_name():
    assert parsed_prev_items[0]['name'] == NAME


def test_prev_description():
    assert parsed_prev_items[0]['event_description'] == ''


def test_prev_start():
    assert parsed_prev_items[0]['start'] == {
        'date': date(2017, 6, 13), 'time': None, 'note': ''
    }


def test_prev_end():
    assert parsed_prev_items[0]['end'] == {
        'date': None, 'time': None, 'note': ''
    }


def test_prev_id():
    assert parsed_prev_items[0][
               'id'] == 'det_eight_mile_woodward_corridor_improvement_authority/201706130000/x/eight_mile_woodward_corridor_improvement_authority'


def test_prev_status():
    assert parsed_prev_items[0]['status'] == 'passed'


def test_prev_location():
    assert parsed_prev_items[0]['location'] == LOCATION


def test_prev_sources():
    assert parsed_prev_items[0]['sources'] == SOURCES


def test_prev_documents():
    assert parsed_prev_items[0]['documents'] == [
        {
            'url': 'http://www.degc.org/wp-content/uploads/2017-06-13-EMWCIA-Board-Meeting-Agenda.pdf',
            'note': 'agenda',
        },
        {
            'url': 'http://www.degc.org/wp-content/uploads/2017-06-13-EMWCIA-Board-Meeting-Minutes.pdf',
            'note': 'minutes',
        },
    ]


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] is 'Board'


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'
