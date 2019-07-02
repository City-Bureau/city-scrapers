from datetime import time

from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.mixins import ChiRogersParkSsaMixin


class ChiSsa54Spider(ChiRogersParkSsaMixin, CityScrapersSpider):
    name = "chi_ssa_54"
    agency = "Chicago Special Service Area #54 Sheridan Road"
    start_urls = ["https://rpba.org/ssa-54/"]
    location = {
        "name": "Starbucks",
        "address": "6738 N Sheridan Rd Chicago, IL 60626",
    }
    start_time = time(8, 30)

    def _validate_location(self, response):
        if "6738 n" not in " ".join(response.css(".et_pb_tab_0 *::text").extract()).lower():
            raise ValueError("Meeting location has changed")
