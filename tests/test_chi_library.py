import pytest
from tests.utils import file_response
from documenters_aggregator.spiders.chi_library import Chi_librarySpider

# def test_tests():
#     print('Please write some tests for this spider or at least disable this one.')
#     assert False

test_response = file_response('files/chi_library.html', url='https://www.chipublib.org/board-of-directors/board-meeting-schedule/')
spider = Chi_librarySpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[0]['name'] == 'Chicago Public Library Board Meeting'


def test_description():
    assert parsed_items[0]['description'] == 'There are no meetings in February, July and August. Entry into these meetings is permitted at 8:45 a.m.'


def test_start_time():
    assert parsed_items[0]['start_time'].isoformat() == '2017-01-17T09:00:00-06:00'


def test_end_time():
    assert parsed_items[0]['end_time'] is None


def test_id():
    assert parsed_items[0]['id'] == 'chi_library/201701170900/x/chicago_public_library_board_meeting'


def test_all_day():
    assert parsed_items[0]['all_day'] is False


# def test_classification(item):
    # assert parsed_items[0]['classification'] == None


# def test_status(item):
    # assert parsed_items[0]['status'] == 'tentative'


# def test_location(item):
    # assert item['location'] == {
    #     'url': 'EXPECTED URL',
    #     'name': 'EXPECTED NAME',
    #     'coordinates': {
    #         'latitude': 'EXPECTED LATITUDE',
    #         'longitude': 'EXPECTED LONGITUDE',
    #     },
    # }


# def test__type(item):
    # assert parsed_items[0]['_type'] == 'event'

@pytest.mark.parametrize('item', parsed_items)
def test_timezone(item):
    assert item['timezone'] == 'America/Chicago'


@pytest.mark.parametrize('item', parsed_items)
def test_sources(item):
    assert item['sources'] == [{'url': 'https://www.chipublib.org/board-of-directors/board-meeting-schedule/', 'note': ''}]
