import datetime
import re
import unicodedata

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from w3lib.html import remove_tags


class ChiSsa8Spider(CityScrapersSpider):
    name = "chi_ssa_8"
    agency = "Chicago Special Service Area #8 Lakeview East"
    timezone = "America/Chicago"
    start_urls = ["https://lakevieweast.com/ssa-8/"]
    monthDateRegex = (
        r"(Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|Jul(y)?"
        r"|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?|Dec(ember)?)\s+\d{1,2}"
    )

    def parse(self, response):
        for item in response.css(".post-content ul"):
            year = self._parse_year(item)
            if year is not None:
                linksByQuarter = self._parse_links_by_quarter(item, year)
                location = self._parse_location(item)
                for li in item.css("li"):
                    startDate = self._parse_start(li, year)
                    if startDate is not None:
                        titleDesc = self._parse_title_desc(li)
                        meeting = Meeting(
                            title=titleDesc,
                            description=titleDesc,
                            classification=self._parse_classification(li),
                            start=startDate,
                            end=self._parse_end(li),
                            all_day=self._parse_all_day(li),
                            time_notes=self._parse_time_notes(li),
                            location=location,
                            links=self._parse_links(titleDesc, linksByQuarter),
                            source=self._parse_source(response),
                        )
                        meeting["status"] = self._get_status(meeting)
                        meeting["id"] = self._get_id(meeting)

                        yield meeting

    def _parse_year(self, item):
        header = item.xpath("./preceding::h3[1]")
        if header[0].extract():
            headerString = header[0].extract()
            headerSearch = re.search(r"\d{4}", headerString)
            if headerSearch:
                return headerSearch.group()
            return None

    def _parse_title_desc(self, item):
        raw = remove_tags(item.extract())
        title = " ".join([s.replace(",", "") for s in raw.split(" ")][3:])
        title = re.sub(r"[\(\)–]", "", title)
        return unicodedata.normalize("NFKD", title.strip())

    def _parse_classification(self, item):
        return COMMISSION

    def _parse_start(self, item, year):
        raw = remove_tags(item.extract())
        monthDateString = re.search(self.monthDateRegex, raw)
        if monthDateString:
            monthDateString = monthDateString.group(0)
            return datetime.datetime.strptime(monthDateString + " " + year, "%B %d %Y")
        return None

    def _parse_end(self, item):
        return None

    def _parse_time_notes(self, item):
        return ""

    def _parse_all_day(self, item):
        return False

    def _parse_location(self, item):
        locationString = (
            item.xpath("//li[contains(text(), 'Location')]").extract_first().strip()
        )
        locationString = remove_tags(locationString)
        rmStrings = ["Location", ":"]
        for x in rmStrings:
            locationString = locationString.replace(x, "")
            location = locationString.split(",")

            name = location[0].strip()
            address = location[1].strip()

            if not re.search("chicago", address, re.IGNORECASE):
                address += ", Chicago, IL"

        return {
            "address": address,
            "name": name,
        }

    def _parse_links_by_quarter(self, item, year):
        meetingList = item.xpath(
            '//h3[contains(text(), "' + year + ' Minutes")]/following-sibling::ul[1]'
        )
        yearLinksList = meetingList.css("li a")
        linksByQuarter = {}
        if meetingList:
            for quaterLinks in yearLinksList:
                quarter = quaterLinks.css("a::text").extract()[0]
                quarter = re.match("(.*?)quarter", quarter, re.IGNORECASE)
                if not quarter:
                    continue
                quarter = quarter.group()

                link = quaterLinks.css("a::attr(href)").extract()[0]
                if not link:
                    continue

                if quarter not in linksByQuarter:
                    linksByQuarter[quarter] = []

                linksByQuarter[quarter].append(link)
            return linksByQuarter

    def _parse_links(self, quarter, linksByQuarter):
        if quarter not in linksByQuarter:
            return []
        links = []
        quarterLinks = linksByQuarter[quarter]
        for quarterLink in quarterLinks:
            quarterDict = {}
            quarterDict["title"] = quarter
            quarterDict["href"] = quarterLink

            links.append(quarterDict)
        return links

    def _parse_source(self, response):
        return response.url
