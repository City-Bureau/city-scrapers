from datetime import datetime
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import COMMITTEE, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.cook_landbank import CookLandbankSpider

test_response = file_response(
    join(dirname(__file__), "files", "cook_landbank.html"),
    url="http://www.cookcountylandbank.org",
)
test_form_response = file_response(
    join(dirname(__file__), "files", "cook_landbank.json"),
    url="http://www.cookcountylandbank.org/wp-admin/admin-ajax.php",
)
test_docs_response = file_response(
    join(dirname(__file__), "files", "cook_landbank_docs.html"),
    url="http://www.cookcountylandbank.org/wp-admin/admin-ajax.php",
)
test_detail_response = file_response(
    join(dirname(__file__), "files", "cook_landbank_detail.html"),
    url="http://www.cookcountylandbank.org/events/cclba-land-transactions-committee-20190913/",  # noqa
)
spider = CookLandbankSpider()

freezer = freeze_time("2019-09-15")
freezer.start()

parsed_items = [item for item in spider._parse_home(test_response)]
parsed_form = [item for item in spider._parse_form_response(test_form_response)]
parsed_detail = [item for item in spider._parse_detail(test_detail_response)][0]
spider._parse_documents_page(test_docs_response)

freezer.stop()


def test_count():
    assert len(parsed_items) == 9
    assert len(parsed_form) == 1
    assert len(list(spider.documents_map.keys())) == 22


def test_title():
    assert parsed_items[0]["title"] == "CCLBA Data & Marketing Committee"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 9, 18, 10, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_all_day():
    assert parsed_items[0]["all_day"] is False


def test_classification():
    assert parsed_items[0]["classification"] == COMMITTEE


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        **spider.location,
        "name": "Cook County Admin Building, 22nd Floor, Conference Room 'B'",
    }


def test_sources():
    assert (
        parsed_items[0]["source"]
        == "http://www.cookcountylandbank.org/events/cclba-data-marketing-committee-20190918/"  # noqa
    )


def test_links():
    assert parsed_items[0]["links"] == []
    assert parsed_detail["links"] == [
        {
            "title": "Agenda",
            "href": "http://www.cookcountylandbank.org/wp-content/uploads/2019/09/CCLBA-Land-Transactions-9-13-2019-Agenda.pdf",  # noqa
        }
    ]
