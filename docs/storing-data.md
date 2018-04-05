# Storing data

Scrapy, the Documenters Event Aggregator's scraping library, has a feature they call "pipelines". Pipelines act on each parsed data item returned by every spider. Pipeline configuration is handled in `spiders/settings.py`. It's a good way to do things like upsert items into a database or have some other side effect.

The Documenters Event Aggregator currently implements an Airtable pipeline. Airtable is useful for exploring possible uses and integrations of the data, with the caveat that it isn't as robust or smooth as databases like Postgres/PostGIS and MongoDB. An SQLAlchemy/ORM pipeline is planned and [could use your help](https://github.com/City-Bureau/city-scrapers/issues/2)!

## Airtable

_There is currently no easy way to copy an Airtable schema, so this is of mostly academic interest until we solve [#122](https://github.com/City-Bureau/city-scrapers/issues/122)._

Check out the [deployment guide](deployment.md). You'll need to set credentials in `deploy/prod.sh` for Airtable.

View or generate your Airtable API key at [https://airtable.com/account](https://airtable.com/account).

Click your database at [https://airtable.com/api](https://airtable.com/api) to get your `BASE_KEY` (which will be tacked on to the URL).

Now edit `deploy/prod.sh` or your configuration file:

```bash
# ...
## Airtable API key (generate/view at https://airtable.com/account)
export AIRTABLE_API_KEY='<YOURAIRTABLE_API_KEY>'

## Airtable database/table identifiers (click your database at https://airtable.com/api)
export DOCUMENTERS_AGGREGATOR_AIRTABLE_BASE_KEY='<YOUR BASE KEY>'
export DOCUMENTERS_AGGREGATOR_AIRTABLE_DATA_TABLE='Events'
```

## SQLAlchemy

Not implemented. [Consider contributing](https://github.com/City-Bureau/city-scrapers/issues/2).
