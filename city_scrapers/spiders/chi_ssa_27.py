from datetime import datetime

from city_scrapers_core.constants import COMMISSION, COMMITTEE, TENTATIVE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider

from parsel import SelectorList


class ChiSsa27Spider(CityScrapersSpider):
    name = "chi_ssa_27"
    agency = "Chicago Special Service Area #27 Lakeview West"
    timezone = "America/Chicago"
    allowed_domains = ["lakeviewchamber.com"]
    start_urls = ["https://www.lakeviewchamber.com/ssa27"]

    def parse_committee(self, two, url2):
        print("here now2222")
        meeting_group, biglist = [], []
        h1, h2 = "<h4>", "</h4>"
        p1, p2 = "<p>", "</p>"
        s1, s2 = "<strong>", "</strong>"
        e1, e2 = "<em>", "</em>"
        #nextmeeting = two.css("p > strong ::text").get()
        meet_list = two.css("*").getall()



        for meeting_itm in meet_list:
            if '<h4>' in meeting_itm:
                print("found h4")


            if '<hr>' in meeting_itm:  # end of previous meeting
                meeting_group_copy = [i for i in meeting_group]
                biglist.append(meeting_group_copy)
                meeting_group.clear()
                continue
            else:
                meeting_group.append(meeting_itm)

        print("here now345")

        for group_mtg in biglist:
            commmittee_mtg_desc = ''
            committee_nxt_mtg = ''
            for itm in group_mtg:
                if s1 in itm and p1 not in itm and e1 not in itm:  # for double listing of strong
                    print(str(meeting))
                    meeting.clear()
                    continue

                if h1 in itm:
                    committee_name = itm.replace(h1, '').replace(h2, '')

                if s1 in itm and e1 not in itm:
                    committee_nxt_mtg = itm.replace(s1, '').replace(s2, '').replace(p1, '').replace(p2, '')

                if p1 in itm and s1 not in itm and e1 not in itm:
                    commmittee_mtg_desc = commmittee_mtg_desc + itm.replace(p1, '').replace(p2, '')  # might be 2

                if e1 in meeting_itm:
                    comm_mtg_location = itm.replace(e1, '').replace(e2, '').replace(p1, '').replace(p2, '')

                print("here now3fff")
                meeting = Meeting(
                    title=committee_name,
                    description=commmittee_mtg_desc,
                    classification=COMMITTEE,
                    start=datetime.now(),
                    #start=self._parse_start(meeting_itm),
                    end=None,
                    all_day=False,
                    time_notes=committee_nxt_mtg,
                    location=comm_mtg_location,
                    # links=self._parse_links(meeting_itm),
                    links='',
                    source=url2,
                )
               # meeting['status'] = self._get_status(meeting)
                meeting['status'] = TENTATIVE
                #meeting['id'] = self._get_id(meeting)
                meeting['id'] = None
                print(str(meeting))



    def parse(self, response):
        """   `parse` should always `yield` Meeting items.
        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping needs.   """
        r = response.css("div.container.content.no-padding")
        one = r.css("#content-232764 div.panel-body p")
        two = r.css("#content-238036 div.panel-body *")
        meeting_location = ''

        for item in one:  # for item in response.css("#content-232764 div.panel-body p"):
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
                source=response.url,
            )
            meeting['status'] = self._get_status(meeting)
            meeting['id'] = self._get_id(meeting)

            yield meeting

        theurl = response.url
        self.parse_committee(two, theurl)
        print("finished")



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
