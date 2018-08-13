import urllib
from datetime import date, time
from urllib.parse import parse_qsl

import pytest
import scrapy

from city_scrapers.spiders.det_city_council import DetCityCouncilSpider
from tests.utils import file_response

test_response = file_response('files/det_city_council.html')
spider = DetCityCouncilSpider()


def test_request_count():
    requests = list(spider.parse(test_response))
    number_next_page_request = 1
    event_requests = 34
    assert len(requests) == number_next_page_request + event_requests

    all_calendar_events = {urllib.parse.unquote(request.url) for request in requests if 'Details' in request.url}
    select_calendar_events = {
        "http://www.detroitmi.gov/Government/City-Council/City-Council-Sessions/ModuleID/8319/ItemID/6552/mctl/EventDetails",
        "http://www.detroitmi.gov/Government/City-Council/City-Council-Sessions/ModuleID/8319/ItemID/6580/mctl/EventDetails",
        "http://www.detroitmi.gov/Government/City-Council/City-Council-Sessions/ModuleID/8319/ItemID/6573/mctl/EventDetails",
        "http://www.detroitmi.gov/Government/City-Council/City-Council-Sessions/ModuleID/8319/ItemID/6585/mctl/EventDetails",
    }
    assert select_calendar_events.issubset(all_calendar_events)

    form_requests = [request for request in requests if isinstance(request, scrapy.FormRequest)]
    assert len(form_requests) == 1

    form_request = form_requests[0]
    months_crawled = form_request.meta.get('months_crawled')
    params = parse_qsl(form_request.body.decode(form_request.encoding))

    assert months_crawled == 1
    # ASP.NET page paging has to be done via form request
    # so make sure updated form params are in request
    assert ('__EVENTTARGET', 'dnn$ctr8319$Events$EventMonth$EventCalendar') in params
    assert ('__EVENTARGUMENT', 'V6787') in params


test_detail = file_response(
    'files/det_city_council_detail.html',
    'http://www.detroitmi.gov/Government/City-Council/City-Council-Sessions/ModuleID/8319/ItemID/6556/mctl/EventDetails'
)
parsed_items = [item for item in spider._parse_item(test_detail) if isinstance(item, dict)]


def test_name():
    assert parsed_items[0]['name'] == 'Planning & Economic Development'


def test_description():
    assert parsed_items[0]['event_description'] == \
           'The Detroit City Council has scheduled an PLANNING & ECONOMIC ' \
           'DEVELOPMENT COMMITTEE to be held on Thursday, July 5, ' \
           '2018 at 10:00 a.m.  in the Committee of the Whole Room, ' \
           '13th floor, Coleman A. Young Municipal Center.'


def test_start():
    assert parsed_items[0]['start'] == {
        'date': date(2018, 7, 5), 'time': time(10, 00), 'note': ''
    }


def test_end():
    assert parsed_items[0]['end'] == {
        'date': None, 'time': None, 'note': ''
    }


def test_id():
    assert parsed_items[0]['id'] == 'det_city_council/201807051000/x/planning_economic_development'


def test_status():
    assert parsed_items[0]['status'] == 'passed'


def test_location():
    assert parsed_items[0]['location'] == {
        'neighborhood': '',
        'name': 'Coleman A. Young Municipal Center',
        'address': '2 Woodward Detroit, MI 48226'
    }


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url': 'http://www.detroitmi.gov/Government/City-Council/City-Council-Sessions/ModuleID/8319/ItemID/6556/mctl/EventDetails',
        'note': ''
    }]


def test_documents():
    assert parsed_items[0]['documents'] == [
        {
            'url': "http://www.detroitmi.gov/Portals/0/docs/City Clerk/Council 2018/Planning Economic/CAL 07-5-18 PED.pdf?ver=2018-07-03-164858-537",
            'note': 'PLANNING & ECONOMIC DEVELOPMENT Agenda'
        }
    ]


def test_choose_location():
    assert spider._choose_location("Other") == {'neighborhood': '', 'name': '', 'address': "Other"}
    assert spider._choose_location("Young Municipal Center and stuff") == {
                'neighborhood': '',
                'name': 'Coleman A. Young Municipal Center',
                'address': '2 Woodward Detroit, MI 48226'
            }


def test_classification():
    assert parsed_items[0]['classification'] == 'Committee'


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'
