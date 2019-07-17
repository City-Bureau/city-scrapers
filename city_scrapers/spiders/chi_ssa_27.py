import re
from datetime import datetime

from city_scrapers_core.constants import COMMISSION, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from parsel import Selector


class ChiSsa27Spider(CityScrapersSpider):
    name = "chi_ssa_27"
    agency = "Chicago Special Service Area #27 Lakeview West"
    timezone = "America/Chicago"
    allowed_domains = ["lakeviewchamber.com"]
    start_urls = ["https://www.lakeviewchamber.com/ssa27"]

    def parse(self, response):
        """   `parse` should always `yield` Meeting items. """
        container = response.css("div.container.content.no-padding")
        commission_panel = container.css("#content-232764 div.panel-body p")
        #comm_meets_list, comm_meeting_address = self.get_committees(response)
        #self._validate_locations(response, comm_meeting_address)
        self._validate_locations(response)
        commission_pan = commission_panel[1:]

        #for item in [*commission_pan, *comm_meets_list]:  # main
        for item in [*commission_pan]:  # main
            print("item is:", item.css('*').extract(

            ))
            meeting = Meeting(
                title=self._parse_title(item),
                description=self._parse_description(item),
                classification=self._parse_classification(item),
                start=self._parse_start(item),
                end=None,
                all_day=False,
                time_notes=self._parse_timenotes,
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=response.url,
            )

            if self.committee_type(item):  # committee
                meeting['status'] = ''
                meeting['id'] = ''
            else:
                meeting['status'] = self._get_status(meeting)
                meeting['id'] = self._get_id(meeting)
            yield meeting

    def committee_type(self, item):
        if 'dict' in str(type(item)):
            return True
        else:
            return False

    def get_committees(self, response):
        counter = response.css("#content-238036 div.panel-body h4::text").getall()
        meets_len = len(counter) + 1
        comm_meets_list, comm_mtg_addy = [], ''

        for cycle in range(1, meets_len * 3, 4):
            this_meet_d = dict()
            front_str4 = "#content-238036 div.panel-body"

            title_str = front_str4 + " h4:nth-child(" + str(cycle) + ")::text"
            desc_str = "#content-238036 div.panel-body h4:nth-child(" + str(cycle) + ") + p::text"
            meet_str = "#content-238036 div.panel-body h4:nth-child(" + str(
                cycle
            ) + ") + p + p::text"
            date_time_str = "#content-238036 div.panel-body h4:nth-child(" + str(
                cycle
            ) + ") + p + p strong::text"

            title = response.css(title_str).get()
            description = response.css(desc_str).get()
            nxt_meet_str1 = response.css(date_time_str).get()

            this_meet_d.update({'title': title})
            this_meet_d.update({'desc': description})
            this_meet_d.update({'next_m1': nxt_meet_str1})

            date_times = response.css(meet_str).get()
            item_txt = Selector(text=date_times).css("p::text").get()
            the_href = Selector(text=date_times).css('a::attr(href)').get()
            com_str = "#content-238036 div.panel-body p em::text"
            comm_mtg_addy = ' '.join(response.css(com_str).getall())

            if '2019' in item_txt:
                words = [("Sept", "Sep"), ("June", "Jun"), ("am", "AM"), ("pm", "PM"), (".", ""),
                         ("\xa0", ""), ("-", "")]
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
        if self.committee_type(item):
            return item.get('title')
        elif "Annual Meeting" in ''.join(item.css("p::text").getall()):
            return "Annual Meeting"
        else:
            return COMMISSION

    def _parse_timenotes(self, item):
        if self.committee_type(item):
            return item.get('time_notes')
        else:
            return ''

    def _parse_classification(self, item):
        if self.committee_type(item):
            return COMMITTEE
        else:
            return COMMISSION

    def _parse_location(self, item):
        location_commission, location_committee = self.get_expected_locations()
        if self.committee_type(item):
            return location_committee
        else:
            return location_commission

    def _parse_description(self, item):
        if self.committee_type(item):
            return item.get('desc')
        else:
            return ''

    def _parse_start(self, item):
        if self.committee_type(item):
            return item.get('date_time')
        else:
            item_txt = ' '.join(item.css('*::text').extract()).strip()
            item_txt = re.sub("Annual Meeting", "", item_txt)
            item_txt = item_txt.replace("June", 'Jun').replace("Sept", 'Sep')
            p_idx = max(item_txt.find('am'), item_txt.find('pm'), 0) + 2  # so we can slice
            front_str = item_txt[:p_idx]  # strip rest of the string
            time_str = front_str.replace("am", "AM").replace("pm", "PM").replace('.', '')
            return datetime.strptime(time_str, '%b %d, %Y, %H:%M %p')


    def _parse_links(self, item):
        """Parse or generate links"""
        t = item.css('p::text').getall()
        print(t)
        if item.css('a::attr(href)'):
            a_link = item.css('a::attr(href)').extract()
            if a_link.lower().find("minutes"):
                return [a_link]
        return []


    def _validate_locations(self, response, location_committee=''):
        css_path = "#content-232764 > div > div.panel-body > p:nth-child(1) > strong::text"
        commission = response.css(css_path).get().find("Sheil")
        if commission < 0:  # fail
            pass
            #raise ValueError("Commission Meeting location has changed")
        committee = location_committee.find("Chamber")
        if committee < 0:  # fail
            pass
            #raise ValueError("Committee Meeting location has changed")

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
