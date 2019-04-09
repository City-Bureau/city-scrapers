import scrapy
from city_scrapers_core.constants import ADVISORY_COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
import datetime as dt
import re

class IlMedicaidSpider(CityScrapersSpider):
    name = "il_medicaid"
    agency = "Illinois Medical Adivsory Committee"
    timezone = "America/Chicago"
    allowed_domains = ["www.illinois.gov"]

    # Using the MAC main page makes it more convenient to grab the meeting
    # title
    start_urls = ["https://www.illinois.gov/hfs/About/BoardsandCommisions/MAC/Pages/"
                  "default.aspx"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        # The title of the main of the committee/subcommittee page is the name
        # of the said committee/subcommittee.
        title = self._parse_title(response.xpath("//title/text()").get())

        # The meeting times are listed in the "Schedules" page for each
        # committee/subcommittee.

        schedule_xpath = "//a[descendant::*[contains(text(),'chedule')]]/@href"
        schedule_page_url = response.xpath(schedule_xpath).get()
        if schedule_page_url is not None:
            schedule_page_url = response.urljoin(schedule_page_url)
            request = scrapy.Request(url = schedule_page_url,
                                     callback = self._get_meetings)
            request.meta['title'] = title
            yield request

        # Request subcommittee pages.

        subcom_xpath = "//a[contains(@title, 'ubcommitt')]/following-sibling::ul/li/a/@href"
        subcom_pages = response.xpath(subcom_xpath).getall()
        if subcom_pages is not None:
            for subcom in subcom_pages:
                subcom = response.urljoin(subcom)
                yield scrapy.Request(url=subcom, callback=self.parse)

        # TBD: Request minutes and notices

    # Just stripping the white spaces seems enough 
    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return item.strip()

    def _get_meetings(self, response):
        """
        Callback method for scraping the 'schedule' pages.
        """

        # The MAC website currently lists the time directly inside the div
        # container without any tags. The descendant-or-self is used in case
        # this is changed in the future. 

        time_xpath = "//h2[starts-with(text(),'Time')]/following::node()[normalize-space()][1]/descendant-or-self::text()"
        raw_time_interval = response.xpath(time_xpath).get()
        time_start, time_end = self._parse_time_interval(raw_time_interval)
        locations_xpath = "//h2[starts-with(text(),'Location')]/following-sibling::node()[normalize-space()]"
        raw_locations = response.xpath(locations_xpath).getall()
        chicago_location = self._parse_chicago_location(raw_locations)
        # locations_xpath = "//h2[starts-with(text(),'Location')]/following-sibling::node()/descendant-or-self::text()[normalize-space()]"

        date_xpath = "//h2[contains(text(),'Meeting Dates')]/following::ul/li/p/text()"
        for date_str in response.xpath(date_xpath).re(r'[\w]+[\s]+[\d]+,\s[\d]+'):
            date = self._parse_date(date_str)

            meeting = Meeting(
                title= response.meta['title'],
                description='', # TBD
                classification=ADVISORY_COMMITTEE, # TBD
                start=dt.datetime.combine(date,time_start),
                end=dt.datetime.combine(date,time_end),
                all_day=False,# TBD
                time_notes="",# TBD
                location={
                    'name': chicago_location['name'],
                    'address': chicago_location['address'],
                },
                links=[],# TBD
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_date(self, date):
        """
        Parses meeting date.
        """
        date = date.replace('\xa0',' ')

        try:
            return dt.datetime.strptime(date, "%B %d, %Y")
        except ValueError:
            return dt.datetime(1900,1,1)

    # replaces _parse_start and _parse_end
    def _parse_time_interval(self, raw_time_interval):
        dashes = r'[-{}]'.format(chr(8211)) # some pages use -, chr(8211)
        raw_times = [x.strip().upper() for x in re.split(dashes, raw_time_interval)]
        time_interval = []
        for time in raw_times:
            if time == "NOON":
                time_interval.append(dt.datetime.strptime('1200','%H%M').time())
            else:
                colon_index = time.find(":")
                time = "".join(time.strip().upper().split("."))
                if colon_index > -1:
                    if len(time[:colon_index]) == 1:
                        time = "0" + time
                    try:
                        time_interval.append(dt.datetime.strptime(time,'%I:%M %p').time())
                    except ValueError:
                        time_interval.append(dt.datetime.strptime(time + " pm",'%I:%M %p').time())
                else:
                    try:
                        time_interval.append(dt.datetime.strptime(time,'%I %p').time())
                    except ValueError:
                        time_interval.append(dt.datetime.strptime(time + " pm",'%I %p').time())
        if time_interval[0] > time_interval[1]:
            time_interval[0] += dt.timedelta(hours=-12)
        return time_interval


    # def _parse_description(self, item):
    #     """Parse or generate meeting description."""
    #     return ""

    # def _parse_classification(self, item):
    #     """Parse or generate classification from allowed options."""
    #     return NOT_CLASSIFIED

    # def _parse_time_notes(self, item):
    #     """Parse any additional notes on the timing of the meeting"""
    #     return ""

    # def _parse_all_day(self, item):
    #     """Parse or generate all-day status. Defaults to False."""
    #     return False

    def _parse_chicago_location(self, raw_locations):
        """Parse or generate the Chicago meeting location."""

        # The meeting is a video conference, so two locations are provided on the website.
        # For the time being, we are only going to show the Chicago location.

        Chicago = "Chicago"
        chicago_location = []

        # City names are inside h3 tag.
        # Each line of address is contained in one or more <p> tags.
        # If multiple lines of address are contained in a <p> tag, then <br> tags are used.
        for i, x in enumerate(raw_locations):
            if "h3" in x and Chicago in x:
                for y in raw_locations[i+1:]:
                    if "<p" in y:
                        chicago_location += re.findall(r">([\w\s\d\.\,]+)<",y)
                    else:
                        break
        for i, line in enumerate(chicago_location):
            chicago_location[i] = line.strip()

        # Check to see if there is a comma in 'city, state zipcode", then add one if there isn't.
        last_line = chicago_location[-1]
        if not "," in last_line:
            first_space_index = last_line.index(" ")
            chicago_location[-1] = last_line[:first_space_index] + "," + last_line[first_space_index:]

        # Split street address from name of the building 
        split_name_address = re.split('\s([\d]+[\w\s]+)',chicago_location[0])
        if len(split_name_address) > 1:
            name, first_line = split_name_address[:2]
            address = first_line + ", " + ", ".join(chicago_location[1:])
        else:
            name = split_name_address[0]
            address = ", ".join(chicago_location[1:])

        return {
            'address': address,
            'name': name,
        }

    # def _parse_links(self, item):
    #     """Parse or generate links."""
    #     return [{"href": "", "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
