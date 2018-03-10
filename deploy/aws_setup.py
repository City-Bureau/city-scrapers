import json
from subprocess import check_output
from os import listdir, environ, path
from os.path import isfile, join

PROJECT_SLUG = 'documenters_aggregator'
DEPLOY_TAG = 'latest'  # datetime.now().strftime("%Y%m%d%H%M")
ECS_URI = environ.get('ECS_REPOSITORY_URI')

SPIDER_PATH = 'documenters_aggregator/spiders'

spider_names = [
    path.splitext(f)[0]
    for f in listdir(SPIDER_PATH)
    if isfile(join(SPIDER_PATH, f)) and f != '__init__.py'
]


def run(command):
    return check_output([command], shell=True)


def json_run(command):
    output = run(command)
    return json.loads(output)


def get_env():
    """
    Read in environment variables
    """
    vars_to_import = [
        'SCRAPY_SETTINGS_MODULE',
        'AIRTABLE_API_KEY',
        'DOCUMENTERS_AGGREGATOR_AIRTABLE_BASE_KEY',
        'DOCUMENTERS_AGGREGATOR_AIRTABLE_DATA_TABLE',
        'DOCUMENTERS_AGGREGATOR_AIRTABLE_GEOCODE_TABLE',
        'SENTRY_DSN',
        'MAPZEN_API_KEY'
    ]
    return {key: environ.get(key) for key in vars_to_import}


def create_log_groups():
    """Create log groups for each scraper."""

    existing_log_groups = [
        data['logGroupName']
        for data
        in json_run('aws logs describe-log-groups')['logGroups']
    ]

    future_log_groups = [
        '{0}-{1}'.format(PROJECT_SLUG, name) for name in spider_names
    ]

    for log_group_name in future_log_groups:
        if log_group_name in existing_log_groups:
            print('log group {0} exists'.format(log_group_name))
        else:
            print('creating log group {0}'.format(log_group_name))
            run('aws logs create-log-group --log-group-name "{0}"'.format(log_group_name))


def create_task_definitions():
    """
    Register all task definitions.
    """

    existing_task_families = [
        family_name
        for family_name
        in json_run('aws ecs list-task-definition-families --status ACTIVE')['families']
    ]

    future_task_families = [
        '{0}-{1}'.format(PROJECT_SLUG, name) for name in spider_names
    ]

    for family_name in future_task_families:
        if family_name in existing_task_families:
            print('task family {0} exists'.format(family_name))
        else:
            print('creating task definition family {0}'.format(family_name))
            definitions = get_definitions(family_name)
            run('aws ecs register-task-definition --family {0} --network-mode host --container-definitions "{1}"'.format(family_name, definitions))

    for family_name in existing_task_families:
        if family_name not in future_task_families:
            print('deregistering task definitions for unused task family {0}'.format(family_name))
            existing_defs = json_run('aws ecs list-task-definitions --family {0}'.format(family_name))
            for arn in existing_defs['taskDefinitionArns']:
                run('aws ecs deregister-task-definition --task-definition {0}'.format(arn))


def get_definitions(family_name):
    env = get_env()
    name = family_name.replace(PROJECT_SLUG + '-', '')
    definition = {
        'environment': [{'name': k, 'value': v} for k, v in env.items()],
        'name': PROJECT_SLUG,
        'image': '{0}:{1}'.format(ECS_URI, DEPLOY_TAG),
        'command': ["sh", "-c", 'scrapy crawl {0}'.format(name)],
        'workingDirectory': '/usr/src/app',
        'memory': 512,
        'memoryReservation': 256,
        'essential': True,
        'logConfiguration': {
            'logDriver': 'awslogs',
            'options': {
                'awslogs-group': family_name,
                'awslogs-region': environ.get('AWS_DEFAULT_REGION', 'us-east-1'),
            }
        }
    }
    return quote_for_awscli([definition])


def update_lambda_function():
    with open("deploy/scraperScheduler/spiders.txt", "w") as file:
        file.write("\n".join(spider_names))

    run('zip -X -j -r code.zip deploy/scraperScheduler/*')
    run('aws lambda update-function-code --function-name scraperScheduler --zip-file fileb://code.zip')
    run('rm code.zip')
    run('rm deploy/scraperScheduler/spiders.txt')


def quote_for_awscli(data):
    # The following is an ugly but functional way of creating the quoting
    # that the aws cli wants.
    jsonstring = json.dumps(data)
    return jsonstring.replace("\"", r"\"")


create_log_groups()
create_task_definitions()
update_lambda_function()
