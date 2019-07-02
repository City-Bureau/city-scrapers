from datetime import time

from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.mixins import ChiRogersParkSsaMixin


class ChiSsa24Spider(ChiRogersParkSsaMixin, CityScrapersSpider):
    name = "chi_ssa_24"
    agency = "Chicago Special Service Area #24 Clark/Morse/Glenwood"
    start_urls = ["https://rpba.org/ssa-24/"]
    location = {
        "name": "RPBA Office",
        "address": "1448 W Morse Ave Chicago, IL 60626",
    }
    start_time = time(9)

    def _validate_location(self, response):
        if "1448 w" not in " ".join(response.css(".et_pb_tab_0 *::text").extract()).lower():
            raise ValueError("Meeting location has changed")
