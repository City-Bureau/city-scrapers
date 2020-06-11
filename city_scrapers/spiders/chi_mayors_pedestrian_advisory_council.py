from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.mixins import ChiMayorsAdvisoryCouncilsMixin


class ChiMayorsPedestrianAdvisoryCouncilSpider(
    ChiMayorsAdvisoryCouncilsMixin, CityScrapersSpider
):
    name = "chi_mayors_pedestrian_advisory_council"
    agency = "Chicago Mayor's Pedestrian Advisory Council"
    start_urls = [
        "http://chicagocompletestreets.org/getinvolved/mayors-advisory-councils/mpac-meeting-archives/"  # noqa
    ]
    title = "Mayor's Pedestrian Advisory Council"
    location = {
        "address": "121 N LaSalle St, Chicago, IL 60602",
        "name": "City Hall, Room 1103",
    }
