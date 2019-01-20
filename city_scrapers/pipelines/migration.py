from datetime import datetime, time

from city_scrapers_core.items import Meeting


class MigrationPipeline:
    """Migrates to city_scrapers_core Meeting object instead of dictionaries"""
    def process_item(self, item, spider):
        return Meeting(
            id=item["id"],
            title=item["name"],
            description=item["event_description"],
            classification=item["classification"],
            status=self._get_status(item["status"]),
            start=self._get_datetime(item["start"]),
            end=self._get_datetime(item["end"]),
            all_day=item["all_day"],
            time_notes=self._get_time_notes(item),
            location=item["location"],
            links=[{"href": doc["url"], "title": doc["note"]} for doc in item["documents"]],
            source=item["sources"][0]["url"],
        )

    def _get_status(self, status):
        if status == "canceled":
            return "cancelled"
        return status

    def _get_datetime(self, dt_dict):
        date_obj = dt_dict["date"]
        time_obj = dt_dict["time"]
        if not date_obj:
            return
        if not time_obj:
            time_obj = time(0)
        return datetime.combine(dt_dict["date"], time_obj)

    def _get_time_notes(self, item):
        return " ".join(
            [dt_dict.get("note", "") for dt_dict in [item["start"], item["end"]]]
        ).strip()
