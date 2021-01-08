import random

from city_scrapers_core.items import Meeting
from scrapy_wayback_middleware import WaybackMiddleware


class CityScrapersWaybackMiddleware(WaybackMiddleware):
    def get_item_urls(self, item):
        MAX_LINKS = 3
        if isinstance(item, Meeting):
            links = []
            if "legistar" in item["source"] and "Calendar.aspx" not in item["source"]:
                links = [item["source"]]
            links.extend(
                random.sample(
                    [link.get("href") for link in item.get("links", [])], MAX_LINKS
                )
            )
            return links
        if isinstance(item, dict):
            return random.sample(
                [doc.get("url") for doc in item.get("documents", [])], MAX_LINKS
            )
        return []
