---
title: Deployment
---

<h1 class="hidden">Deployment</h1>

We are using Amazon Elastic Container Service (ECS) to run this project in production. Each of the spiders has its own:

* TaskDefinition in ECS
* LogGroup in CloudWatch

There is also a Lambda script that runs every hour and kicks off the next scraper by running its Task in ECS.

## How Deployment Works

The [GitHub repo](https://github.com/City-Bureau/city-scrapers) is connected to AWS CodeBuild. When code is pushed to the master branch on GitHub, CodeBuild fetches the latest code and runs a build as defined in `buildspec.yml`. This file defines a workflow that:
  1. Builds a Docker image using `deploy/Dockerfile`
  2. Tags the new image with `latest` (Note that this is the tag that all of the ECS Task Definitions will use).
  3. Checks that the tests pass by running `invoke runtests` in the new image
  4. Pushes the Docker image to our ECS Repository
  5. Runs the script `deploy/setup_aws.py`, which creates the task definitions in ECS, sets up log groups in CloudWatch, etc. for all existing spiders.

The bottom line is this: when everything works, pushing to master will deploy code to production as long as the build passes. If the tests don't pass in step #3, the build is aborted.

## Configuration

The above requires that all ENV variables defined in `deploy/prod_settings.py` are configured in the CodeBuild project. Once this is setup, anyone who can push to master on GitHub can deploy, without needing to have access to these credentials directly.
