from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.mixins import ChiMayorsAdvisoryCouncilsMixin


class ChiMayorsBicycleAdvisoryCouncilSpider(
    ChiMayorsAdvisoryCouncilsMixin, CityScrapersSpider
):
    name = "chi_mayors_bicycle_advisory_council"
    agency = "Chicago Mayor's Bicycle Advisory Council"
    start_urls = [
        "https://chicagocompletestreets.org/sample-page-2/mayors-advisory-councils/mbac-meeting-archives/"  # noqa
    ]
    title = "Mayor's Bicycle Advisory Council"
    location = {
        "address": "121 N LaSalle St, Chicago, IL 60602",
        "name": "City Hall, Room 1103",
    }
