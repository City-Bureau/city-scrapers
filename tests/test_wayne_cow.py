import pytest

from tests.utils import file_response
from city_scrapers.spiders.wayne_cow import Wayne_cowSpider

# Adapted from test_chi_parks.py
from freezegun import freeze_time

freezer = freeze_time('2018-04-26 12:00:01')
freezer.start()
test_response = file_response(
    'files/wayne_cow.html', url='https://www.waynecounty.com/elected/commission/committee-of-the-whole.aspx')
spider = Wayne_cowSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]
freezer.stop()


def test_name():
    assert parsed_items[0]['name'] == 'Committee of the Whole'


@pytest.mark.parametrize('item', parsed_items)
def test_description(item):
    EXPECTED_DESCRIPTION = ("This committee is a forum for extensive discussion on issues "
                            "by the 15 members of the Wayne County Commission. Meetings "
                            "are scheduled at the call of the chair of the Commission. "
                            "Final approval of items happens at full Commission meetings, "
                            "not Committee of the Whole. All Committee of the Whole "
                            "meetings are held in the 7th floor meeting room, Guardian "
                            "Building, 500 Griswold, Detroit, unless otherwise indicated.")
    assert item['description'] == EXPECTED_DESCRIPTION

# def test_start_time():
# assert parsed_items[0]['start_time'].isoformat() == 'EXPECTED START DATE AND TIME'


# def test_end_time():
# assert parsed_items[0]['end_time'].isoformat() == 'EXPECTED END DATE AND TIME'


# def test_id():
# assert parsed_items[0]['id'] == 'EXPECTED ID'


def test_location():
    assert parsed_items[0]['location'] == {
        'url': 'http://guardianbuilding.com/',
        'name': '7th floor meeting room, Guardian Building',
        'address': '500 Griswold St, Detroit, MI 48226',
        'coordinates': {
            'latitude': '',
            'longitude': '', },
    }


@pytest.mark.parametrize('item', parsed_items)
def test_sources(item):
    assert item['sources'] == [
        {'url': 'https://www.waynecounty.com/elected/commission/committee-of-the-whole.aspx', 'note': ''}]


@pytest.mark.parametrize('item', parsed_items)
def test_timezone(item):
    assert item['timezone'] == 'America/Detroit'


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == 'Committee'


@pytest.mark.parametrize('item', parsed_items)
def test__type(item):
    assert item['_type'] == 'event'
