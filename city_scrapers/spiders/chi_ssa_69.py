from datetime import datetime

import lxml.html as lh
from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from lxml.html.clean import clean_html


class ChiSsa69Spider(CityScrapersSpider):
    name = "chi_ssa_69"
    agency = "Chicago Special Service Area #69 95th & Ashland Avenue"
    timezone = "America/Chicago"
    allowed_domains = ["auburngresham.wixsite.com"]
    start_urls = ["https://auburngresham.wixsite.com/ssa69/calendar"]

    def lxml_to_text(self, html):
        doc = lh.fromstring(html)
        doc = clean_html(doc)
        return doc.text_content()

    def is_title_line(self, line, lpos=1):
        if ('font-weight:600' in line.extract()) and (lpos == 1):
            return True
        else:
            return False

    def is_date_line(self, line):
        if ('date' in line.extract()):
            return True
        else:
            return False

    def is_wixguard(self, line):
        if ('<span class="wixGuard">' in line.extract()):
            return True
        else:
            return False

    def combine_consecutive_wixguard_spans(self, spans):
        cur = ""
        next = ""
        out_spans = []
        for i in range(len(spans) - 1):
            cur = spans[i]
            next = spans[i + 1]
            if self.is_wixguard(cur) is False or self.is_wixguard(next) is False:
                out_spans.append(spans[i])
        out_spans.append(spans[-1])
        return out_spans

    def combine_consecutive_font_weight_600s(self, spans):
        cur = ""
        next = ""
        out_spans = []
        for i in range(len(spans) - 1):
            cur = spans[i]
            next = spans[i + 1]
            if self.is_title_line(cur) is False or self.is_title_line(next) is False:
                out_spans.append(spans[i])
        out_spans.append(spans[-1])
        return out_spans

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """

        all_spans = response.css("span")
        spans = self.combine_consecutive_wixguard_spans(all_spans)
        spans = self.combine_consecutive_font_weight_600s(all_spans)

        title_line = ""
        date_line = ""
        lpos = 999  # line position within meeting listing - 999 mesnd unset
        for i in range(len(spans)):
            lpos += 1
            print(str(i) + "-" + str(lpos) + "---" + spans[i].extract())
            # print(lpos)
            if (self.is_title_line(spans[i], lpos)):
                title_line = spans[i].extract()
                try:
                    title_line = self.lxml_to_text(title_line)
                except Exception:
                    title_line = "unable to get text from title line"
                # line_position_within_listing += 1
            if (lpos == 1):
                # check the next line to see if it is the line with event date(s)
                if (self.is_date_line(spans[i])):
                    date_line = spans[i]
                else:
                    # have to deal with this case in a special way
                    date_line = 'no specific date'
                    # special_info_line = spans[_]
                lpos += 1
            if (spans[i].css(".wixGuard")):
                lpos = 0

                # print(date_line)

                meeting = Meeting(
                    title=title_line,
                    # date_line is used below just to satisfy flake8 linter
                    description='this is a test description' + date_line,
                    classification=NOT_CLASSIFIED,
                    start=datetime.now(),
                    end=datetime.now(),
                    all_day=False,
                    time_notes="time notes test",
                    location="test location",
                    links=None,
                    source=self._parse_source(response),
                )
                yield meeting
                # print(str(i) + "-" + str(lpos) + "---" + title_line)
                # if (i > 131):
                #    # exit()

        # meetings = response.css("font-weight:600")
        # for item in meetings:
        #    meeting = Meeting(
        #        title=self._parse_title(item),
        #        description=self._parse_description(item),
        #        classification=self._parse_classification(item),
        #        start=self._parse_start(item),
        #        end=self._parse_end(item),
        #        all_day=self._parse_all_day(item),
        #        time_notes=self._parse_time_notes(item),
        #        location=self._parse_location(item),
        #        links=self._parse_links(item),
        #        source=self._parse_source(response),
        #    )

        # meeting["status"] = self._get_status(meeting)
        # meeting["id"] = self._get_id(meeting)

        #  yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return ""

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        return None

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item):
        """Parse or generate location."""
        return {
            "address": "",
            "name": "",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": "", "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
