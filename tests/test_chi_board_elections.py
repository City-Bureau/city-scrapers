from datetime import date, time

import pytest
from freezegun import freeze_time
from tests.utils import file_response

from city_scrapers.constants import COMMISSION
from city_scrapers.spiders.chi_board_elections import ChiBoardElectionsSpider

freezer = freeze_time('2018-11-30 12:00:01')
freezer.start()
test_response = file_response(
    'files/chi_board_elections.html',
    url='https://app.chicagoelections.com/pages/en/board-meetings.aspx'
)
spider = ChiBoardElectionsSpider()
parsed_items = [item for item in spider._next_meeting(test_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[0]['name'] == 'Electoral Board'


def test_description():
    assert parsed_items[0]['event_description'] == ''


def test_start():
    assert parsed_items[0]['start'] == {'date': date(2018, 11, 27), 'time': time(9, 30), 'note': ''}


def test_end():
    assert parsed_items[0]['end'] == {'date': date(2018, 11, 27), 'time': None, 'note': ''}


def test_id():
    assert parsed_items[0]['id'] == \
           'chi_board_elections/201811270930/x/electoral_board'


def test_status():
    assert parsed_items[0]['status'] == 'passed'


def test_location():
    assert parsed_items[0]['location'] == {
        'address': '8th Floor Office, 69 W. Washington St.',
        'name': 'Cook County Administration Building',
        'neighborhood': '',
    }


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url': 'https://app.chicagoelections.com/pages/en/board-meetings.aspx',
        'note': ''
    }]


def test_documents():
    assert parsed_items[0]['documents'] == [{
        'note': 'Regular Board Meeting Agenda',
        'url':
            'https://app.chicagoelections.com/documents/'
            'general/Standard-Board-Meeting-Agenda.pdf'
    }]


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] is COMMISSION


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert parsed_items[0]['_type'] == 'event'


# Previous meetings on different page
prev_url = "https://app.chicagoelections.com/pages/en/meeting-minutes-and-videos.aspx"
test_response_prev = file_response('files/chi_board_elections_prev.html', url=prev_url)
parsed_items_prev = \
    [item for item in spider._prev_meetings(test_response_prev) if isinstance(item, dict)]
freezer.stop()


def test_name_prev():
    assert parsed_items_prev[0]['name'] == 'Electoral Board'


def test_description_prev():
    assert parsed_items_prev[0]['event_description'] == ''


def test_start_prev():
    assert parsed_items_prev[0]['start'] == \
           {'date': date(2018, 11, 27), 'time': time(9, 30), 'note': ''}


def test_end_prev():
    assert parsed_items_prev[0]['end'] == {'date': date(2018, 11, 27), 'time': None, 'note': ''}


def test_id_prev():
    assert parsed_items_prev[0]['id'] == \
           'chi_board_elections/201811270930/x/electoral_board'


def test_status_prev():
    assert parsed_items_prev[0]['status'] == 'passed'


def test_location_prev():
    assert parsed_items_prev[0]['location'] == {
        'address': '8th Floor Office, 69 W. Washington St.',
        'name': 'Cook County Administration Building',
        'neighborhood': '',
    }


def test_sources_prev():
    assert parsed_items_prev[0]['sources'] == [{
        'url': 'https://app.chicagoelections.com/pages/en/meeting-minutes-and-videos.aspx',
        'note': ''
    }]


def test_documents_prev():
    assert parsed_items_prev[4]['documents'] == \
           [{'url':
            'https://app.chicagoelections.com/documents/general/BoardMeetingMinutes-2018-10-30.pdf',
             'note': 'Regular Board Meeting Agenda'},
            {'note': 'Regular Board Meeting Video', 'url': 'https://youtu.be/AKFNigWEkc0'}
            ]


@pytest.mark.parametrize('item', parsed_items_prev)
def test_all_day_prev(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items_prev)
def test_classification_prev(item):
    assert item['classification'] is COMMISSION


@pytest.mark.parametrize('item', parsed_items_prev)
def test__type_prev(item):
    assert parsed_items_prev[0]['_type'] == 'event'


# def test_start_full():
#     listy = []
#     for x in parsed_items_prev:
#         listy.append(x['start'])
#         # listy.append(x['documents'])
#     assert listy == ["Just for demonstration purposes"]
