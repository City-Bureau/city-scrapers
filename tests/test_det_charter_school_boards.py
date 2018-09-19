from datetime import date, time

import pytest
from freezegun import freeze_time

from tests.utils import file_response
from city_scrapers.spiders.det_charter_school_boards import DetCharterSchoolBoardsSpider

test_response = file_response('files/det_charter_school_boards.html',
                              'http://detroitk12.org/admin/charter_schools/boards/')

freezer = freeze_time('2018-08-15 12:00:01')
freezer.start()
spider = DetCharterSchoolBoardsSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]
freezer.stop()


def test_event_count():
    non_calendar_events = 8
    calendar_events = 81
    assert len(parsed_items) == non_calendar_events + calendar_events


def test_starts_with_day_of_week():
    # page is just on big block of text with meeting details nested in
    # p tags. Can id meetings by finding p tag text that starts with DoW
    assert spider._startswith_day_of_week() == \
           ('//p[starts-with(text(), "Monday") '
            'or starts-with(text(), "Tuesday") '
            'or starts-with(text(), "Wednesday") '
            'or starts-with(text(), "Thursday") '
            'or starts-with(text(), "Friday") '
            'or starts-with(text(), "Saturday") '
            'or starts-with(text(), "Sunday")]')


def test_name():
    assert parsed_items[2]['name'] == 'Charter Schools Boards: Annual Boards of Directors Conference'


def test_description():
    assert parsed_items[2]['event_description'] == \
           'All board members are invited to participate in a day of learning and exchange of ideas. Multiple ' \
           'breakout sessions will provide training to both new and experienced board members. Continental breakfast ' \
           'and lunch will be provided.'


def test_start():
    assert parsed_items[2]['start'] == {
        'date': date(2018, 4, 21),
        'time': time(8, 30),
        'note': '',
    }


def test_end():
    assert parsed_items[2]['end'] == {
        'date': date(2018, 4, 21),
        'time': time(15, 00),
        'note': '',
    }


def test_id():
    assert parsed_items[2]['id'] == 'det_charter_school_boards/201804210830/x/charter_schools_boards_annual_boards_of_directors_conference'


def test_status():
    assert parsed_items[2]['status'] == 'passed'


def test_location():
    assert parsed_items[2]['location'] == {
        'neighborhood': '',
        'name': 'Greater Grace Temple',
        'address': '23500 West Seven Mile Road Detroit, MI'
    }


def test_sources():
    assert parsed_items[0]['sources'] == [{
        'url': 'http://detroitk12.org/admin/charter_schools/boards/',
        'note': ''
    }]


def test_documents():
    assert parsed_items[0]['documents'] == []


def test_name_calendar():
    assert parsed_items[8]['name'] == 'Charter Schools Boards: MacDowell Preparatory Academy Board Meeting'


def test_description_calendar():
    assert parsed_items[8]['event_description'] == ''


def test_start_calendar():
    assert parsed_items[8]['start'] == {
        'date': date(2018, 8, 15),
        'time': time(18, 00),
        'note': '',
    }


def test_end_calendar():
    assert parsed_items[8]['end'] == {
        'date': date(2018, 8, 15),
        'time': time(20, 00),
        'note': '',
    }


def test_id_calendar():
    assert parsed_items[8]['id'] == \
           'det_charter_school_boards/201808151800/x/charter_schools_boards_mac_dowell_preparatory_academy_board_meeting'


def test_status_calendar():
    assert parsed_items[8]['status'] == 'confirmed'


def test_location_calendar():
    assert parsed_items[8]['location'] == {
        'neighborhood': '',
        'name': '',
        'address': '4201 Outer Dr W, Detroit, MI 48221, USA'
    }


def test_sources_calendar():
    assert parsed_items[8]['sources'] == [{
        'url': 'http://detroitk12.org/admin/charter_schools/boards/',
        'note': ''
    }]


def test_documents_calendar():
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
