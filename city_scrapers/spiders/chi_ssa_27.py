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

    def parse_committee(self, respon, url):
        committee_panel = respon.css("#content-238036 div.panel-body *")
        m2, cleaned = [], []
        h1 = "<h4>"
        p1, p2 = "<p>", "</p>"
        s1 = "<strong>"
        e1 = "<em>"
        meet_list = committee_panel.css("*").getall()

        prev = None
        for meeting_itm in meet_list:  # rem dupes
            if meeting_itm != prev:
                m2.append(meeting_itm)
                prev = meeting_itm

        for this_line in m2:
            if "<h4>" in this_line:
                cleaned.append(this_line)
                continue
            elif p1 in this_line:
                if e1 in this_line:
                    this_line = this_line.replace(p1, '').replace(p2, '')
                cleaned.append(this_line)

        list_mtg_objs, this_mtg = [], dict()
        comm_meeting_address = ''

        for i3 in cleaned:
            if h1 in i3:  # h4
                if this_mtg:
                    list_mtg_objs.append(deepcopy(this_mtg))
                this_mtg = dict()
                committee_name = Selector(text=i3).css("h4::text").get()
                this_mtg.update({'committee_name': committee_name})
            elif s1 in i3:  # strong
                nxt_nme2 = Selector(text=i3).css("p::text").get()
                the_href = Selector(text=i3).css('a::attr(href)').get()

                if '2019' in nxt_nme2:
                    item_txt = nxt_nme2.replace("Sept", 'Sep').replace("June", 'Jun')
                    p_idx = max(item_txt.find('am'), item_txt.find('pm'), 0) + 2  # so we can slice
                    front_str = item_txt[:p_idx]  # remove comments from the rest of the string
                    time_str = front_str.replace("am", "AM").replace("pm", "PM")\
                        .replace('.', '').replace('\xa0', '')
                    new_date = datetime.strptime(time_str, '%b %d, %Y, %H:%M %p')
                    this_mtg.update({'date_time': new_date})
                    this_mtg.update({'time_notes': ''})
                else:
                    nxt_nme2 = nxt_nme2.replace('\xa0', '')
                    this_mtg.update({'date_time': datetime(1900, 1, 1)})
                    this_mtg.update({'time_notes': nxt_nme2})

                if the_href:
                    this_mtg.update({'url_link': the_href})

            elif p1 in i3:
                comm_des = Selector(text=i3).css("p::text").get()
                this_mtg.update({'meeting_desc': comm_des})
            if e1 in i3:
                comm_meeting_address = Selector(text=i3).css("em::text").get()
                list_mtg_objs.append(deepcopy(this_mtg))

        final_meeting_obj = []

        for meeting_group in list_mtg_objs:
            meeting = Meeting(
                title=meeting_group.get('committee_name'),
                description=meeting_group.get('meeting_desc'),
                classification=COMMITTEE,
                start=meeting_group.get('date_time'),  # fix soon
                end=None,
                all_day=False,
                time_notes=meeting_group.get('time_notes'),  # fix soon
                location=comm_meeting_address,
                links=meeting_group.get('url_link'),  # fix soon
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
        item_txt = ' '.join(item.css('*::text').extract()).strip()
        item_txt = item_txt.replace("Annual Meeting", '').replace("Sept", 'Sep')
        item_txt = item_txt.replace("June", 'Jun')
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
'''
It's less relevant now, but once you add committees it'll be good to add a test_count function 
to make sure that the right meetings are being included like we have here

city-scrapers/tests/test_cook_board.py

Line 17 in bc1d5ff

 def test_count(): 
 
 '''


'''Once you start checking committees, it might be easier to pass the response to the function checking the location since the location won't be in the second block of items. We've been storing any location that we're validating in self.location and calling the method _validate_location in this case just to make things more clear. You can see an example here

city-scrapers/city_scrapers/spiders/chi_ssa_34.py

Line 28 in c23f1fd

 self._validate_location(response) 
 '''


'''tests/test_chi_ssa_27.py
parsed_items = [item for item in spider.parse(test_response)]

 freezer.stop()

  @pjsier
pjsier 17 hours ago  Member
It's less relevant now, but once you add committees it'll be good to add a test_count function to make sure that the right meetings are being included like we have here

city-scrapers/tests/test_cook_board.py

Line 17 in bc1d5ff

 def test_count(): 
 
 '''