import pytest
from datetime import date, time

from freezegun import freeze_time
from tests.utils import file_response

from city_scrapers.spiders.chi_ssa_38 import ChiSsa38Spider

test_response = file_response('files/chi_ssa_38.html')
spider = ChiSsa38Spider()

freezer = freeze_time('2018-12-22')
freezer.start()

parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]

freezer.stop()


# def test_name():
    # assert parsed_items[0]['name'] == 'EXPECTED NAME'


def test_description():
    assert parsed_items[0]['event_description'] == ''


def test_start():
    # assert parsed_items[0]['start'] == {'date': date(2018, 9, 13), 'time': '', 'note': ''} # Fix year here
    assert parsed_items[1]['start'] == {'date': date(2018, 9, 13), 'time': '', 'note': ''}

# Confirmed that we get all the dates back
# def test_all_start():
#     listy = []
#     for x in parsed_items:
#         listy.append(x['start'])
#     assert listy == ["Just for test"]



def test_end():
    assert parsed_items[1]['end'] == {'date': date(2018, 9, 13), 'time': None, 'note': ''}


# def test_id():
    # assert parsed_items[0]['id'] == 'EXPECTED ID'


# def test_status():
    # assert parsed_items[0]['status'] == 'EXPECTED STATUS'


def test_location():
    assert parsed_items[0]['location'] == {
            'address': '4054 N. Lincoln Avenue',
            'name': 'Northcenter Chamber of Commerce',
            'neighborhood': '',
        }


def test_sources():
    assert parsed_items[0]['sources'] == [{
                    'url': 'http://www.northcenterchamber.com/pages/MeetingsTransparency1',
                    'note': ''
                }]

def test_documents():
    assert parsed_items[1]['documents'] == [
        {'url': 'https://chambermaster.blob.core.windows.net'
                '/userfiles/UserFiles/chambers/1775/CMS/SSA38-Minutes-9132018.docx',
         'note': 'SSA Commission Meeting Minutes'}]


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


# @pytest.mark.parametrize('item', parsed_items)
# def test_classification(item):
    # assert item['classification'] is None


# @pytest.mark.parametrize('item', parsed_items)
# def test__type(item):
    # assert parsed_items[0]['_type'] == 'event'
