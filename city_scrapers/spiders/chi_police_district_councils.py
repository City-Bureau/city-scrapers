import urllib.parse
from datetime import datetime, timedelta
from io import BytesIO

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil import parser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdftypes import resolve1
from pdfminer.psparser import PSKeyword, PSLiteral
from pdfminer.utils import decode_text


def decode_value(value):
    if isinstance(value, (PSLiteral, PSKeyword)):
        value = value.name
    if isinstance(value, bytes):
        value = decode_text(value)
    return value


def generate_start_urls(url):
    return [f"{url}/DC001.html"]
    return [
        f"{url}/DC{district:03}.html"
        for district in range(1, 26)
        if district not in (13, 21, 23)
    ]


class ChiPoliceDistrictCouncilsSpider(CityScrapersSpider):
    name = "chi_police_district_councils"
    agency = "Chicago Police District Councils"
    timezone = "America/Chicago"
    start_urls = generate_start_urls(
        "https://www.chicago.gov/city/en/depts/ccpsa/supp_info/district-council-pages"
    )

    def parse(self, response):
        for item in response.css(".llcontent"):
            url = item.css("p > a::attr('href')").get().strip()
            if "notices-and-agendas" in url:
                url_text = item.css("p > a::text").get().strip()
                yield response.follow(
                    url,
                    callback=self._parse_meeting,
                    meta={"url_text": url_text, "source": response.url},
                )

    def _parse_meeting(self, response):
        pdf = self._parse_pdf(response)

        try:
            start = self._parse_start_from_pdf(pdf)
        except (KeyError, parser._parser.ParserError):
            start = self._parse_start_from_url_text(response.meta["url_text"])

        meeting = Meeting(
            title=self._parse_title(response.url, pdf),
            description="",
            classification=self._parse_classification(pdf),
            start=start,
            end=self._parse_end(start),
            all_day=False,
            time_notes="",
            location={},
            links=self._parse_links(response),
            source=response.meta["source"],
        )
        if not pdf == {}:
            meeting["description"] = self._parse_description(pdf)
            meeting["location"] = self._parse_location(pdf)

        meeting["status"] = self._get_status(meeting)
        meeting["id"] = self._get_id(meeting)

        yield meeting

    def _parse_pdf(self, response):
        """Parse dates and details from schedule PDF"""
        data = {}
        fp = BytesIO(response.body)
        parser = PDFParser(fp)
        doc = PDFDocument(parser)
        res = resolve1(doc.catalog)
        if "AcroForm" in res:
            fields = resolve1(doc.catalog["AcroForm"])["Fields"]
            for f in fields:
                field = resolve1(f)
                name, values = field.get("T"), field.get("V")
                name = decode_text(name)
                values = resolve1(values)
                if isinstance(values, list):
                    values = [decode_value(v) for v in values]
                else:
                    values = decode_value(values)

                data.update({name: values})
        return data

    def _parse_meeting_type(self, item):
        if "Regular" in item and item["Regular"] == "On":
            return "Regular"
        elif "Special" in item and item["Special"] == "On":
            return "Special"
        elif "Closed" in item and item["Closed"] == "On":
            return "Closed"
        else:
            return ""

    def _parse_title(self, url, item=None):
        district = int(urllib.parse.urlparse(url).path.split("/")[7].split("-")[-1])

        meeting_type = self._parse_meeting_type(item)
        subtitle = f"{district:03} {meeting_type}" if meeting_type else f"{district:03}"

        return f"Chicago Police District Council {subtitle} Meeting"

    def _parse_description(self, item):
        try:
            pcl = item["Public Comment Limit"]
        except KeyError:
            pcl = item["PCL"]

        try:
            splmt = item["Limit per Commenter"]
        except KeyError:
            splmt = item["SpLmt"]
        instructions = (
            "Items on this agenda are subject to change. If you have any "
            "questions regarding this agenda, "
            "please contact 312-742-8888.\n\n"
            "INSTRUCTIONS FOR PUBLIC COMMENT\n\n"
            "The District Council will provide an opportunity for public "
            "comment. The public comment session will be "
            f"{pcl} minutes long. "
            "Each commenter will have up to "
            f"{splmt} minutes "
            "to speak. Anyone interested in giving public comment should "
            "write their name on a card provided at the meeting and give "
            "it to the members of the District Council or staff in the "
            "meeting room any time within 30 minutes of the start of the "
            "meeting. If the number of interested speakers exceeds the "
            "time dedicated to public comment, speakers will be selected "
            "by a random drawing.\n\nAnyone may submit written public "
            "comment by delivering it at the public meeting or by "
            "emailing it to Javon.Lewis-Brown@cityofchicago.org."
        )

        return (
            "Discussions:\n"
            f"{item['Discussions']}\n\n"
            "Votes:\n"
            f"{item['Votes']}\n\n"
            f"{instructions}"
        )

    def _parse_classification(self, item):
        return COMMISSION

    def _parse_start_from_url_text(self, date_str):
        return datetime.strptime(date_str, "%B %d, %Y")

    def _parse_start_from_pdf(self, item):
        start = item["DateTime"].replace("@", "")

        fmt1 = "%B %d, %Y, %I%M%p"
        fmt2 = "%B %d, %I%M%p"
        for fmt in (fmt1, fmt2):
            try:
                return datetime.strptime(start, fmt).replace(year=datetime.today().year)
            except ValueError:
                continue
        return parser.parse(start)

    def _parse_end(self, start):
        return start + timedelta(hours=2)

    def _parse_location(self, item):
        for key in ("LocationAddress", "Address"):
            try:
                return {
                    "address": "",
                    "name": item[key],
                }
            except KeyError:
                continue
        return {}

    def _parse_links(self, response):
        return [{"href": response.url, "title": "agenda"}]
