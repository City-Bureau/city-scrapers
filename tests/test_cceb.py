import pytest
from tests.utils import file_response
from documenters_aggregator.spiders.cceb import CcebSpider

test_response = file_response('files/cceb_default.html', url='http://cookcountyclerk.com/elections/electoralboard/Pages/default.aspx')
spider = CcebSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_name():
    expected_name = ('Cook County Electoral Board Case; '
                     'Contest: Referendum; Objector: Esther Carrera; '
                     'Candidate: William Christian (Non)')
    assert parsed_items[0]['name'] == expected_name


def test_description():
    expected_description = ('http://cookcountyclerk.com/'
                            'elections/electoralboard/CaseDocuments//2017COEBREF01.pdf')
    assert parsed_items[0]['description'] == expected_description


def test_start_time():
    assert parsed_items[0]['start_time'] == '2017-08-28T14:00:00-05:00'


def test_end_time():
    assert parsed_items[0]['end_time'] is None


def test_id():
    assert parsed_items[0]['id'] == 'row1'


def test_all_day():
    assert parsed_items[0]['all_day'] is False


def test_classification():
    assert parsed_items[0]['classification'] == 'Not classified'


def test_status():
    assert parsed_items[0]['status'] == 'confirmed'


def test_location():
    assert parsed_items[0]['location'] == {
        'url': None,
        'name': '69 W. Washington, Pedway Room',
        'coordinates': {
            'latitude': None,
            'longitude': None,
        },
    }


def test__type():
    assert parsed_items[0]['_type'] == 'event'


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['sources'] == [{'url': 'http://cookcountyclerk.com/elections/electoralboard/Pages/default.aspx', 'note': ''}]