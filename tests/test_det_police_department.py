from datetime import time, date
from urllib.parse import parse_qsl

import pytest
import scrapy

from city_scrapers.spiders.det_police_department import DetPoliceDepartmentSpider
from tests.files.det_police_department_post import POST_REQUEST_RESPONSE_BODY
from tests.utils import file_response

initial_response = file_response('files/det_police_department_detroit_police_commissioners_meetings.html')
spider = DetPoliceDepartmentSpider()
POST_REQUEST_RESPONSE = scrapy.http.TextResponse(
    url="http://www.detroitmi.gov/Government/Detroit-Police-Commissioners-Meetings",
    body=POST_REQUEST_RESPONSE_BODY,
    encoding='utf-8'
)


def test_initial_request():
    initial_requests = list(spider.parse(initial_response))
    assert len(initial_requests) == 1

    form_request = initial_requests[0]
    prev_call_count = form_request.meta.get('prev_call_count')
    params = parse_qsl(form_request.body.decode(form_request.encoding))

    assert prev_call_count == 1
    # ASP.NET page so expansion of accordions has to be
    # done via form request so make sure updated form
    # params are in request
    assert ('ctx', '1') in params
    assert ('__DNNCAPISCI', 'FAQs dnn_ctr7392_FAQs') in params
    assert ('__DNNCAPISCP', '1716') in params


def test_convert_response():
    # response body of post request returns unevaluated html in
    # the text area tag. Convert table to a response to have access
    # to various scrapy selectors / parsing
    parsable_response = spider._convert_response(POST_REQUEST_RESPONSE)
    assert len(parsable_response.xpath('//tr[position() > 1]').extract()) != 0


test_response = spider._convert_response(POST_REQUEST_RESPONSE)
parsed_items = [item for item in spider._parse_item(test_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[0]['name'] == 'Board of Commissioners'


def test_description():
    assert parsed_items[0]['event_description'] == 'Swearing-in Ceremony'


def test_start():
    assert parsed_items[0]['start'] == {
        'date': date(2018, 1, 4),
        'time': time(15, 00),
        'note': ''
    }


def test_end():
    assert parsed_items[0]['end'] == {
        'date': None, 'time': None, 'note': ''
    }


def test_id():
    assert parsed_items[0]['id'] == 'det_police_department/201801041500/x/board_of_commissioners'


def test_status():
    assert parsed_items[0]['status'] == 'passed'


def test_location():
    det_public_safety_hq = {'neigborhood': '', 'name': 'Detroit Public Safety Headquarters',
                            'address': '1301 3rd Ave, Detroit, MI 48226'}
    community = {'neigborhood': '', 'name': '', 'address': 'In the community (see website for details)'}
    public_safety_meetings = [item['location'] for item in parsed_items if item['start']['time'] == time(15, 00)]
    community_meetings = [item['location'] for item in parsed_items if item['start']['time'] != time(15, 00)]
    assert all([location == det_public_safety_hq for location in public_safety_meetings])
    assert all([location == community for location in community_meetings])


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url': 'http://www.detroitmi.gov/Government/Detroit-Police-Commissioners-Meetings',
        'note': '',
    }]


def test_documents():
    assert parsed_items[0]['documents'] == []


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == 'Board'


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'
