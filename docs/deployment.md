# Deployment

Documenters Aggregator is designed to be Dockerized and run on Amazon EC2 Container Service. It comes with a simple system for swapping out configurations.

## Using sample "prod" configuration

* Copy `deploy/prod.sh.example` to `deploy/prod.sh`
* Copy `deploy/prod_settings.py.example` to `deploy/prod_settings.py`

Now run:

```bash
env deploy/prod.sh
```

Modify `deploy/prod_settings.py` to tweak Scrapy to use specific configuration variables tuned to whatever environment you're running it in.

Set secrets and credentials in `deploy/prod.sh`.

Any files ending in `.py` or `.sh` in the `deploy` directory will be ignored.

## Creating your own targets

Simply copy and modify `deploy/prod.sh` and, if you want, `deploy/prod_settings.py`, e.g. `deploy/stage.sh` and `deploy/stage_settings.py`. Don't forget to update the `SCRAPY_SETTINGS_MODULE` environment variable in `deploy/stage.sh` to reflect the correct settings.
