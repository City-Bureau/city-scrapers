from datetime import datetime, time
from unittest.mock import MagicMock

import pytest  # noqa
from freezegun import freeze_time

from city_scrapers.mixins import DetCityMixin


class MockDetCitySpider(DetCityMixin):
    agency_cal_id = '1000'


def test_start_urls():
    freezer = freeze_time('2019-02-22')
    freezer.start()
    spider = MockDetCitySpider()
    assert '2018-10-25' in spider.start_urls[0]
    assert '1000' in spider.start_urls[0]
    freezer.stop()


def test_parse_title():
    response_mock = MagicMock()
    title_mock = MagicMock()
    title_mock.extract_first.return_value = 'Test Meeting 2019-01-01'
    response_mock.css.return_value = title_mock
    spider = MockDetCitySpider()
    assert spider._parse_title(response_mock) == 'Test Meeting'


def test_parse_start_end():
    response_mock = MagicMock()
    dt_mock = MagicMock()
    dt_mock.extract_first.return_value = '2019-01-01T10:10:10'
    dt_mock.extract.return_value = ['   \n', ' 9:10M - 2:00 p.m.']
    response_mock.css.return_value = dt_mock
    spider = MockDetCitySpider()
    assert spider._parse_start(response_mock) == datetime(2019, 1, 1, 9, 10)
    assert spider._parse_end(response_mock, datetime(2019, 1, 1, 9,
                                                     10))[0] == datetime(2019, 1, 1, 14)


def test_parse_time_str():
    spider = MockDetCitySpider()
    assert spider._parse_time_str('from 11:11a.m.') == time(11, 11)
    assert spider._parse_time_str('1pm') == time(13)


def test_create_document_date_map():
    spider = MockDetCitySpider()
    spider.document_links = [
        {
            'title': '2019 01 01 Test Item',
            'href': 'https://example.com'
        },
        {
            'title': 'June 1., 2019 Test',
            'href': 'https://example.com'
        },
    ]
    spider._create_document_date_map()
    assert spider.document_date_map[datetime(2019, 1, 1).date()] == [{
        'title': '2019 01 01 Test Item',
        'href': 'https://example.com'
    }]
    assert spider.document_date_map[datetime(2019, 6, 1).date()] == [{
        'title': 'June 1., 2019 Test',
        'href': 'https://example.com'
    }]


def test_replace_agency_doc_param():
    spider = MockDetCitySpider()
    spider.agency_doc_id = ['1111', '2222']
    assert spider._replace_agency_doc_param(
        'https://detroitmi.gov/documents?field_department_target_id_1[0][target_id]=1111&page=2'
    ) == 'https://detroitmi.gov/documents?field_department_target_id_1%5B0%5D%5Btarget_id%5D=2222'
