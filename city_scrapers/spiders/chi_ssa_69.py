import re
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
        ''' figure out if this line is the title line '''
        if (lpos == 1) and (('font-weight:600' in line.extract()) or
                            ('font-weight:bold;' in line.extract())):
            # check that the title text is not just whitespace
            if (self.lxml_to_text(line.extract()).isspace()):
                return False
            else:
                return True
        else:
            return False

    def is_date_line(self, line):
        ''' figure our if this line is the date line '''
        if ('Date' in line.extract()):
            return True
        else:
            return False

    def is_location_line(self, line, lpos=3):
        ''' figure our if this line is the location line '''
        if ((lpos == 3) and ('Location:' in line.extract())):
            return True
        else:
            print('n' + line.extract())
            return False

    def is_location_determined(self, line):
        ''' return whether the location line has been set to a location yet '''
        print("running is_location_determined")
        print(line)

        if (line == 'no specific location found on line position 3'):
            return False
        elif (line == ''):
            return False
        # below would work if is_location_line didn't perform extract()
        # elif ( self.is_location_line(line) ):
        elif ('Location:' in line):
            return True
        else:
            return False

    def is_wixguard(self, line):
        ''' figure out if this line is the wixguard line that separates listings '''
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
            if self.is_title_line(cur) is False or self.is_title_line(next) is False or \
                    self.lxml_to_text(cur.extract()) != self.lxml_to_text(next.extract()):
                out_spans.append(spans[i])
        out_spans.append(spans[-1])
        return out_spans

    def combine_consecutive_duplicate_text_lines(self, spans):
        cur = ""
        next = ""
        out_spans = []
        for i in range(len(spans) - 1):
            cur = spans[i]
            next = spans[i + 1]
            if self.lxml_to_text(cur.extract()) != self.lxml_to_text(next.extract()):
                out_spans.append(spans[i])
        out_spans.append(spans[-1])
        return out_spans

    def trim_extra_at_beginning(self, spans):
        beginning_triggered = False
        out_spans = []
        for i in range(len(spans) - 1):
            if (self.is_wixguard(spans[i])):
                beginning_triggered = True
            if beginning_triggered is True:
                out_spans.append(spans[i])
        return out_spans

    def parse_spans(self, these_spans, response):
        title_line = ""
        date_line = ""
        location_line = ""
        lpos = 999  # line position within meeting listing - 999 means unset
        meeting_info = []
        meetings_info_list = []
        for i in range(len(these_spans)):
            lpos += 1

            print(str(i) + "-" + str(lpos) + "--->>" + these_spans[i].extract())
            if (self.is_title_line(these_spans[i], lpos)):
                # if (self.is_title_line(spans[i])):
                title_line = these_spans[i].extract()
                print('SETTING title = ' + str(self.lxml_to_text(these_spans[i].extract())))
                try:
                    title_line = self.lxml_to_text(title_line)
                except Exception:
                    title_line = "unable to get text from title line"
            if (lpos == 2):
                # check the next line to see if it is the line with event date(s)
                if (self.is_date_line(these_spans[i])):
                    date_line = self.lxml_to_text(these_spans[i].extract())
                else:
                    # have to deal with this case in a special way
                    date_line = 'no specific date'
                    # special_info_line = spans[_]
                print("------>" + date_line + "<---------")
            if (lpos == 3):
                if (self.is_location_line(these_spans[i])):
                    location_line = self.lxml_to_text(these_spans[i].extract())
                else:
                    # have to deal with this case in a special way
                    location_line = 'no specific location found on line position 3'
                    # special_info_line = spans[_]
                # print("------>" + location_line + "<---------")

                lpos += 1

            if ((lpos > 3) and self.is_location_determined(location_line) is False):
                if (self.is_location_line(these_spans[i])):
                    location_line = self.lxml_to_text(these_spans[i].extract())

            if (these_spans[i].css(".wixGuard")):
                lpos = 0

                if (title_line.isspace() is not True and title_line != ''):
                    title = title_line
                    description = ''  # intentionally empty
                    classification = NOT_CLASSIFIED
                    start = datetime.now()  # not correct yet
                    end = datetime.now()  # not correct yet
                    all_day = False
                    time_notes = date_line  # not correct yet
                    location = location_line
                    links = None
                    source = self._parse_source(response)

                    meeting_info = [
                        title, description, classification, start, end, all_day, time_notes,
                        location, links, source
                    ]
                    meetings_info_list.append(meeting_info)
                    print(str(i) + "-" + str(lpos) + "--->" + title_line)
            else:
                # if something weird slips through, we might have to
                # backup the line position (lpos)
                if (self.lxml_to_text(these_spans[i].extract()).isspace()):
                    lpos = lpos - 1
                # if (self.lxml_to_text(spans[i].extract()) == title_line):
                # lpos = 0
                # print("BACKING UP FOR 2ND TITLE")

                # if (i > 5900):
                # exit()

        return meetings_info_list

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """

        all_spans = response.css("span")

        spans_for_title = self.combine_consecutive_wixguard_spans(all_spans)
        spans_for_title = self.combine_consecutive_font_weight_600s(spans_for_title)
        spans_for_title = self.trim_extra_at_beginning(spans_for_title)
        # spans = self.combine_consecutive_duplicate_text_lines(spans)

        # I discovered that if I treat the spans differently,
        # I can make it work for date, but that would mess up
        # the way they work for titles
        spans_for_general_use = self.combine_consecutive_wixguard_spans(all_spans)
        spans_for_general_use = self.combine_consecutive_font_weight_600s(spans_for_general_use)
        spans_for_general_use = self.trim_extra_at_beginning(spans_for_general_use)
        spans_for_general_use = self.combine_consecutive_duplicate_text_lines(spans_for_general_use)

        meeting_info_for_titles = self.parse_spans(spans_for_title, response)
        meeting_info_for_dates = self.parse_spans(spans_for_general_use, response)
        assert len(meeting_info_for_dates) == len(meeting_info_for_titles)

        # munge info for titles and dates together
        for i in range(len((meeting_info_for_dates))):

            meeting = Meeting(
                title=meeting_info_for_titles[i][0].replace(u'\xa0', u' '),
                description='',  # intentionally empty
                classification=NOT_CLASSIFIED,
                start=datetime.now(),
                end=datetime.now(),
                all_day=False,
                # time_notes="time notes test",
                time_notes=meeting_info_for_dates[i][6],
                location=self._parse_location(meeting_info_for_dates[i][7]),
                links=None,
                source=self._parse_source(response),
            )
            yield meeting

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
        address = ""
        name = ""
        item_str = str(item)
        address_regex = r"((?i)\d+ ((?! \d+ ).)*(il|illinois)(, \d{5}| \d{5}|\b))"
        address_matches = re.findall(address_regex, item_str)
        assert len(address_matches) < 2
        if len(address_matches) > 0:
            address = address_matches[0][0]
            # take care of unicode non-breaking space \xa0
            address = address.replace(u'\xa0', u' ')
        else:
            name = item_str
        return {
            "address": address,
            "name": name,
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": "", "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url