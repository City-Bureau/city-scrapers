import json
from datetime import datetime
from tests.utils import read_test_file_content, test_geocode_item
<<<<<<< HEAD:tests/test_pipeline_geocoder.py
=======
from city_scrapers.pipelines.localExporter import CsvPipeline
>>>>>>> 15e0505f352da00c2a7efbfe2782807db8c80654:tests/test_geocode_pipeline.py
from city_scrapers.spiders.chi_buildings import Chi_buildingsSpider
from city_scrapers.pipelines.mapbox import MapboxPipeline

pipeline = MapboxPipeline()
testSpider = Chi_buildingsSpider()

def test_valid_geocode_item():
    fixture = test_geocode_item()
    processed = pipeline.process_item(fixture, testSpider)
    print(processed)
