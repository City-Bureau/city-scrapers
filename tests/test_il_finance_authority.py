from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.constants import COMMITTEE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.il_finance_authority import IlFinanceAuthoritySpider

test_response = file_response(
    join(dirname(__file__), "files", "il_finance_authority.html"),
    url="https://www.il-fa.com/public-access/board-documents/",
)

test_pdf_response = file_response(
    join(dirname(__file__), "files", "il_finance_authority.pdf"),
    url=("https://www.il-fa.com/"),
    mode="rb",
)

spider = IlFinanceAuthoritySpider()

freezer = freeze_time("2020-09-30")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

pdf_text = spider._parse_agenda_pdf(test_pdf_response)

freezer.stop()


def test_time():
    time = spider._parse_start(pdf_text)
    assert time == "9:00 AM"


def test_name():
    location = spider._parse_location(pdf_text)
    assert "Authority’s Chicago Office" in location["name"]


def test_location():
    location = spider._parse_location(pdf_text)
    assert (
        "in the Authority’s Chicago Office, 160 North LaSalle Street, Suite S-1000, Chicago, Illinois 60601"
        in location["address"]
    )


def test_title():
    assert parsed_items[0].meta["title"] == "Conduit Financing Comm"


def test_classification():
    assert spider._parse_classification(parsed_items[0].meta["title"]) == COMMITTEE


def test_start():
    time = spider._parse_start(pdf_text)
    date = parsed_items[0].meta["date"]
    assert spider._meeting_datetime(date, time) == datetime(2020, 12, 8, 9, 0)


def test_source():
    assert (
        spider._parse_source(parsed_items[0])
        == "https://www.il-fa.com/sites/default/files/board-documents/12-08-20-conduit-notice.pdf"
    )
