from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from datetime import datetime


class ChiNorthwestHomeEquitySpider(CityScrapersSpider):
    name = "chi_northwest_home_equity"
    agency = "Chicago Northwest Home Equity Assurance Program"
    timezone = "America/Chicago"
    allowed_domains = ["nwheap.com"]
    start_urls = ["https://nwheap.com/category/meet-minutes-and-agendas/"]

    #used to convert month to number month, help with mm/dd/yyyy formatting
    calendar = {"january": "01",
                "february": "02",
                "march": "03",
                "april": "04",
                "may": "05",
                "june": "06",
                "july": "07",
                "august": "08",
                "september": "09",
                "october": "10",
                "november": "11",
                "december": "12"}

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """

        #the page contains a list of meetings minute, which are past meetings,
        #and upcomming meetings
        #we parsed both sections and return the meetings the best way we can
        futureMeetings = response.xpath("//aside[@id='em_widget-5']/ul/li[not(@class)]")
        pastMeetings = response.xpath("//div[@class='post-loop-content']")
        
        #loop through the meetings minute (past meetings)
        for post in pastMeetings:
            meeting = Meeting(
                title=self._parse_title(post, True),
                description=self._parse_description(post, True),
                classification=self._parse_classification(post),
                start=self._parse_start(post, True, response),
                end=self._parse_end(post, True, response),
                all_day=self._parse_all_day(post, True),
                time_notes=self._parse_time_notes(post, True),
                location=self._parse_location(post, True, response),
                links=self._parse_links(post, True),
                source=self._parse_source(response)
            )
            
            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

        #loop through the upcomming meetings
        for post in futureMeetings:
            meeting = Meeting(
                title=self._parse_title(post, False),
                description=self._parse_description(post, False),
                classification=self._parse_classification(post),
                start=self._parse_start(post, False, response),
                end=self._parse_end(post, False, response),
                all_day=self._parse_all_day(post, False),
                location=self._parse_location(post, False, response),
                links=self._parse_links(post, False),
                source=self._parse_source(response)
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    #to prevent rewriting the same functions for two cases (past/future),
    #we pass in an 'isPast' boolean to determine which case

    def _parse_title(self, item, isPast):
        """Parse or generate meeting title."""
        if isPast:
            title = item.xpath(".//h2[@class='entry-title']/a/text()").get()
        else:
            title = item.xpath("./a/text()").extract()[0]
            
        return title

    def _parse_description(self, item, isPast):
        """Parse or generate meeting description."""
        if isPast:
            description = item.xpath("./div[@class='entry-content']/p/text()").get()
            
            #some meeting minutes don't have descriptions
            if not description:
                description = ""
        else:
            #upcomming meetings don't have descriptions at all
            description = ""
        
        return description

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        #Northwest Home Equity Assurance Program is governing commission appointed by the mayor
        return COMMISSION

    def _parse_start(self, item, isPast, response):
        """Parse start datetime as a naive datetime object."""
        #finding the start datetime is tricky for past meetings
        #the website doesn't have a constant way of telling date/time
        #Our methodology uses the meeting's date to search for sidebar 
        #past meeting and fetch the time
        if isPast:
            #sometimes the date is in the title of that Meet Minutes
            title = item.xpath(".//h2[@class='entry-title']/a/text()").extract()
            date = title[0].split(" ")[0:3]

            monthNumberString = date[0].lower()
            monthNumberString = self.calendar.get(monthNumberString)
            dayString = date[1].replace(",", "")
            yearString = date[2]

            #if the string fetched is not a month then search for it in the description
            if not monthNumberString:
                description = item.xpath("./div[@class='entry-content']/p/text()").get()
                description  = description.split(" ")
                monthNumberString = ""
                
                #check each word in the description if it is a month
                for i in range(len(description)):

                    if self.calendar.get(description[i].lower()):
                        monthNumberString += self.calendar[description[i].lower()]

                        #there are different formatting of month, day, and year
                        #the day could be before or after the year
                        if (len(description[i+1]) >= 4):
                            dayString = description[i-1].replace(",","")
                            yearString = description[i+1][:4]

                        else:
                            dayString = description[i+1].replace(",","")
                            yearString = description[i+2][:4]

            #in case the day is only a single digit
            if len(dayString) == 1:
                dayString = "0" + dayString

            #create the complete date string
            dateStringFourDigit = "/".join([monthNumberString, dayString, yearString])

            queryString = "//ul[li='" + dateStringFourDigit + "']/li[2]/text()"

            #search the time in the Past Meeting sidebar
            timeString = response.xpath(queryString).get()

            #not found then default to 12am
            if not timeString:
                timeString = "12:00:00AM"
            else:
                timeString = timeString.split(" ")
                timeString = timeString[0] + ":00" + timeString[1].upper()

            dateString = dateStringFourDigit + " " + timeString
            datetimeFormat = "%m/%d/%Y %H:%M:%S%p"

            start = datetime.strptime(dateString, datetimeFormat)

        else:
            #getting the time from upcomming events sidebar
            date = item.xpath("./ul/li/text()")[0].extract()
            timeSpan = item.xpath("./ul/li/text()")[1].extract()
            timeArr = timeSpan.split(" ")
            timeString = timeArr[0] + ":00" + timeArr[1].upper()
            
            dateString = date + " " + timeString
            datetimeFormat = "%m/%d/%Y %H:%M:%S%p"

            start = datetime.strptime(dateString, datetimeFormat)

        return start

    def _parse_end(self, item, isPast, response):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        #finding the end time is similar to finding the start time
        
        if isPast:
            #using the same strategy as finding the start time
            title = item.xpath(".//h2[@class='entry-title']/a/text()").extract()
            date = title[0].split(" ")[0:3]

            monthNumberString = date[0].lower()
            monthNumberString = self.calendar.get(monthNumberString)
            dayString = date[1].replace(",", "")
            yearString = date[2]

            #if the string fetched is not a month then search for it in the description
            if not monthNumberString:
                description = item.xpath("./div[@class='entry-content']/p/text()").get()
                description  = description.split(" ")
                monthNumberString = ""
                
                #check each word in the description if it is a month
                for i in range(len(description)):

                    if self.calendar.get(description[i].lower()):
                        monthNumberString += self.calendar[description[i].lower()]

                        #there are different formatting of month, day, and year
                        #the day could be before or after the year
                        if (len(description[i+1]) >= 4):
                            dayString = description[i-1].replace(",","")
                            yearString = description[i+1][:4]

                        else:
                            dayString = description[i+1].replace(",","")
                            yearString = description[i+2][:4]

            #in case the day is only a single digit
            if len(dayString) == 1:
                dayString = "0" + dayString

            #create the complete date string
            dateStringFourDigit = "/".join([monthNumberString, dayString, yearString])

            queryString = "//ul[li='" + dateStringFourDigit + "']/li[2]/text()"

            #search the time in the Past Meeting sidebar
            timeString = response.xpath(queryString).get()


            if not timeString:
                end = None
            
            else:
                #the only difference is that the end time will be in a different index
                timeString = timeString.split(" ")
                timeString = timeString[3] + ":00" + timeString[4].upper()

                dateString = dateStringFourDigit + " " + timeString
                datetimeFormat = "%m/%d/%Y %H:%M:%S%p"
                end = datetime.strptime(dateString, datetimeFormat)

        else:
            date = item.xpath("./ul/li/text()")[0].extract()
            timeSpan = item.xpath("./ul/li/text()")[1].extract()
            timeArr = timeSpan.split(" ")
            timeString = timeArr[3] + ":00" + timeArr[4].upper()
            
            dateString = date + " " + timeString
            datetimeFormat = "%m/%d/%Y %H:%M:%S%p"

            end = datetime.strptime(dateString, datetimeFormat)
        
        return end

    def _parse_time_notes(self, item, isPast):
        """Parse any additional notes on the timing of the meeting"""
        #there are no examples of notes about meeting times for any of the meetings on this site
        if isPast:
            return ""
        else:
            return ""

    def _parse_all_day(self, item, isPast):
        """Parse or generate all-day status. Defaults to False."""
        #none of the meetings were marked as all day, no way to know how they would mark it as such
        if isPast:
            return False
        else:
            return False

    def _parse_location(self, item, isPast, response):
        """Parse or generate location."""
        #the meeting minutes don't tell the address of the past meetings
        #it is possible to get the address from the Past Meeting sidebar
        if isPast:
            #similar to the _parse_start and _parse_end, 
            #try to fetch the information from the Past Meeting sidebar
            #by using the dates obtain from the meeting minutes
            title = item.xpath(".//h2[@class='entry-title']/a/text()").extract()
            date = title[0].split(" ")[0:3]

            monthNumberString = date[0].lower()
            monthNumberString = self.calendar.get(monthNumberString)
            dayString = date[1].replace(",", "")
            yearString = date[2]

            #if the string fetched is not a month then search for it in the description
            if not monthNumberString:
                description = item.xpath("./div[@class='entry-content']/p/text()").get()
                description  = description.split(" ")
                monthNumberString = ""
                
                #check each word in the description if it is a month
                for i in range(len(description)):

                    if self.calendar.get(description[i].lower()):
                        monthNumberString += self.calendar[description[i].lower()]

                        #there are different formatting of month, day, and year
                        #the day could be before or after the year
                        if (len(description[i+1]) >= 4):
                            dayString = description[i-1].replace(",","")
                            yearString = description[i+1][:4]

                        else:
                            dayString = description[i+1].replace(",","")
                            yearString = description[i+2][:4]

            #in case the day is only a single digit
            if len(dayString) == 1:
                dayString = "0" + dayString

            #create the complete date string
            dateString = "/".join([monthNumberString, dayString, yearString])

            #the street address and city are in different "li" elements
            queryStringStreetAddress = "//ul[li='" + dateString + "']/li[3]/text()"
            queryStringCity = "//ul[li='" + dateString + "']/li[4]/text()"

            streetAddress = response.xpath(queryStringStreetAddress).get()
            city = response.xpath(queryStringCity).get()

            if (streetAddress and city):
                address = ", ".join([streetAddress.strip(), city.strip(), "IL"])
                name = ""
            #we'll return an empty if the address cannot be found
            else:
                address = ""
                name = "TBD"

        else:
            #the address are within the upcomming events sidebar
            street = item.xpath("./ul/li/text()")[2].extract().strip()
            city = item.xpath("./ul/li/text()")[3].extract().strip()
            state = "IL"
            address = ", ".join([street,city,state])
            name = ""

        return {
            "address": address,
            "name": name,
        }

    def _parse_links(self, item, isPast):
        """Parse or generate links."""
        #grabs the links to the specific page for each meeting, on that page we can find the links
        if isPast:
            title = item.xpath(".//h2[@class='entry-title']/a/text()").get()
            href = item.xpath(".//h2[@class='entry-title']/a/@href").get()
        else:
            title = item.xpath("./a/text()").extract()[0]
            href = item.xpath("./a/@href").extract()[0]

        return [{"href": href, "title": title}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
