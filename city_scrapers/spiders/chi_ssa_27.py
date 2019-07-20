from datetime import date, datetime
from re import split, sub

from city_scrapers_core.constants import COMMISSION, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from scrapy import Field, Item


class ChiSsa27Spider(CityScrapersSpider):
    name = "chi_ssa_27"
    agency = "Chicago Special Service Area #27 Lakeview West"
    timezone = "America/Chicago"
    allowed_domains = ["lakeviewchamber.com"]
    start_urls = ["https://www.lakeviewchamber.com/ssa27"]
    minutes_list = []

    def parse(self, response):
        """   `parse` should always `yield` Meeting items. """
        self.minutes_list = self.get_minutes_panel_items(response)
        self._validate_locations(response)
        locs = "div.container.content.no-padding #content-232764 div.panel-body p"
        for item in response.css(locs)[1:]:  # main
            meeting = Meeting(
                title=self._parse_title(item),
                description='',
                classification='',
                start=self._parse_start(item),
                end=None,
                all_day=False,
                time_notes='',
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=response.url,
            )
            meeting['status'] = self._get_status(meeting)
            meeting['id'] = self._get_id(meeting)
            yield meeting

    def clean_up_title(self, t_name=''):
        if len(t_name) > 0:
            while t_name[0:1] in ['\n', '(']:
                t_name = t_name[1:]
            if t_name[-1] == ')':
                t_name = t_name[:-1]
        return t_name

    def get_minutes_panel_items(self, response):
        class Paragraph(Item):
            link = Field()
            date = Field()
            date2 = Field()
            title = Field()

        panel = response.css("#content-232768 div.panel-body p")[1:]
        min_list = []
        paragraphs = panel.css('p')

        last_paragraph = paragraphs[-1].css('*::text').getall()
        if '\xa0' in last_paragraph:
            paragraphs = paragraphs[:-1]

        first_paragraph = paragraphs[0:1].css('*::text').getall()
        if '\xa0' in first_paragraph:
            paragraphs = paragraphs[1:]

        for p in paragraphs:
            tname = ''
            href = p.css('a::attr(href)').get()
            tlist = p.css('*::text').getall()
            dt_date = datetime.strptime(tlist[0], '%B %d, %Y')
            try:
                tname = tlist[1]
                if tname == '':
                    tname = (split('-', split('/', href)[-1], 3)[-1])[:-4]
            except IndexError:
                pass

            tname = self.clean_up_title(tname)
            d2 = dt_date.date()
            min_list.append(Paragraph(link=href, date=dt_date, date2=d2, title=tname))
        return min_list



    def _parse_links(self, item):
        # MATCH DATE WITH ITEM IN LIST
        the_link = ''
        item_txt = ' '.join(item.css('*::text').extract()).strip()
        item_txt = sub("Annual Meeting", "", item_txt)
        item_txt = item_txt.replace("June", 'Jun').replace("Sept", 'Sep')

        myitms = split(',', item_txt, 4)
        d_date = ''.join([myitms[0], myitms[1]]).replace('.', '')
        dt = datetime.strptime(d_date, '%b %d %Y')
        date_short = dt.date()
        try:
            records = list(filter(lambda d: d['date2'] == date_short, self.minutes_list))
            the_link = records[0]['link']
        except:
            the_link = ''
        return the_link


    def _parse_title(self, item):
        if "Annual Meeting" in ''.join(item.css("p::text").getall()):
            return "Annual Meeting"
        return COMMISSION

    def _parse_location(self, item):
        commission_loc = {"name": "Sheil Park",
            "address": "3505 N. Southport Ave., Chicago, IL 60657", }
        committee_loc = {"name": "Lakeview Chamber of Commerce",
            "address": "1409 W. Addison St. in Chicago", }
        # if self.committee_type(item):
        #     return committee_loc
        return commission_loc

    def _parse_start(self, item):
        item_txt = ' '.join(item.css('*::text').extract()).strip()
        item_txt = sub("Annual Meeting", "", item_txt)
        item_txt = item_txt.replace("June", 'Jun').replace("Sept", 'Sep')
        p_idx = max(item_txt.find('am'), item_txt.find('pm'), 0) + 2  # so we can slice
        front_str = item_txt[:p_idx]  # strip rest of the string
        time_str = front_str.replace("am", "AM").replace("pm", "PM").replace('.', '')
        return datetime.strptime(time_str, '%b %d, %Y, %H:%M %p')

    def _validate_locations(self, response):
        commission_path = "#content-232764 div.panel-body > p:nth-child(1) > strong::text"
        commission_addy = response.css(commission_path).get()
        commission_result = commission_addy.find("Sheil")

        committee_addy = response.css("#content-238036 div.panel-body p em::text").get()
        committee_result = committee_addy.find("Chamber")

        if commission_result < 0:  # fail
            raise ValueError("Commission Meeting location has changed")
        if committee_result < 0:  # fail
            raise ValueError("Committee Meeting location has changed")
