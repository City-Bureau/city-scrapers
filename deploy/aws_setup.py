import os
import json
import boto3
from os import listdir, environ, path
from os.path import isfile, join
from zipfile import ZipFile

DEPLOY_TAG = 'latest'  # datetime.now().strftime("%Y%m%d%H%M")
ECS_URI = environ.get('ECS_REPOSITORY_URI')
BATCH_JOB_ROLE = 'city-scrapers-batch-job-role'
SPIDER_PATH = 'documenters_aggregator/spiders'

ENV_VARS = [
    'SCRAPY_SETTINGS_MODULE',
    'AIRTABLE_API_KEY',
    'DOCUMENTERS_AGGREGATOR_AIRTABLE_BASE_KEY',
    'DOCUMENTERS_AGGREGATOR_AIRTABLE_DATA_TABLE',
    'DOCUMENTERS_AGGREGATOR_AIRTABLE_GEOCODE_TABLE',
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
    active_job_defs = batch.describe_job_definitions(status='ACTIVE')['jobDefinitions']
    active_job_def_names = set([j['jobDefinitionName'] for j in active_job_defs])

    future_job_defs = spider_names
    env_vars = [{'name': v, 'value': environ.get(v)} for v in ENV_VARS]
    job_role_arn = iam.Role(BATCH_JOB_ROLE).arn

    for job_def in future_job_defs:
        if job_def in active_job_def_names:
            print('job def {} exists'.format(job_def))
        else:
            print('creating job def {}'.format(job_def))
            batch.register_job_definition(
                jobDefinitionName=job_def,
                type='container',
                containerProperties={
                    'image': '{0}:{1}'.format(ECS_URI, DEPLOY_TAG),
                    'vcpus': 1,
                    'memory': 768,
                    'command': ['sh', '-c', 'scrapy crawl {}'.format(job_def)],
                    'jobRoleArn': job_role_arn,
                    'environment': [{'name': v, 'value': environ.get(v)} for v in ENV_VARS],
                    'readonlyRootFilesystem': False,
                    'privileged': False,
                },
                retryStrategy={'attempts': 3}
            )

    for job_def in active_job_def_names:
        if job_def not in future_job_defs:
            print('deregistering job definitions for unused job {}'.format(job_def))
            remove_arns = [j['jobDefinitionArn'] for j in active_job_defs if j['jobDefinitionName'] == job_def]
            for arn in remove_arns:
                batch.deregister_job_definition(jobDefinition=arn)


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
