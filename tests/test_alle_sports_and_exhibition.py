import datetime

import pytest
from freezegun import freeze_time
from tests.utils import file_response

from city_scrapers.spiders.alle_sports_and_exhibition import AlleSportsAndExhibitionSpider

test_response = file_response('files/alle_sports_and_exhibition_schedule_sea.html')
spider = AlleSportsAndExhibitionSpider()

freezer = freeze_time('2018-12-17')
freezer.start()

parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]

freezer.stop()

# import pdb;pdb.set_trace()


def test_name():
    assert parsed_items[0]['name'] == 'SEA Board Meetings'


def test_description():
    assert parsed_items[0]['event_description'] == ''


def test_start():
    assert parsed_items[0]['start'] == {
        'date': datetime.date(2018, 2, 8),
        'time': datetime.time(10, 30),
        'note': ''
    }


def test_end():
    assert parsed_items[0]['end'] == {
        'date': datetime.date(2018, 2, 8),
        'time': datetime.time(13, 30),
        'note': 'Estimated 3 hours after start time'
    }


def test_id():
    assert parsed_items[0]['id'] == 'alle_sports_and_exhibition/201802081030/x/sea_board_meetings'


def test_status():
    assert parsed_items[0]['status'] == 'passed'


def test_location():
    assert parsed_items[0]['location'] == {
        'address': (
            'David L. Lawrence Convention Center , '
            '3rd Floor, 1000 Fort Duquesne Blvd, '
            'Pittsburgh, PA 15222'
        ),
        'name': 'David L. Lawrence Convention Center',
        'neighborhood': ''
    }


@pytest.mark.parametrize('item', parsed_items)
def test_sources(item):
    assert item['sources'] == [{
        'url': 'http://www.pgh-sea.com/schedule_sea.aspx?yr=2018',
        'note': ''
    }]


def test_documents():
    assert parsed_items[0]['documents'] == [
        {
            'note': 'Agenda',
            'url': 'http://www.pgh-sea.com/files/SEA_Agenda_2-8-2018.pdf'
        },
        {
            'note': 'Minutes',
            'url': 'http://www.pgh-sea.com/files/SEA_Board_Approved_Minutes_2-8-2018.PDF'
        }
    ]


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] is 'Board'


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert parsed_items[0]['_type'] == 'event'
