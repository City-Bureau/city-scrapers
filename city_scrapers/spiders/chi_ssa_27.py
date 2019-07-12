from copy import deepcopy
from datetime import datetime, timedelta

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


    def parse_committee(self, respon, url):
        meeting_list, cleaned = [], []
        committee_panel = respon.css("#content-238036 div.panel-body *")
        m2, cleaned = [], []
        h1, h2 = "<h4>", "</h4>"
        p1, p2 = "<p>", "</p>"
        s1, s2 = "<strong>", "</strong>"
        e1, e2 = "<em>", "</em>"
        meet_list = committee_panel.css("*").getall()

        prev = None
        for meeting_itm in meet_list:   # rem dupes
            if meeting_itm != prev:
                m2.append(meeting_itm)
                prev = meeting_itm

        for m in m2:
            if h1 in m:
                cleaned.append(m)
                continue
            if p1 in m:
                if e1 in m:
                    m = m.replace(p1,'').replace(p1,'')
                cleaned.append(m)


        dcomms, dd = [],  dict({})
        for i3 in cleaned:
            if h1 in i3:   #h4
                my_copy = deepcopy(dd)
                dcomms.append(my_copy)
                dd = dict({})
                commt_nme = Selector(text=i3).css("h4::text").get()
                dd.update({'committee_name' : commt_nme})
                print()
            elif s1 in i3:  #strong
                nxt_nme = Selector(text=i3).css("strong::text").get()
                dd.update({'comm_nxt_mtg' : nxt_nme})
            elif p1 in i3:
                comm_des = Selector(text=i3).css("p::text").get()
                dd.update({'comm_des' : comm_des})
            if e1 in i3:
                comm_addy = Selector(text=i3).css("em::text").get()
                my_copy = deepcopy(dd)
                dcomms.append(my_copy)
        raw_meeting_list = []
        previous_line = None
        for meeting_itm in committee_panel.xpath("/div "):   # rem dupes
            mmm = meeting_itm.xpath("div div")
            if meeting_itm != previous_line:
                meeting_list.append(meeting_itm)
                previous_line = meeting_itm

        meeting_dict = []
        d_item = None
        for meet in meeting_list:
            if "<h4>" in meet:   #h4
                if d_item:
                    meeting_dict.append(deepcopy(d_item))
                d_item = dict()    # starting new meeting group
                comm_name = Selector(text=meet).css("h4::text").get()
                d_item.update({'committee_name' : comm_name})
            elif "<strong>" in meet and "<p>" not in meet:  #strong
                next_name = Selector(text=meet).css("p > strong::text").get()
                time_item = Selector(text=meet).css("p::text").get()
                d_item.update({'comm_nxt_mtg' : next_name})
                d_item.update({'time_item' : time_item})
            elif "<p>" in meet:
                comm_des = Selector(text=meet).css("p::text").get()
                d_item.update({'comm_des' : comm_des})
            elif "<em>" in meet:
                comm_addy = Selector(text=meet).css("em::text").get()  # same for every meeting

                meeting_dict.append(deepcopy(d_item))    ## at the end if it has "em"

        final_meeting_obj = []
        ttime = datetime.now() + timedelta(days=1, hours=3)
        for m_item in meeting_dict:
            meeting = Meeting(
                title=m_item.get('committee_name'),
                description=m_item.get('comm_des'),
                classification=COMMITTEE,
                start=ttime,   # fix soon
                end=None,
                all_day=False,
                time_notes=m_item.get('comm_nxt_mtg'),  # fix soon
                location=comm_addy,
                links='',  # fix soon
                source=url,
            )
            meeting['status'] = TENTATIVE
            meeting['id'] = self._get_id(meeting)
            final_meeting_obj.append(deepcopy(meeting))
        return final_meeting_obj

    def parse(self, response):
        """   `parse` should always `yield` Meeting items.
        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping needs.   """
        container = response.css("div.container.content.no-padding")
        regular_panel = container.css("#content-232764 div.panel-body p")
        committee_panel = container.css("#content-238036 div.panel-body *")
        meeting_location = ''
        meeting_url = response.url

        for item in regular_panel:  # for item in response.css("#content-232764 div.panel-body p"):
            if item.css("p > strong ::text").getall():
                meeting_location = self._parse_location(item)
                continue

            meeting = Meeting(
                title=self._parse_title(item),
                description="",
                classification=self._parse_classification(),
                start=self._parse_start(item),
                end=None,
                all_day=False,
                time_notes="",
                location=meeting_location,
                links=self._parse_links(item),
                source=meeting_url,
            )
            meeting['status'] = self._get_status(meeting)
            meeting['id'] = self._get_id(meeting)
            yield meeting

        committee_mtgs = self.parse_committee(response, meeting_url)
        for one_meeting in committee_mtgs:
            yield one_meeting



    # ----------------------------------------- regular:


    def _parse_title(self, item):
        """Parse or generate meeting title."""
        item_txt = ''.join(item.css("p::text").getall())
        if "Annual Meeting" in item_txt:
            return "Annual Meeting"
        else:
            return COMMISSION


    def _parse_classification(self):
        # This can return COMMISSION generally or COMMITTEE for the committee meetings
        return COMMISSION


    def _parse_start(self, item):
        item_txt = item.css('a::text').get()
        if not item_txt:
            item_txt = item.css('p::text').get()

        item_txt = item_txt.replace("Annual Meeting", '').replace("Sept", 'Sep')
        p_idx = max(item_txt.find('am'), item_txt.find('pm'), 0) + 2  # so we can slice after this
        front_str = item_txt[:p_idx]  # remove comments from the rest of the string
        time_str = front_str.replace("am", "AM").replace("pm", "PM").replace('.', '')
        return datetime.strptime(time_str, '%b %d, %Y, %H:%M %p')


    def _parse_location(self, item):
        first_note = item.css("p > strong ::text").get()
        if item.css("p > strong ::text").get():
            if "Sheil Park" in first_note:
                return {
                    "address": "3505 N. Southport Ave., Chicago, IL 60657",
                    "name": "Sheil Park",
                }
            else:
                raise ValueError('Meeting address has changed')


    def _parse_links(self, item):
        if not item.css('a'):
            return []
        else:
            return [{'href': item.css('a::attr(href)').get(), 'title': 'Minutes'}]
