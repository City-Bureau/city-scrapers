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
        minutes_panel = container.css("#content-232768 div.panel-body p")
        min_panel_items = self.get_minutes_panel_items(minutes_panel)

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

            if self.item_type(item):  # committee
                meeting['status'] = ''
                meeting['id'] = ''
            else:
                meeting['status'] = self._get_status(meeting)
                meeting['id'] = self._get_id(meeting)
            yield meeting

    def get_minutes_panel_items(self, panel):
        panels = panel.css('p').getall()
        panels2 = panel.css('a::attr(href)').getall()
        panels3 = panel.css("a::text").getall()
        for p in panels:
            p_sel = Selector(text=p)


            p_href = p_sel.css('a::attr(href)').get()
            p_txt = p_sel.css('a::text').getall()

            thislist = []
            aa = [p.css('a::attr(href)').get()]
            bb = p.css('a::text').getall()
            thislist.append(p_href, p_txt)
            cc = aa.append(bb)
            print("p is:", p)
        return panels, panels2

    def item_type(self, item):
        if 'dict' in str(type(item)):
            return True
        else:
            return False

    def _parse_title(self, item):
        if self.item_type(item):
            return item.get('title')
        elif "Annual Meeting" in ''.join(item.css("p::text").getall()):
            return "Annual Meeting"
        else:
            return COMMISSION

    def _parse_timenotes(self, item):
        if self.item_type(item):
            return item.get('time_notes')
        else:
            return ''

    def _parse_classification(self, item):
        if self.item_type(item):
            return COMMITTEE
        else:
            return COMMISSION

    def _parse_location(self, item):
        location_commission, location_committee = self.get_expected_locations()
        if self.item_type(item):
            return location_committee
        else:
            return location_commission

    def _parse_description(self, item):
        if self.item_type(item):
            return item.get('desc')
        else:
            return ''

    def _parse_start(self, item):
        if self.item_type(item):
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
