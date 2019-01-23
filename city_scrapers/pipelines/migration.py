from datetime import datetime, time

from city_scrapers_core.decorators import ignore_jscalendar
from city_scrapers_core.items import Meeting


class MigrationPipeline:
    """Migrates to city_scrapers_core Meeting object instead of dictionaries"""

    @ignore_jscalendar
    def process_item(self, item, spider):
        if isinstance(item, Meeting):
            return item
        meeting = Meeting(
            id=item["id"],
            title=item["name"],
            description=item.get("event_description"),
            classification=item["classification"],
            status=self._get_status(item["status"]),
            start=self._get_datetime(item["start"]),
            end=self._get_datetime(item["end"], is_end=True),
            all_day=item["all_day"],
            time_notes=self._get_time_notes(item),
            location=item["location"],
            links=[{
                "href": doc["url"],
                "title": doc["note"]
            } for doc in item["documents"]],
            source=item["sources"][0]["url"],
        )
        # Bypass __setitem__ to add uid to Meeting object if present
        if item.get("uid"):
            meeting._values["uid"] = item["uid"]
        return meeting

    def _get_status(self, status):
        if status == "canceled":
            return "cancelled"
        return status

    def _get_datetime(self, dt_dict, is_end=False):
        date_obj = dt_dict["date"]
        time_obj = dt_dict["time"]
        if not date_obj or (is_end and not time_obj):
            return
        if not time_obj:
            time_obj = time(0)
        return datetime.combine(dt_dict["date"], time_obj)

    def _get_time_notes(self, item):
        return " ".join([
            dt_dict.get("note", "")
            for dt_dict in [item.get("start", {}), item.get("end", {})]
        ]).strip()
