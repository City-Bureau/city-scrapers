from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, COMMITTEE, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.cook_hospitals import CookHospitalsSpider

test_response = file_response(
    join(dirname(__file__), "files", "cook_hospitals.html"),
    url=(
        'https://cookcountyhealth.org/about/board-of-directors/board-committee-meetings-agendas-minutes/'  # noqa
    )
)
spider = CookHospitalsSpider()

freezer = freeze_time("2019-05-15")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 51


def test_title():
    assert parsed_items[0]['title'] == 'Board of Directors'


def test_description():
    assert parsed_items[0]['description'] == ''


def test_start():
    assert parsed_items[0]['start'] == datetime(2019, 1, 25, 9)


def test_end():
    assert parsed_items[0]['end'] is None


def test_time_notes():
    assert parsed_items[0]['time_notes'] == 'Confirm time in agenda'


def test_links():
    assert parsed_items[0]['links'] == [
        {
            'href': 'https://cookcountyhealth.org/wp-content/uploads/01-25-19-Board-Agenda.pdf',
            'title': 'Agenda'
        },
        {
            'href': 'https://cookcountyhealth.org/wp-content/uploads/Metrics-Finance-01-25-19.pdf',
            'title': 'Metrics Finance Committee'
        },
        {
            'href': 'https://cookcountyhealth.org/wp-content/uploads/Metrics-HR-01-25-19.pdf',
            'title': 'Metrics Human Resources Committee'
        },
        {
            'href':
                'https://cookcountyhealth.org/wp-content/uploads/Metrics-Managed-Care-01-25-19.pdf',
            'title': 'Metrics Managed Care Committee'
        },
        {
            'href': 'https://cookcountyhealth.org/wp-content/uploads/Metrics-QPS-01-25-19.pdf',
            'title': 'Metrics QPS Committee'
        },
        {
            'href':
                'https://cookcountyhealth.org/wp-content/uploads/Item-VIII-Report-from-the-CEO-01-25-19.pdf',  # noqa
            'title': 'Item VIII Report from CEO'
        },
        {
            'href':
                'https://cookcountyhealth.org/wp-content/uploads/Item-IXA-SP-Discussion-Federal-State-Landscape-01-25-19.pdf',  # noqa
            'title': 'Item IV(A) SP discussion State and Federal Issues'
        },
        {
            'href':
                'https://cookcountyhealth.org/wp-content/uploads/01-25-19-Board-scan-Minutes.pdf',
            'title': '01-25-19 Board of Directors Meeting Minutes'
        }
    ]


def test_id():
    assert parsed_items[0]['id'] == 'cook_hospitals/201901250900/x/board_of_directors'


def test_status():
    assert parsed_items[0]['status'] == PASSED


def test_location():
    assert parsed_items[0]['location'] == spider.location


def test_classification():
    assert parsed_items[0]['classification'] == BOARD
    assert parsed_items[-1]['classification'] == COMMITTEE


@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False


@pytest.mark.parametrize('item', parsed_items)
def test_source(item):
    assert item[
        'source'
    ] == 'https://cookcountyhealth.org/about/board-of-directors/board-committee-meetings-agendas-minutes/'  # noqa
