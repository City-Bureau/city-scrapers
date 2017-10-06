import json
import os

from datetime import datetime
from invoke import task
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

PROJECT_SLUG = 'documenters_aggregator'
DEPLOY_TAG = datetime.now().strftime("%Y%m%d%H%M")
ECS_URI = os.environ.get('ECS_REPOSITORY_URI')

crawler_process = CrawlerProcess(get_project_settings())
spider_classes = [crawler_process.spider_loader.load(spidername) for spidername in crawler_process.spider_loader.list()]


@task
def create_logs(ctx):
    """Create log groups for each scraper."""
    for cls in spider_classes:
        ctx.run('aws logs create-log-group --log-group-name "{0}-{1}"'.format(PROJECT_SLUG, cls.name), warn=True)


@task
def delete_logs(ctx):
    """Remove log groups."""
    for cls in spider_classes:
        ctx.run('aws logs delete-log-group --log-group-name "{0}-{1}"'.format(PROJECT_SLUG, cls.name))


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


@task(login)
def register_task_definitions(ctx):
    for cls in spider_classes:
        definitions = get_definitions(cls.name)
        ctx.run('aws ecs register-task-definition --family {0}-{1} --network-mode host --container-definitions "{2}"'.format(PROJECT_SLUG, cls.name, definitions))


@task(login)
def enable_rules(ctx):
    # @TODO this offset mechanism is mega-dumb
    cron_offset = 0
    for i, cls in enumerate(spider_classes):
        rule_definition = get_event_rule_definition(cls, cron_offset=cron_offset)
        ctx.run('aws events put-rule --cli-input-json "{0}"'.format(rule_definition))
        if i % 2:
            cron_offset += 1

        target_definition = {
            "Rule": "documenters_aggregator-{0}".format(cls.name),
            "Targets": [
                {
                    "Input": "{}",
                    "RoleArn": "arn:aws:iam::647111127395:role/ecsEventsRole",
                    "EcsParameters": {
                        "TaskDefinitionArn": "arn:aws:ecs:us-east-1:647111127395:task-definition/documenters_aggregator-{0}".format(cls.name),  # @TODO hardcoded :/
                        "TaskCount": 1
                    },
                    "Id": "documenters_aggregator-rta",
                    "Arn": "arn:aws:ecs:us-east-1:647111127395:cluster/documenters-aggregator"  # @TODO hardcoded :/
                }
            ]
        }

        ctx.run('aws events put-targets --cli-input-json "{0}"'.format(quote_for_awscli(target_definition)))


@task(login)
def disable_rules(ctx):
    for cls in spider_classes:
        rule_definition = get_event_rule_definition(cls, state="DISABLED")
        ctx.run('aws events put-rule --cli-input-json "{0}"'.format(rule_definition))


@task(build, push, create_logs, register_task_definitions, enable_rules)
def deploy(ctx):
    """Build, tag, push, and deploy to Elastic Container Service."""
    print("Deployed.")


def get_event_rule_definition(cls, state="ENABLED", cron_offset=0):
    # @TODO this offset mechanism is mega-dumb
    hours = [str(0 + cron_offset), str(12 + cron_offset)]
    rule_definition = {
        "State": state,
        "ScheduleExpression": "cron(0 {0} ? * * *)".format(','.join(hours)),
        "Name": "documenters_aggregator-{0}".format(cls.name),
        "Description": "{0} scraper".format(cls.long_name),
        "RoleArn": "arn:aws:iam::647111127395:role/ecsEventsRole",  # @TODO hardcoded :/
    }
    return quote_for_awscli(rule_definition)


def get_definitions(classname):
    env = get_env()
    definition = {
        'environment': [{'name': k, 'value': v} for k, v in env.items()],
        'name': PROJECT_SLUG,
        'image': '{0}:{1}-{2}'.format(ECS_URI, PROJECT_SLUG, DEPLOY_TAG),
        'command': ["sh", "-c", 'scrapy crawl {0}'.format(classname)],
        'workingDirectory': '/usr/src/app',
        'memory': 512,
        'memoryReservation': 256,
        'essential': True,
        'logConfiguration': {
            'logDriver': 'awslogs',
            'options': {
                'awslogs-group': '{0}-{1}'.format(PROJECT_SLUG, classname),
                'awslogs-region': os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'),
            }
        }
    }
    return quote_for_awscli([definition])


def quote_for_awscli(data):
    jsonstring = json.dumps(data)
    # The following is an ugly but functional way of getting right quoting that aws cli wants.
    return jsonstring.replace("\"", r"\"")


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
# [ ] Create ecs service
# [ ] Delete ecs service
# (ecs services seem hard, for now might leave up to user)

# [✔️] Docker build

# [✔️] Create cloudfront log groups
# [✔️] Delete cloudfront log groups

# [✔️] Create ecs task definitions
# [ ] Delete ecs task definition (you basically can't, and that's basically ok!)

# [✔️] Create scheduled tasks (may need to create lambda fn?)
# [✔️] Delete scheduled tasks (may need to delete lamba fn?)

# [ ] Create email on error alert
# [ ] Delete email on error alert
