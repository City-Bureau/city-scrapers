from .airtable import AirtablePipeline
from .geocoder import GeocoderPipeline
from .mapbox import MapboxPipeline
from .LoggingPipeline import CityScrapersLoggingPipeline
from .sqlalchemy import CityScrapersSQLAlchemyPipeline
from .ValidationPipeline import ValidationPipeline
from .TravisValidation import TravisValidationPipeline
from .localExporter import CsvPipeline
<<<<<<< HEAD
from .feedWriter import JsonWriterPipeline
from .addressCoderPipeline import AddressPipeline
=======
from .item import CityScrapersItemPipeline

>>>>>>> upstream/master

__all__ = (
    'CityScrapersLoggingPipeline',
    'AirtablePipeline',
    'GeocoderPipeline',
    'CityScrapersSQLAlchemyPipeline',
    'ValidationPipeline',
    'TravisValidationPipeline',
<<<<<<< HEAD
    'MapboxPipeline',
    'CsvPipeline',
    'JsonWriterPipeline',
    'AddressPipeline',
=======
    'CsvPipeline',
    'CityScrapersItemPipeline'
>>>>>>> upstream/master
)
