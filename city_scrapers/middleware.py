from city_scrapers_core.items import Meeting
from scrapy_wayback_middleware import WaybackMiddleware


class CityScrapersWaybackMiddleware(WaybackMiddleware):
    def get_item_urls(self, item):
        if isinstance(item, Meeting):
            return [link.get("href") for link in item.get("links", [])]
        if isinstance(item, dict):
            return [doc.get("url") for doc in item.get("documents", [])]
        return []
