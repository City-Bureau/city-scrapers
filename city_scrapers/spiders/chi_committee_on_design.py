from pickle import FALSE, TRUE
from datetime import datetime
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiCommitteeOnDesignSpider(CityScrapersSpider):
    name = "chi_committee_on_design"
    agency = "Comittee On Design"
    timezone = "America/Chicago"
    start_urls = [
        "https://www.chicago.gov/city/en/depts/dcd/supp_info/committee-on-design.html"
    ]

    def parse(self, response):

        # Parse strong text on page to get a list of all years
        # each has a table of meetings under it
        years = response.css("strong::text").getall()
        years = years[3:]
        years = [i[0:4] for i in years]

        tablecount = 0
        for table in response.css("table"):  # loop through every meeting table
            # holds all meetings for a given year (loop)
            total = []
            # list of raw HTML for a given meeting
            # to later get meeting agenda if link exists
            total_clean_dates = []
            for item in table.css("td"):
                dates = item.css("p::text").getall()
                # taking raw HTML and splitting by date
                # to later pull meeting agenda link
                clean_dates = item.css("p").get().split("<br>")
                total_clean_dates += clean_dates
                # loop through text from the table, removing non-date strings
                for i in range(len(dates)):
                    curr = dates[i]
                    d = curr.strip()
                    d = d.rstrip("\xa0")
                    dates[i] = d
                for d in dates:
                    if d[0] == "•":
                        dates.remove(d)
                total += dates  # add dates to list of meetings
            print("SIZE OF TOTAL " + str(total))
            print("SIZE OF CLEAN DATES " + str(clean_dates))
            # get current year based on which table we are on
            curyear = years[tablecount]
            for i in range(len(total)):
                meet = total[i]  # current meeting we are working with
                canceled = FALSE
                splitMeet = meet.split()
                # meeting string is in format "month day" or "month day canceled"
                if len(splitMeet) > 2:
                    if splitMeet[2].strip() == "Canceled":
                        canceled = TRUE
                        meet = splitMeet[0] + " " + splitMeet[1]
                    else:  # if not "canceled", it is unexpected so we throw an error
                        raise ValueError("Unknown addition to date time")
                clean_date = total_clean_dates[i]
                clean_date_list = clean_date.split('"')
                agendaLink = ""
                if len(clean_date_list) > 1:
                    agendaLink = clean_date_list[1]

                meeting = Meeting(
                    title=self._parse_title(),
                    description=self._parse_description(),
                    classification=self._parse_classification(),
                    start=self._parse_start(curyear, meet),
                    end=self._parse_end(),
                    all_day=self._parse_all_day(),
                    time_notes=self._parse_time_notes(),
                    location=self._parse_location(),
                    links=self._parse_links(response, agendaLink),
                    source=self._parse_source(response),
                )
                # check that meeting is in the future, else do not yield the meeting
                if meeting["start"] < datetime.now():
                    continue

                meeting["status"] = self._get_status(meeting)
                # update status if previously determined that meeting was canceled
                if canceled == TRUE:
                    meeting["status"] = self._get_status(
                        item, text="Meeting is cancelled"
                    )
                meeting["id"] = self._get_id(meeting)

                yield meeting

            tablecount += 1

    def _parse_title(self):
        return "Committee on Design Meeting"

    def _parse_description(self):
        return (
            "The Committee on Design is a volunteer group of 24 urban "
            "design professionals organized by the Department of Planning and"
            " Development (DPD) to advise Commissioner Maurice Cox and DPD"
            " staff on design excellence for key development projects "
            "and urban design initiatives."
        )

    def _parse_classification(self):
        return "COMMITTEE"

    def _parse_start(self, curyear, monthDay):
        """Parse start datetime as a naive datetime object."""
        return datetime.strptime(
            "{} {} 1PM".format(monthDay.strip(), curyear), "%B %d %Y %I%p"
        )

    def _parse_end(self):
        return None

    def _parse_time_notes(self):
        return "Historically, meetings have started at 1:00pm or 1:30pm"

    def _parse_all_day(self):
        return False

    def _parse_location(self):
        """Parse or generate location."""
        return {
            "address": "Virtual",
            "name": "Virtual",
        }

    def _parse_links(self, response, agendaLink):
        """Parse or generate links."""
        text = response.css("main").css("p").css("a::text").get()
        if text != "live streamed":
            raise ValueError("Live Stream link has changed")
        if agendaLink != "":
            return [
                {
                    "href": response.css("main").css("p").css("a::attr(href)").get(),
                    "title": "Meeting Link",
                },
                {"href": agendaLink, "title": "Agenda"},
            ]
        return [
            {
                "href": response.css("main").css("p").css("a::attr(href)").get(),
                "title": "Meeting Link",
            }
        ]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
