import pytest
import datetime

from tests.utils import file_response
from city_scrapers.spiders.alle_county import AlleCountySpider

spider = AlleCountySpider()
test_response = file_response('files/alle_county_Calendar.html',
                              url=('https://alleghenycounty'
                                   '.legistar.com/Calendar.aspx'))
parsed_items = ([item for item in spider.parse(test_response)
                if isinstance(item, dict)])


@pytest.mark.parametrize('item',
                         [parsed_items[0]['name']])
def test_name(item):
    assert item == 'County Council'


def test_description():
    assert parsed_items[0]['event_description'] == ''


def test_start():
    assert (parsed_items[0]['start_time'] ==
            {'date': datetime.date(2018, 11, 15),
             'time': datetime.time(17, 0),
             'note': ''})


def test_end():
    assert (parsed_items[0]['end_time'] ==
            {'date': datetime.date(2018, 11, 15),
             'time': datetime.time(20, 0),
             'note': 'Estimated 3 hours after start time'})


def test_id():
    assert (parsed_items[0]['id'] ==
            'alle_county/201811151700/x/county_council')


def test_status():
    assert parsed_items[0]['status'] == 'passed'


def test_location():
    assert (parsed_items[0]['location'] ==
            {'address': ('2018 Budget Public Hearing, '
                         'Fourth Floor, Gold Room\r\nBudget & '
                         'Finance Chair Paul Klein Presiding, '
                         '436 Grant Street, Pittsburgh, PA 15219'),
             'name': '',
             'neighborhood': ''})


def test_sources():
    assert (parsed_items[0]['sources'] ==
            [{'url': ('https://alleghenycounty.'
                      'legistar.com/DepartmentDetail.aspx?'
                      'ID=26127&GUID=0B26890F-A762-408F-A03C'
                      '-110A9BD4CAD9'),
              'note': ''}])


def test_documents():
    assert (parsed_items[0]['documents'][0]['url'] ==
            ('https://alleghenycounty.'
             'legistar.com/MeetingDetail.aspx?ID=651745&GUID=63EDD993-558F'
             '-4CC7-9E2A-2D11E82DA693&Options=info&Search='))


@pytest.mark.parametrize('item',
                         [parsed_items[0]['all_day']])
def test_all_day(item):
    assert item is False


def test_classification():
    assert parsed_items[0]['classification'] == 'Forum'


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'
