import os
import json
import boto3
from os import listdir, environ, path
from os.path import isfile, join
from zipfile import ZipFile

DEPLOY_TAG = 'latest'  # datetime.now().strftime("%Y%m%d%H%M")
ECS_URI = environ.get('ECS_REPOSITORY_URI')
BATCH_JOB_ROLE = 'city-scrapers-batch-job-role'

SPIDER_PATH = join(
    path.dirname(path.dirname(path.abspath(__file__))),
    'city_scrapers',
    'spiders'
)

ENV_VARS = [
    'SCRAPY_SETTINGS_MODULE',
    'AIRTABLE_API_KEY',
    'CITY_SCRAPERS_AIRTABLE_BASE_KEY',
    'CITY_SCRAPERS_AIRTABLE_DATA_TABLE',
    'CITY_SCRAPERS_AIRTABLE_GEOCODE_TABLE',
    'CITY_SCRAPERS_GOOGLE_API_KEY',
    'SENTRY_DSN',
    'MAPZEN_API_KEY'
]

batch = boto3.client('batch')
iam = boto3.resource('iam')
lambda_client = boto3.client('lambda')

spider_names = [
    path.splitext(f)[0]
    for f in listdir(SPIDER_PATH)
    if isfile(join(SPIDER_PATH, f)) and f != '__init__.py'
]


def create_job_definitions():
    """
    Register all job definitions.
    """
    job_def_res = batch.describe_job_definitions(status='ACTIVE')
    job_defs = job_def_res['jobDefinitions']
    while 'nextToken' in job_def_res:
        job_def_res = batch.describe_job_definitions(
            status='ACTIVE',
            nextToken=job_def_res['nextToken'],
        )
        job_defs.extend(job_def_res['jobDefinitions'])

    active_job_arns = set([job['jobDefinitionArn'] for job in job_defs])
    print('deregistering all current job definitions')
    for job_arn in active_job_arns:
        batch.deregister_job_definition(jobDefinition=job_arn)

    future_job_defs = spider_names
    job_role_arn = iam.Role(BATCH_JOB_ROLE).arn

    for job_def in future_job_defs:
        print('creating job def {}'.format(job_def))
        batch.register_job_definition(
            jobDefinitionName=job_def,
            type='container',
            containerProperties={
                'image': '{0}:{1}'.format(ECS_URI, DEPLOY_TAG),
                'vcpus': 1,
                'memory': 768,
                'command': ['scrapy', 'crawl', job_def],
                'jobRoleArn': job_role_arn,
                'environment': [{'name': v, 'value': environ.get(v)} for v in ENV_VARS],
                'readonlyRootFilesystem': False,
                'privileged': False,
            },
            retryStrategy={'attempts': 3}
        )


def update_lambda_function(name):
    with ZipFile('{}.zip'.format(name), 'w') as zf:
        for f in listdir(join(path.dirname(__file__), name)):
            zf.write(join(path.dirname(__file__), name, f), path.basename(f))

    with open('{}.zip'.format(name), 'rb') as zf:
        zip_buffer = zf.read()

    os.remove('{}.zip'.format(name))
    lambda_client.update_function_code(FunctionName=name, ZipFile=zip_buffer)


create_job_definitions()
update_lambda_function('city-scrapers-status')
