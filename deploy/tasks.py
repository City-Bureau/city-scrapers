import json
import os

from datetime import datetime
from invoke import task

PROJECT_SLUG = 'documenters_aggregator'
DEPLOY_TAG = datetime.now().strftime("%Y%m%d%H%M")
ECS_URI = os.environ.get('ECS_REPOSITORY_URI')


@task
def build(ctx):
    """Build Docker container."""
    ctx.run('docker build --pull -f deploy/Dockerfile -t {0} .'.format(PROJECT_SLUG))


@task
def run(ctx):
    """Run Docker container."""
    env = get_env()
    env_args = ' '.join(['-e {0}={1}'.format(k, v) for k, v in env.items()])
    ctx.run('docker run {1}'.format(env_args, PROJECT_SLUG))


@task
def login(ctx):
    """Get AWS ECR access token."""
    ctx.run('$(aws ecr get-login --no-include-email)')


@task(login)
def tag(ctx):
    """Tag Docker container."""
    print('tagging {0}-{1}'.format(PROJECT_SLUG, DEPLOY_TAG))
    ctx.run('docker tag {0}:latest {1}:{0}-{2}'.format(PROJECT_SLUG, ECS_URI, DEPLOY_TAG))


@task(login, tag)
def push(ctx):
    """Push Docker container to Elastic Container Repository."""
    print('docker push {0}:{1}-{2}'.format(ECS_URI, PROJECT_SLUG, DEPLOY_TAG))
    with ctx.cd('deploy'):
        ctx.run('docker push {0}:{1}-{2}'.format(ECS_URI, PROJECT_SLUG, DEPLOY_TAG))


@task(build, push)
def deploy(ctx):
    """Build, tag, push, and deploy to Elastic Container Service."""
    definitions = get_definitions()
    ctx.run('aws ecs register-task-definition --family {0} --network-mode host --container-definitions "{1}"'.format(PROJECT_SLUG, definitions))


def get_definitions():
    env = get_env()
    definition = {
        'environment': [{'name': k, 'value': v} for k, v in env.items()],
        'name': PROJECT_SLUG,
        'image': '{0}:{1}-{2}'.format(ECS_URI, PROJECT_SLUG, DEPLOY_TAG),
        'memory': 512,
        'memoryReservation': 256,
        'essential': True,
        'logConfiguration': {
            'logDriver': 'awslogs',
            'options': {
                'awslogs-group': PROJECT_SLUG,
                'awslogs-region': os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'),
            }
        }
    }
    definition_string = json.dumps([definition])
    # The following is an ugly but functional way of getting right quoting that aws cli wants.
    return definition_string.replace("\"", r"\"")


def get_env():
    """
    Read in environment variables
    @TODO better handled with dotenv?
    """
    return {
        'SCRAPY_SETTINGS_MODULE': os.environ.get('SCRAPY_SETTINGS_MODULE'),
        'AIRTABLE_API_KEY': os.environ.get('AIRTABLE_API_KEY'),
        'DOCUMENTERS_AGGREGATOR_AIRTABLE_BASE_KEY': os.environ.get('DOCUMENTERS_AGGREGATOR_AIRTABLE_BASE_KEY'),
        'DOCUMENTERS_AGGREGATOR_AIRTABLE_DATA_TABLE': os.environ.get('DOCUMENTERS_AGGREGATOR_AIRTABLE_DATA_TABLE')
    }


# @TODO
# Create cloudfront log group
# Create ecs service?
