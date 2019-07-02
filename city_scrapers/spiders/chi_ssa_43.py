from datetime import time

from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.mixins import ChiRogersParkSsaMixin


class ChiSsa43Spider(ChiRogersParkSsaMixin, CityScrapersSpider):
    name = "chi_ssa_43"
    agency = "Chicago Special Service Area #43 Devon Avenue"
    start_urls = ["https://rpba.org/ssa-43/"]
    location = {
        "name": "Ald. Silverstein's Office",
        "address": "2949 W Devon Ave Chicago, IL 60659",
    }
    start_time = time(2, 30)

    def _validate_location(self, response):
        if "2949 w" not in " ".join(response.css(".et_pb_tab_0 *::text").extract()).lower():
            raise ValueError("Meeting location has changed")
