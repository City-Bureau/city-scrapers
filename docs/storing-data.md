# Storing data

Scrapy, the Documenters Event Aggregator's scraping library, has a feature they call "pipelines". Pipelines act on each parsed data item returned by every spider. Pipeline configuration is handled in `spiders/settings.py`. It's a good way to do things like upsert items into a database or have some other side effect.

The Documenters Event Aggregator currently implements an Airtable pipeline. Airtable is useful for exploring possible uses and integrations of the data, with the caveat that it isn't as robust or smooth as databases like Postgres/PostGIS and MongoDB. An SQLAlchemy/ORM pipeline is planned and [could use your help](https://github.com/City-Bureau/documenters-aggregator/issues/2)!

## Airtable



## SQLAlchemy

Not implemented. [Consider contributing](https://github.com/City-Bureau/documenters-aggregator/issues/2).
