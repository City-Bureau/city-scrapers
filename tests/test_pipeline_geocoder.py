import json
from datetime import datetime
from tests.utils import read_test_file_content, test_geocode_item
from city_scrapers.pipelines.localExporter import CsvPipeline
from city_scrapers.spiders.chi_buildings import Chi_buildingsSpider
from city_scrapers.pipelines.mapbox import MapboxPipeline

pipeline = MapboxPipeline()
testSpider = Chi_buildingsSpider()

def test_valid_geocode_item():
    fixture = test_geocode_item()
    processed = pipeline.process_item(fixture, testSpider)
    print(processed)
