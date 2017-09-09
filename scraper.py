
# We import the dependencies
import json
import time
from lxml.html import fromstring
import cssselect
import datetime as dt
import pytz
import requests


class LandBankScraper:
  
    API_url = 'http://www.cookcountylandbank.org/wp-admin/admin-ajax.php'
    scraped_events = []
    time_horizon = 7
    # time_horizon = 90
    date_stack = []

    def daterange(self, start_date, end_date):
        for n in range(int ((end_date - start_date).days)):
            yield start_date + dt.timedelta(n)

    def stack_dates(self, time_horizon):

        min_date = dt.date(dt.date.today().year, 9, 5)
        min_date = dt.date.today()
        max_date = min_date + dt.timedelta(days=time_horizon)
        dates = [date for date in self.daterange(min_date, max_date)]
        return dates

    def get_events_info(self, date):

        # Posting to the API
        data = {
        'action':'the_ajax_hook',
        # 'current_month': str(date.month),
        # 'current_year': str(date.year),
        # 'event_count':'0',
        # 'fc_focus_day': str(date.day),

        'current_month': '8',
        'current_year': '2017',
        'event_count':'0',
        'fc_focus_day': 11,

        'filters[0][filter_type]':'tax',
        'filters[0][filter_name]':'event_type',
        'filters[0][filter_val]':'9, 16, 17, 18, 19, 20, 26, 27',
        'direction':'none',
        'shortcode[hide_past]':'no',
        'shortcode[show_et_ft_img]':'no',
        'shortcode[event_order]':'DESC',
        'shortcode[ft_event_priority]':'no',
        'shortcode[lang]':'L1',
        'shortcode[month_incre]':'0',
        'shortcode[evc_open]':'no',
        'shortcode[show_limit]':'no',
        'shortcode[etc_override]':'no',
        'shortcode[tiles]':'no',
        'shortcode[tile_height]':'0',
        'shortcode[tile_bg]':'0',
        'shortcode[tile_count]':'2'
        }
        # Making the post request
        response = requests.post(self.API_url, data=data)

        # The data that we are looking is in the second
        # Element of the response and has the key 'data', 
        # so that is what's returned
        return response.json()['content']

    def parse_events(self, data):
        # Creating an lxml Element instance
        element = fromstring(data)

        event_info = {}

        if not element.cssselect('div.eventon_list_event p.no_events'):
            event_id = element.cssselect('div[data-event_id]')[0].get('data-event_id')
            start_date = element.cssselect('[itemprop=\'startDate\']')[0].get('datetime')
            end_date = element.cssselect('[itemprop=\'endDate\']')[0].get('datetime')
            street_address = element.cssselect('item [itemprop=\'streetAddress\']')[0].text
            start_time = element.cssselect('em.evo_time span[class=\'start\']')[0].text
            start_time = dt.datetime.strptime(start_date + ' ' + start_time, '%Y-%m-%d %I:%M %p')
            start_time = pytz.timezone('US/Central').localize(start_time)

            location_detail = element.cssselect('span[class=\'evcal_desc evo_info \']')[0].get('data-location_name')
            name = element.cssselect('span[class=\'evcal_desc2 evcal_event_title\']')[0].text
            source_url = element.cssselect('div[class=\'evo_event_schema\'] a[itemprop=\"url\"]')[0].get('href')
            agenda = []
            for item in element.cssselect('div[class=\'eventon_desc_in\'] h4'): 
            # There's some more advanced set / regex logic you can do in scrapy, if you want to capture all these list items. Not now.
                description = item.text
                if description:
                    agenda.append(description)
                else:
                    continue

            if dt.datetime.today() > dt.datetime.strptime(start_date, '%Y-%m-%d'):
                status = 'passed'
            else:
                status = 'confirmed'

            event_info = {
                        'name': name,
                        'description': '',
                        'classification': '',
                        'start_time': start_time,
                        'timezone': 'US/Central',
                        'street_adress': street_address,
                        'end_time': '',
                        'all_day': False,
                        'status': status,
                        'location': {
                                    'url': 'http://www.cookcountylandbank.org/',
                                    'name': location_detail + ", " + street_address,
                                    'coordinates': {
                                                    'latitude': '',
                                                    'longitude': ''
                                                    },
                                    },
                        'agenda': agenda,
                        'updated_at': dt.date.today(),
                        'sources': {
                                    'url': source_url,
                                    'note': 'Event Page'
                                    }
                        }
            
            self.scraped_events.append(event_info)
        else: 
            return

        import pdb; pdb.set_trace()

    def run(self):
        # Create list of dates to query
        self.date_stack = self.stack_dates(self.time_horizon)
        progress = ""
        stack_depth = len(self.date_stack)

        while self.date_stack:
            query_date = self.date_stack.pop()
            date_event_data = self.get_events_info(query_date)
            self.parse_events(date_event_data)

            progress += "."
            print("Scraping" + progress + str(stack_depth - len(self.date_stack)) + "/" + str(stack_depth), end="\r")
            time.sleep(5)

        print('Scraped!')

        self.save_data()

    def save_data(self):
        with open('events.json', 'w') as json_file:
            json.dump(self.scraped_events, json_file, indent=4)

if __name__ == '__main__':
    scraper = LandBankScraper()
    scraper.run()

# Note: Address validation / standardization is free from the USPS via API (maybe not necessary)
# Google geocoding API: https://developers.google.com/maps/documentation/geocoding/start

