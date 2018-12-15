import datetime

import pytest
from tests.utils import file_response

from city_scrapers.spiders.alle_port_authority import AllePortAuthoritySpider

test_response = file_response(
    'files/alle_port_authority_MeetingAgendasResolutions.html',
    url=(
        'https://www.portauthority.org/paac/CompanyInfoProjects/'
        'BoardofDirectors/MeetingAgendasResolutions.aspx'
    )
)

spider = AllePortAuthoritySpider()
parsed_items = [item for item in spider.parse(test_response)]


def test_name():
    assert parsed_items[0]['name'] == 'Annual Meeting'


def test_description():
    assert parsed_items[0]['event_description'] == ''


def test_start():
    assert (
        parsed_items[0]['start'] == {
            'date': datetime.date(2018, 1, 26),
            'time': datetime.time(9, 30),
            'note': ''
        }
    )


def test_end():
    assert (
        parsed_items[0]['end'] == {
            'date': datetime.date(2018, 1, 26),
            'time': datetime.time(12, 30),
            'note': 'Estimated 3 hours after start time'
        }
    )


def test_id():
    assert (parsed_items[0]['id'] == 'alle_port_authority/201801260930/x/annual_meeting')


def test_status():
    assert parsed_items[0]['status'] == 'passed'


def test_location():
    assert parsed_items[0]['location'] == {
        'neighborhood': '',
        'name': '',
        'address': (
            'Neal H. Holmes Board Room, '
            '345 Sixth Avenue, Fifth Floor, '
            'Pittsburgh, PA 15222-2527'
        )
    }


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'note': '',
        'url': (
            'https://www.portauthority.org/paac/'
            'CompanyInfoProjects/BoardofDirectors/'
            'MeetingAgendasResolutions.aspx'
        )
    }]


def test_documents():
    assert (
        parsed_items[0]['documents'][0] == {
            'note': 'Minutes',
            'url': (
                'http://www.portauthority.org/paac/'
                'Portals/0/Board/2018/AnnualMeetingMinutes.pdf'
            )
        }
    )


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] == ''


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] is 'Board' or 'Committee'


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'
