import re
from copy import deepcopy
from datetime import datetime

from city_scrapers_core.constants import COMMISSION, COMMITTEE, TENTATIVE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from parsel import Selector


class ChiSsa27Spider(CityScrapersSpider):
    name = "chi_ssa_27"
    agency = "Chicago Special Service Area #27 Lakeview West"
    timezone = "America/Chicago"
    allowed_domains = ["lakeviewchamber.com"]
    start_urls = ["https://www.lakeviewchamber.com/ssa27"]
    location = {
        "name": "Sheil Park",
        "address": "3505 N. Southport Ave., Chicago, IL 60657",
    }
    location_committee = {
        "name": "Lakeview Chamber of Commerce",
        "address": "1409 W. Addison St. in Chicago",
    }

    def clean_lines(self, respon):
        prev, meet_list_two, list_mtg_objs, cleaned, this_mtg = None, [], [], [], dict()
        committee_panel = respon.css("#content-238036 div.panel-body *")

        for meeting_itm in committee_panel.css("*").getall():  # rem dupes
            if meeting_itm != prev:
                meet_list_two.append(meeting_itm)
                prev = meeting_itm
        for this_line in meet_list_two:
            if "<h4>" in this_line:
                cleaned.append(this_line)
            elif "<p>" in this_line:
                if "<em>" in this_line:
                    cleaned.append(this_line.replace("<p>", '').replace("</p>", ''))
        return cleaned

    def get_meeting_objects(self, response_main):
        comm_mtg_addy, meet_list_two, list_mtg_objs, this_mtg = '', [], [], dict()
        cleaned = self.clean_lines(response_main)

        for line in cleaned:
            if "<h4>" in line:  # h4
                if this_mtg:
                    list_mtg_objs.append(deepcopy(this_mtg))
                this_mtg = dict()
                this_mtg.update({'committee_name': Selector(text=line).css("h4::text").get()})
            elif "<strong>" in line:  # strong meeting time section
                item_txt = Selector(text=line).css("p::text").get()
                the_href = Selector(text=line).css('a::attr(href)').get()

                if '2019' in item_txt:
                    words = [("Sept", "Sep"), ("June", "Jun"), ("am", "AM"), ("pm", "PM"),
                             (".", ""), ("\xa0", ""), ("-", "")]
                    for tup in words:
                        item_txt = item_txt.replace(tup[0], tup[1])
                        while item_txt[-1] == ' ':
                            item_txt = item_txt.strip(' ')

                    new_date = datetime.strptime(item_txt, '%b %d, %Y, %H:%M %p')
                    this_mtg.update({'date_time': new_date})
                    this_mtg.update({'time_notes': ''})
                else:
                    nxt_nme2 = item_txt.replace('\xa0', '')
                    this_mtg.update({'date_time': datetime(1900, 1, 1)})
                    this_mtg.update({'time_notes': nxt_nme2})

                if the_href:
                    this_mtg.update({'url_link': the_href})

            elif "<p>" in line:
                this_mtg.update({'meeting_desc': Selector(text=line).css("p::text").get()})
            if "<em>" in line:
                list_mtg_objs.append(deepcopy(this_mtg))
                comm_mtg_addy = Selector(text=line).css("em::text").get()
        return list_mtg_objs, comm_mtg_addy

    def parse(self, response):
        """   `parse` should always `yield` Meeting items. """
        container = response.css("div.container.content.no-padding")
        commission_panel = container.css("#content-232764 div.panel-body p")
        meeting_url = response.url
        committee_mtgs, comm_meeting_address = self.get_meeting_objects(response)
        self._validate_location(response)
        self._validate_location_Committee(comm_meeting_address)

        for item in [*commission_panel, *committee_mtgs]:  # main
            if "content-232764" in item.css('*::text'):
                loc = self.location
            else:
                loc = self.location_committee
            meeting = Meeting(
                title=self._parse_title(item),
                description=self._parse_description(item),
                classification=self._parse_classification(item),
                start=self._parse_start(item),
                end=None,
                all_day=False,
                time_notes="",
                location=loc,  ## what about committees?
                links=self._parse_links(item),
                source=meeting_url,
            )
            meeting['status'] = self._get_status(meeting)
            meeting['id'] = self._get_id(meeting)
            yield meeting


    def _parse_title(self, item):
        if "content-232764" in item.css('*::text'):
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
        if "content-232764" in item.css('*::text'):
            return COMMISSION
        else:
            return COMMITTEE

    def _parse_description(self, item):
        if "content-238036" in item.css('*::text'):  # Committee
            return item.get('meeting_desc')

    def _parse_start(self, item):
        if "content-232764" in item.css('*::text'):
            item_txt = ' '.join(item.css('*::text').extract()).strip()
            item_txt = re.sub("Annual Meeting", "", item_txt)
            item_txt = item_txt.replace("June", 'Jun').replace("Sept", 'Sep')
            p_idx = max(item_txt.find('am'), item_txt.find('pm'), 0) + 2  # so we can slice
            front_str = item_txt[:p_idx]  # strip rest of the string
            time_str = front_str.replace("am", "AM").replace("pm", "PM").replace('.', '')
            return datetime.strptime(time_str, '%b %d, %Y, %H:%M %p')
        else:
            return item.get('date_time')

    def _validate_location(self, response):
        css_path = "#content-232764 > div > div.panel-body > p:nth-child(1) > strong::text"
        if "Sheil" not in " ".join(response.css(css_path).extract()):
            raise ValueError("Commission Meeting location has changed")

    def _validate_location_Committee(self, item):
        if "Chamber" not in item:
            raise ValueError("Committee Meeting location has changed")

    def _parse_links(self, item):
        if "content-238036" in item.css('*::text'):  # Committee
            return item.get('url_link')
        elif not item.css('a'):
            return []
        else:
            return [{'href': item.css('a::attr(href)').get(), 'title': 'Minutes'}]
