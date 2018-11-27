import pytest

from tests.utils import file_response
from city_scrapers.spiders.chi_board_elections import ChiBoardElectionsSpider


test_response = file_response('files/chi_board_elections.html')
spider = ChiBoardElectionsSpider()
parsed_items = [item for item in spider._next_meeting(test_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[0]['name'] == 'Chicago Board of Election Commissioners'


def test_description():
    assert parsed_items[0]['event_description'] == 'Meeting'


def test_start():
    assert parsed_items[0]['start'] == {'date': 'Nov. 27, 2018', 'time': '9:30 a.m', 'note': ''}


def test_end():
    assert parsed_items[0]['end'] == {}


# def test_id():
#     assert parsed_items[0]['id'] == 'EXPECTED ID'


# def test_status():
    # assert parsed_items[0]['status'] == 'EXPECTED STATUS'


# def test_location():
    # assert parsed_items[0]['location'] == {
        # 'neighborhood': 'EXPECTED URL',
        # 'name': 'EXPECTED NAME',
        # 'address': 'EXPECTED ADDRESS'
    # }


# def test_sources():
    # assert parsed_items[0]['sources'] == [{
        # 'url': 'EXPECTED URL',
        # 'note': 'EXPECTED NOTE'
    # }]


# def test_documents():
    # assert parsed_items[0]['documents'] == [{
      # 'url': 'EXPECTED URL',
      # 'note': 'EXPECTED NOTE'
    # }]


# @pytest.mark.parametrize('item', parsed_items)
# def test_all_day(item):
    # assert item['all_day'] is False


# @pytest.mark.parametrize('item', parsed_items)
# def test_classification(item):
    # assert item['classification'] is None


# @pytest.mark.parametrize('item', parsed_items)
# def test__type(item):
    # assert parsed_items[0]['_type'] == 'event'

# Previous meetings on different page

test_response_prev = file_response('files/chi_board_elections_prev.html')
spider = ChiBoardElectionsSpider()
parsed_items_prev = [item for item in spider._prev_meetings(test_response_prev) if isinstance(item, dict)]


def test_name_prev():
    assert parsed_items_prev[0]['name'] == 'Chicago Board of Election Commissioners'


def test_description_prev():
    assert parsed_items_prev[0]['event_description'] == 'Meeting'


# def test_start_prev():
#     assert parsed_items_prev[0]['start'] == {'date': 'Nov. 27, 2018', 'time': '9:30 a.m', 'note': ''}


def test_end_prev():
    assert parsed_items_prev[0]['end'] == {}


# def test_id_prev():
#     assert parsed_items_prev[0]['id'] == 'EXPECTED ID'


# def test_status_prev():
    # assert parsed_items_prev[0]['status'] == 'EXPECTED STATUS'


# def test_location_prev():
    # assert parsed_items_prev[0]['location'] == {
        # 'neighborhood': 'EXPECTED URL',
        # 'name': 'EXPECTED NAME',
        # 'address': 'EXPECTED ADDRESS'
    # }


# def test_sources_prev():
    # assert parsed_items_prev[0]['sources'] == [{
        # 'url': 'EXPECTED URL',
        # 'note': 'EXPECTED NOTE'
    # }]


# def test_documents_prev():
    # assert parsed_items_prev[0]['documents'] == [{
      # 'url': 'EXPECTED URL',
      # 'note': 'EXPECTED NOTE'
    # }]


# @pytest.mark.parametrize('item', parsed_items_prev)
# def test_all_day_prev(item):
    # assert item['all_day'] is False


# @pytest.mark.parametrize('item', parsed_items_prev)
# def test_classification_prev(item):
    # assert item['classification'] is None


# @pytest.mark.parametrize('item', parsed_items_prev)
# def test__type_prev(item):
    # assert parsed_items_prev[0]['_type'] == 'event'

