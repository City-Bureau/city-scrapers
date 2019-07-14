import re
from datetime import datetime

from city_scrapers_core.constants import COMMISSION, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from parsel import Selector
from scrapy.http import HtmlResponse


class ChiSsa27Spidertesttest(CityScrapersSpider):
    name = "chi_ssa_27testtest"
    agency = "Chicago Special Service Area #27 Lakeview West"
    timezone = "America/Chicago"
    allowed_domains = ["lakeviewchamber.com"]
    start_urls = ["https://www.lakeviewchamber.com/ssa27"]


    def parse(self, response):
        """   `parse` should always `yield` Meeting items. """
        location_commission, location_committee = self.get_expected_locations()
        container = response.css("div.container.content.no-padding")
        commission_panel = container.css("#content-232764 div.panel-body p")
        meeting_url = response.url
        comm_meets_list, comm_meeting_address = self.get_committees(response)
        self._validate_locations(response, comm_meeting_address)
        commission_pan = commission_panel[1:]
        for item in [*commission_pan, *comm_meets_list]:  # main

            if 'dict' in str(type(item)):
                loc = location_committee
            else:
                loc = location_commission
            meeting = Meeting(
                title=self._parse_title(item),
                description=self._parse_description(item),
                classification=self._parse_classification(item),
                start=self._parse_start(item),
                end=None,
                all_day=False,
                time_notes="",
                location=loc,
                links=self._parse_links(item),
                source=meeting_url,
            )
            meeting['status'] = ''
            # meeting['status'] = self._get_status(meeting)
            meeting['id'] = self._get_id(meeting)
            yield meeting

    def get_committees(self, response):
        r = response.css("#content-238036 div.panel-body h4::text").getall()
        meets_len = len(r) + 1
        comm_meets_list, comm_mtg_addy = [], ''

        for cycle in range(1, meets_len * 3, 4):
            this_meet_d = dict()
            front_str4 = "#content-238036 div.panel-body"

            titlestr = front_str4 + " h4:nth-child(" + str(cycle) + ")::text"
            desstr = "#content-238036 div.panel-body h4:nth-child(" + str(cycle) + ") + p::text"
            meetstr1 = "#content-238036 div.panel-body h4:nth-child(" + str(
                cycle) + ") + p + p::text"
            datetimestr = "#content-238036 div.panel-body h4:nth-child(" + str(
                cycle) + ") + p + p strong::text"

            title = response.css(titlestr).get()
            description = response.css(desstr).get()
            nxt_meet_str1 = response.css(datetimestr).get()

            this_meet_d.update({'title': title})
            this_meet_d.update({'desc': description})
            this_meet_d.update({'next_m1': nxt_meet_str1})

            datetimes = response.css(meetstr1).get()
            item_txt = Selector(text=datetimes).css("p::text").get()
            the_href = Selector(text=datetimes).css('a::attr(href)').get()
            com_str = "#content-238036 div.panel-body p em::text"
            comm_mtg_addy = ' '.join(response.css(com_str).getall())

            if '2019' in item_txt:
                words = [("Sept", "Sep"), ("June", "Jun"), ("am", "AM"), ("pm", "PM"),
                         (".", ""), ("\xa0", ""), ("-", "")]
                for tup in words:
                    item_txt = item_txt.replace(tup[0], tup[1])
                    while item_txt[-1] == ' ':
                        item_txt = item_txt.strip(' ')

                new_date = datetime.strptime(item_txt, '%b %d, %Y, %H:%M %p')
                this_meet_d.update({'date_time': new_date})
                this_meet_d.update({'time_notes': ''})

            else:
                place_holder_date = datetime(1900, 1, 1)
                time_notes = item_txt.replace('\xa0', '')
                this_meet_d.update({'date_time': place_holder_date})
                this_meet_d.update({'time_notes': time_notes})

                if the_href:
                    this_meet_d.update({'url_link': the_href})

            comm_meets_list.append(this_meet_d)
        return comm_meets_list, comm_mtg_addy


    def _parse_title(self, item):
        if 'dict' in str(type(item)):
            return item.get('committee_name')
        elif "Annual Meeting" in ''.join(item.css("p::text").getall()):
            return "Annual Meeting"
        else:
            return COMMISSION

    def _parse_timenotes(self, item):
        if "content-238036" in item.css('*::text'):  # Committee
            return item.get('time_notes')
        else:
            return ''

    def _parse_classification(self, item):
        if 'dict' in str(type(item)):
            return COMMITTEE
        else:
            return COMMISSION

    def _parse_description(self, item):
        if 'dict' in str(type(item)):
            return item.get('meeting_desc')

    def _parse_start(self, item):
        if 'dict' not in str(type(item)):

            #if "content-232764" in item.css('*::text') or "content-232764" in str(item.xpath):

            item_txt = ' '.join(item.css('*::text').extract()).strip()
            item_txt = re.sub("Annual Meeting", "", item_txt)
            item_txt = item_txt.replace("June", 'Jun').replace("Sept", 'Sep')
            p_idx = max(item_txt.find('am'), item_txt.find('pm'), 0) + 2  # so we can slice
            front_str = item_txt[:p_idx]  # strip rest of the string
            time_str = front_str.replace("am", "AM").replace("pm", "PM").replace('.', '')
            return datetime.strptime(time_str, '%b %d, %Y, %H:%M %p')
        else:
            comm_val = item.get('date_time')
            print()
            return item.get('date_time')

    def _parse_links(self, item):
        if 'dict' in str(type(item)):
            #if "content-238036" in item.css('*::text'):  # Committee
            return item.get('url_link')
        elif not item.css('a'):
            return []
        else:
            return [{'href': item.css('a::attr(href)').get(), 'title': 'Minutes'}]

    def _validate_locations(self, response, location_committee):
        css_path = "#content-232764 > div > div.panel-body > p:nth-child(1) > strong::text"
        if "Sheil" not in str(response.xpath):
            pass
        # if "Sheil" not in " ".join(response.css(css_path).extract()):
        # raise ValueError("Commission Meeting location has changed")
        if "Chamber" not in location_committee:
            pass
            # raise ValueError("Committee Meeting location has changed")

    def get_expected_locations(self):
        location_commission = {
            "name": "Sheil Park",
            "address": "3505 N. Southport Ave., Chicago, IL 60657",
        }
        location_committee = {
            "name": "Lakeview Chamber of Commerce",
            "address": "1409 W. Addison St. in Chicago",
        }
        return location_commission, location_committee
