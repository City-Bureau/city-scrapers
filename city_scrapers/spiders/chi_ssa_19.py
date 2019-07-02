from datetime import time

from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.mixins import ChiRogersParkSsaMixin


class ChiSsa19Spider(ChiRogersParkSsaMixin, CityScrapersSpider):
    name = "chi_ssa_19"
    agency = "Chicago Special Service Area #19 Howard Street"
    start_urls = ["https://rpba.org/ssa-19/"]
    location = {
        "name": "The Factory Theater",
        "address": "1623 W Howard St Chicago, IL 60626",
    }
    start_time = time(8, 30)

    def _validate_location(self, response):
        if "1623 w" not in " ".join(response.css(".et_pb_tab_0 *::text").extract()).lower():
            raise ValueError("Meeting location has changed")
