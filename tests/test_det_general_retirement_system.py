import urllib
from datetime import date, time
from urllib.parse import parse_qsl

import pytest
import scrapy
from freezegun import freeze_time

from city_scrapers.constants import BOARD, NOT_CLASSIFIED
from city_scrapers.spiders.det_general_retirement_system import DetGeneralRetirementSystemSpider
from tests.utils import file_response

test_response = file_response('files/det_general_retirement_system_meetings.html',
                              'http://www.rscd.org/grsd/Resources/Meetings')

spider = DetGeneralRetirementSystemSpider()


def test_request_count():
    requests = list(spider.parse(test_response))
    assert len(requests) == 5

    calendar_events_urls = {urllib.parse.unquote(request.url) for request in requests if 'Details' in request.url}
    assert calendar_events_urls == {
        "http://www.rscd.org/grsd/Resources/Meetings/ctl/Details/Mid/531/ItemID/218?ContainerSrc=[G]Containers/RSCD/Plain-NoTitle",
        "http://www.rscd.org/grsd/Resources/Meetings/ctl/Details/Mid/531/ItemID/1552?ContainerSrc=[G]Containers/RSCD/Plain-NoTitle",
        "http://www.rscd.org/grsd/Resources/Meetings/ctl/Details/Mid/531/ItemID/1285?ContainerSrc=[G]Containers/RSCD/Plain-NoTitle",
        "http://www.rscd.org/grsd/Resources/Meetings/ctl/Details/Mid/531/ItemID/223?ContainerSrc=[G]Containers/RSCD/Plain-NoTitle",
    }

    form_requests = [request for request in requests if isinstance(request, scrapy.FormRequest)]
    assert len(form_requests) == 1

    form_request = form_requests[0]
    prev_call_count = form_request.meta.get('prev_call_count')
    params = parse_qsl(form_request.body.decode(form_request.encoding))

    assert prev_call_count == 1
    # ASP.NET page paging has to be done via form request
    # so make sure updated form params are in request
    assert ('__EVENTTARGET', 'dnn$ctr531$Events$EventMonth$EventCalendar') in params
    assert ('__EVENTARGUMENT', 'V6818') in params


test_detail = file_response(
    'files/det_general_retirement_system_meetings_detail.html',
    'http://www.rscd.org/grsd/Resources/Meetings/ctl/Details/Mid/531/ItemID/1552?ContainerSrc=[G]Containers/RSCD/Plain-NoTitle'
)
freezer = freeze_time('2018-07-31 12:00:01')
freezer.start()
parsed_items = [item for item in spider._parse_item(test_detail) if isinstance(item, dict)]
freezer.stop()


def test_name():
    assert parsed_items[0]['name'] == 'Board of Trustees: Board Meeting'


def test_description():
    assert parsed_items[0]['event_description'] == \
           'Board of Trustees of the General Retirement System of the City of Detroit.'


def test_start():
    assert parsed_items[0]['start'] == {
        'date': date(2018, 8, 1), 'time': time(10, 00), 'note': ''
    }


def test_end():
    assert parsed_items[0]['end'] == {
        'date': None, 'time': None, 'note': ''
    }


def test_id():
    assert parsed_items[0]['id'] == 'det_general_retirement_system/201808011000/x/board_of_trustees_board_meeting'


def test_status():
    assert parsed_items[0]['status'] == 'confirmed'


def test_location():
    """
    Retirement Systems' Conference Room, Ally Detroit Center
    500 Woodward Ave., Suite 3000 Detroit, Michigan 48226
    """
    assert parsed_items[0]['location'] == {
        'neighborhood': '',
        'name': "Retirement Systems' Conference Room, Ally Detroit Center",
        'address': '500 Woodward Ave., Suite 3000 Detroit, Michigan 48226'
    }


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url': 'http://www.rscd.org/grsd/Resources/Meetings/ctl/Details/Mid/531/ItemID/1552?ContainerSrc=[G]Containers/RSCD/Plain-NoTitle',
        'note': ''
    }]


def test_documents():
    assert parsed_items[0]['documents'] == []


def test_classification():
    assert parsed_items[0]['classification'] == BOARD


def test_parse_classification():
    assert spider._parse_classification('EBP Meeting') == NOT_CLASSIFIED
    assert spider._parse_classification('Board Meeting') == BOARD


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'
